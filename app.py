import os
import json as _json
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, session, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect

from config import Config
from models import db, Admin, Category, Product, PriceOption, Layout, Order, SiteSetting
from forms import (OrderForm, LoginForm, CategoryForm, ProductForm,
                   PriceOptionForm, LayoutForm, SettingsForm)
from mail import send_order_email
from telegram import send_order_telegram
from security import (
    apply_security_headers,
    safe_save_upload,
    truncate_str,
    rate_limit,
    layout_belongs_to_product,
    price_option_belongs_to_product,
)

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
csrf = CSRFProtect(app)


@app.after_request
def security_headers(response):
    return apply_security_headers(response)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'
login_manager.login_message = 'Войдите для доступа к админ-панели'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Admin, int(user_id))


@app.errorhandler(429)
def rate_limit_exceeded(e):
    return render_template('429.html'), 429


@app.context_processor
def inject_settings():
    def get_setting(key, default=''):
        return SiteSetting.get(key, default)
    categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
    return dict(
        get_setting=get_setting,
        nav_categories=categories,
        current_year=datetime.utcnow().year
    )


@app.route('/')
def index():
    categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
    return render_template('index.html', categories=categories)


@app.route('/catalog')
def catalog_all():
    categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
    products = Product.query.filter_by(is_active=True).order_by(Product.sort_order).all()
    return render_template('catalog_all.html', categories=categories, products=products)


@app.route('/catalog/<slug>')
def catalog(slug):
    category = Category.query.filter_by(slug=slug, is_active=True).first_or_404()
    products = Product.query.filter_by(category_id=category.id, is_active=True)\
        .order_by(Product.sort_order).all()
    return render_template('catalog.html', category=category, products=products)


@app.route('/order', methods=['GET', 'POST'])
@rate_limit('order', 10)
def order():
    form = OrderForm()
    if form.validate_on_submit():
        file_path = safe_save_upload(
            form.file.data,
            app.config['UPLOAD_FOLDER'],
            app.config['UPLOAD_ALLOWED_EXTENSIONS'],
        ) or ''

        new_order = Order(
            name=form.name.data,
            phone=form.phone.data,
            email=form.email.data or '',
            order_type=form.order_type.data or '',
            osnastka=form.osnastka.data or '',
            message=form.message.data or '',
            file_path=file_path,
            status='new'
        )
        db.session.add(new_order)
        db.session.commit()

        try:
            send_order_email(new_order)
        except Exception as e:
            app.logger.error(f'Failed to send email for order #{new_order.id}: {e}')

        try:
            send_order_telegram(new_order)
        except Exception as e:
            app.logger.error(f'Failed to send Telegram for order #{new_order.id}: {e}')

        flash('Ваш заказ успешно отправлен! Мы свяжемся с вами в ближайшее время.', 'success')
        return redirect(url_for('order_success'))

    return render_template('order.html', form=form)


@app.route('/order/product/<int:product_id>', methods=['GET', 'POST'])
@rate_limit('order_product', 15)
def order_product(product_id):
    product = Product.query.get_or_404(product_id)
    step = request.args.get('step', '1')
    layouts = Layout.query.filter_by(product_id=product.id).order_by(Layout.sort_order).all()
    price_options = PriceOption.query.filter_by(product_id=product.id).order_by(PriceOption.sort_order).all()
    session_key = f'order_product_{product_id}'
    allowed_ext = app.config['UPLOAD_ALLOWED_EXTENSIONS']
    max_msg = app.config['MAX_FIELD_MESSAGE']
    max_name = app.config['MAX_FIELD_NAME']
    max_phone = app.config['MAX_FIELD_PHONE']
    max_email = app.config['MAX_FIELD_EMAIL']
    max_addr = app.config['MAX_FIELD_ADDRESS']
    max_params_len = app.config['MAX_PARAMS_JSON_LENGTH']

    skip_layout_osnastka = product.category.slug in ('faksimile', 'ottisk')
    skip_layout = not layouts

    if request.method == 'POST':
        if step == '1':
            params = {k.replace('param_', ''): truncate_str(v, 500) for k, v in request.form.items()
                      if k.startswith('param_') and v}
            params['message'] = truncate_str(request.form.get('message', ''), 2000)
            file_path = safe_save_upload(
                request.files.get('file_step1'),
                app.config['UPLOAD_FOLDER'],
                allowed_ext,
            ) or ''
            session[session_key] = {'params': params, 'file_path': file_path}
            if skip_layout_osnastka:
                step_data = {'layout_id': str(layouts[0].id) if layouts else '', 'params': params, 'file_path': file_path}
                session[session_key] = step_data
                return redirect(url_for('order_product', product_id=product_id, step=3, layout_id=step_data.get('layout_id') or ''))
            if not layouts:
                session[session_key] = {'params': params, 'file_path': file_path}
                return redirect(url_for('order_product', product_id=product_id, step=3))
            return redirect(url_for('order_product', product_id=product_id, step=2))
        elif step == '2':
            step_data = session.get(session_key, {})
            raw_layout = request.form.get('layout_id') or (str(layouts[0].id) if layouts else '')
            if layout_belongs_to_product(raw_layout, product.id, layouts):
                step_data['layout_id'] = raw_layout
            else:
                step_data['layout_id'] = str(layouts[0].id) if layouts else ''
            session[session_key] = step_data
            return redirect(url_for('order_product', product_id=product_id, step=3, layout_id=step_data['layout_id']))
        elif step == '3':
            step_data = session.pop(session_key, {})
            layout_id = request.form.get('layout_id') or step_data.get('layout_id')
            if layout_id and not layout_belongs_to_product(layout_id, product.id, layouts):
                layout_id = str(layouts[0].id) if layouts else None
            price_option_id = request.form.get('price_option_id')
            if skip_layout_osnastka and not price_option_id and price_options:
                price_option_id = str(price_options[0].id)
            if price_option_id and not price_option_belongs_to_product(price_option_id, product.id, price_options):
                price_option_id = str(price_options[0].id) if price_options else None

            name = truncate_str(request.form.get('name'), max_name)
            phone = truncate_str(request.form.get('phone'), max_phone)
            email = truncate_str(request.form.get('email', ''), max_email)
            message = truncate_str(
                request.form.get('message', '') or step_data.get('params', {}).get('message', ''),
                max_msg,
            )
            delivery_datetime = truncate_str(request.form.get('delivery_datetime', ''), 200)
            delivery_address = truncate_str(request.form.get('delivery_address', ''), max_addr)

            if not name or not phone:
                flash('Укажите имя и телефон.', 'error')
                session[session_key] = step_data
                return redirect(url_for('order_product', product_id=product_id, step=3))

            layout_obj = Layout.query.get(int(layout_id)) if layout_id and str(layout_id).isdigit() else None
            po = PriceOption.query.get(int(price_option_id)) if price_option_id and str(price_option_id).isdigit() else None
            layout_price = 0 if (skip_layout_osnastka or not layouts) else (layout_obj.price if layout_obj else 750)
            po_price = po.price_normal if po else 0
            needs_delivery = request.form.get('needs_delivery') == 'on'
            delivery_fee = 500 if needs_delivery else 0
            total = layout_price + po_price + delivery_fee

            file_path = step_data.get('file_path', '')
            file_path_step3 = safe_save_upload(
                request.files.get('file'),
                app.config['UPLOAD_FOLDER'],
                allowed_ext,
            ) or ''

            params_raw = step_data.get('params', {})
            params_json = _json.dumps(params_raw, ensure_ascii=False)
            if len(params_json) > max_params_len:
                params_json = _json.dumps({}, ensure_ascii=False)

            new_order = Order(
                product_id=product.id,
                layout_id=None if skip_layout_osnastka else (int(layout_id) if layout_id else None),
                price_option_id=int(price_option_id) if price_option_id else None,
                total_price=total,
                name=name,
                phone=phone,
                email=email,
                message=message,
                file_path=file_path,
                file_path_step3=file_path_step3,
                params_json=params_json,
                status='new',
                needs_delivery=needs_delivery,
                delivery_datetime=delivery_datetime,
                delivery_address=delivery_address,
            )
            db.session.add(new_order)
            db.session.commit()

            try:
                send_order_email(new_order)
            except Exception as e:
                app.logger.error(f'Failed to send email for order #{new_order.id}: {e}')

            try:
                send_order_telegram(new_order)
            except Exception as e:
                app.logger.error(f'Failed to send Telegram for order #{new_order.id}: {e}')

            flash('Ваш заказ успешно отправлен! Мы свяжемся с вами в ближайшее время.', 'success')
            return redirect(url_for('order_success'))

    layout_id = request.args.get('layout_id')
    selected_layout = Layout.query.get(layout_id) if layout_id else (layouts[0] if layouts else None)

    return render_template('order_product.html',
                           product=product,
                           step=int(step) if step.isdigit() else 1,
                           layouts=layouts,
                           price_options=price_options,
                           selected_layout=selected_layout,
                           layout_id=layout_id,
                           skip_layout=not layouts,
                           skip_layout_osnastka=skip_layout_osnastka)


@app.route('/order/success')
def order_success():
    return render_template('order_success.html')


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


@app.route('/delivery')
def delivery():
    return render_template('delivery.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/policy')
def policy():
    return render_template('policy.html')


@app.route('/admin/login', methods=['GET', 'POST'])
@rate_limit('admin_login', 5)
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Admin.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        flash('Неверный логин или пароль', 'error')
    return render_template('admin/login.html', form=form)


@app.route('/admin/logout', methods=['POST'])
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/admin')
@login_required
def admin_dashboard():
    orders_count = Order.query.count()
    new_orders = Order.query.filter_by(status='new').count()
    products_count = Product.query.count()
    categories_count = Category.query.count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html',
                           orders_count=orders_count,
                           new_orders=new_orders,
                           products_count=products_count,
                           categories_count=categories_count,
                           recent_orders=recent_orders)


@app.route('/admin/categories')
@login_required
def admin_categories():
    categories = Category.query.order_by(Category.sort_order).all()
    return render_template('admin/categories.html', categories=categories)


@app.route('/admin/categories/add', methods=['GET', 'POST'])
@login_required
def admin_category_add():
    form = CategoryForm()
    if form.validate_on_submit():
        image_path = safe_save_upload(
            form.image.data,
            app.config['UPLOAD_FOLDER'],
            {'jpg', 'jpeg', 'png', 'gif'},
        ) or ''
        cat = Category(
            name=form.name.data,
            slug=form.slug.data,
            description=form.description.data or '',
            icon=form.icon.data or '',
            image=image_path,
            sort_order=form.sort_order.data or 0,
            is_active=form.is_active.data
        )
        db.session.add(cat)
        db.session.commit()
        flash('Категория добавлена', 'success')
        return redirect(url_for('admin_categories'))
    return render_template('admin/category_form.html', form=form, title='Добавить категорию')


@app.route('/admin/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_category_edit(id):
    cat = db.session.get(Category, id) or abort(404)
    form = CategoryForm(obj=cat)
    if form.validate_on_submit():
        up = safe_save_upload(
            form.image.data,
            app.config['UPLOAD_FOLDER'],
            {'jpg', 'jpeg', 'png', 'gif'},
        )
        if up:
            cat.image = up
        cat.name = form.name.data
        cat.slug = form.slug.data
        cat.description = form.description.data or ''
        cat.icon = form.icon.data or ''
        cat.sort_order = form.sort_order.data or 0
        cat.is_active = form.is_active.data
        db.session.commit()
        flash('Категория обновлена', 'success')
        return redirect(url_for('admin_categories'))
    return render_template('admin/category_form.html', form=form, title='Редактировать категорию', category=cat)


@app.route('/admin/categories/<int:id>/delete', methods=['POST'])
@login_required
def admin_category_delete(id):
    cat = db.session.get(Category, id) or abort(404)
    db.session.delete(cat)
    db.session.commit()
    flash('Категория удалена', 'success')
    return redirect(url_for('admin_categories'))


@app.route('/admin/products')
@login_required
def admin_products():
    products = Product.query.order_by(Product.sort_order).all()
    return render_template('admin/products.html', products=products)


@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def admin_product_add():
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name) for c in
                                 Category.query.order_by(Category.sort_order).all()]
    if form.validate_on_submit():
        image_path = safe_save_upload(
            form.image.data,
            app.config['UPLOAD_FOLDER'],
            {'jpg', 'jpeg', 'png', 'gif'},
        ) or ''
        prod = Product(
            category_id=form.category_id.data,
            name=form.name.data,
            description=form.description.data or '',
            image=image_path,
            sort_order=form.sort_order.data or 0,
            is_active=form.is_active.data
        )
        db.session.add(prod)
        db.session.commit()
        flash('Товар добавлен', 'success')
        return redirect(url_for('admin_products'))
    return render_template('admin/product_form.html', form=form, title='Добавить товар')


@app.route('/admin/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_product_edit(id):
    prod = db.session.get(Product, id) or abort(404)
    form = ProductForm(obj=prod)
    form.category_id.choices = [(c.id, c.name) for c in
                                 Category.query.order_by(Category.sort_order).all()]
    if form.validate_on_submit():
        up = safe_save_upload(
            form.image.data,
            app.config['UPLOAD_FOLDER'],
            {'jpg', 'jpeg', 'png', 'gif'},
        )
        if up:
            prod.image = up
        prod.category_id = form.category_id.data
        prod.name = form.name.data
        prod.description = form.description.data or ''
        prod.sort_order = form.sort_order.data or 0
        prod.is_active = form.is_active.data
        db.session.commit()
        flash('Товар обновлён', 'success')
        return redirect(url_for('admin_products'))
    return render_template('admin/product_form.html', form=form, title='Редактировать товар',
                           product=prod)


@app.route('/admin/products/<int:id>/delete', methods=['POST'])
@login_required
def admin_product_delete(id):
    prod = db.session.get(Product, id) or abort(404)
    db.session.delete(prod)
    db.session.commit()
    flash('Товар удалён', 'success')
    return redirect(url_for('admin_products'))


@app.route('/admin/products/<int:product_id>/prices/add', methods=['GET', 'POST'])
@login_required
def admin_price_add(product_id):
    prod = db.session.get(Product, product_id) or abort(404)
    form = PriceOptionForm()
    if form.validate_on_submit():
        image_path = safe_save_upload(
            form.image.data,
            app.config['UPLOAD_FOLDER'],
            {'jpg', 'jpeg', 'png', 'gif'},
        ) or ''
        po = PriceOption(
            product_id=prod.id,
            osnastka_type=form.osnastka_type.data,
            description=form.description.data or '',
            price_normal=form.price_normal.data,
            sort_order=form.sort_order.data or 0,
            image=image_path
        )
        db.session.add(po)
        db.session.commit()
        flash('Цена добавлена', 'success')
        return redirect(url_for('admin_product_edit', id=prod.id))
    return render_template('admin/price_form.html', form=form, product=prod,
                           title='Добавить цену')


@app.route('/admin/prices/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_price_edit(id):
    po = db.session.get(PriceOption, id) or abort(404)
    form = PriceOptionForm(obj=po)
    if form.validate_on_submit():
        up = safe_save_upload(
            form.image.data,
            app.config['UPLOAD_FOLDER'],
            {'jpg', 'jpeg', 'png', 'gif'},
        )
        if up:
            po.image = up
        po.osnastka_type = form.osnastka_type.data
        po.description = form.description.data or ''
        po.price_normal = form.price_normal.data
        po.sort_order = form.sort_order.data or 0
        db.session.commit()
        flash('Цена обновлена', 'success')
        return redirect(url_for('admin_product_edit', id=po.product_id))
    return render_template('admin/price_form.html', form=form, product=po.product,
                           title='Редактировать цену', price_option=po)


@app.route('/admin/prices/<int:id>/delete', methods=['POST'])
@login_required
def admin_price_delete(id):
    po = db.session.get(PriceOption, id) or abort(404)
    product_id = po.product_id
    db.session.delete(po)
    db.session.commit()
    flash('Цена удалена', 'success')
    return redirect(url_for('admin_product_edit', id=product_id))


@app.route('/admin/products/<int:product_id>/layouts/add', methods=['GET', 'POST'])
@login_required
def admin_layout_add(product_id):
    prod = db.session.get(Product, product_id) or abort(404)
    form = LayoutForm()
    if form.validate_on_submit():
        image_path = safe_save_upload(
            form.image.data,
            app.config['UPLOAD_FOLDER'],
            {'jpg', 'jpeg', 'png', 'gif'},
        ) or ''
        layout = Layout(
            product_id=prod.id,
            name=form.name.data,
            price=float(form.price.data) if form.price.data is not None else 750,
            sort_order=form.sort_order.data or 0,
            image=image_path
        )
        db.session.add(layout)
        db.session.commit()
        flash('Макет добавлен', 'success')
        return redirect(url_for('admin_product_edit', id=prod.id))
    return render_template('admin/layout_form.html', form=form, product=prod, title='Добавить макет')


@app.route('/admin/layouts/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_layout_edit(id):
    layout = db.session.get(Layout, id) or abort(404)
    form = LayoutForm(obj=layout)
    if form.validate_on_submit():
        up = safe_save_upload(
            form.image.data,
            app.config['UPLOAD_FOLDER'],
            {'jpg', 'jpeg', 'png', 'gif'},
        )
        if up:
            layout.image = up
        layout.name = form.name.data
        layout.price = float(form.price.data) if form.price.data is not None else 750
        layout.sort_order = form.sort_order.data or 0
        db.session.commit()
        flash('Макет обновлён', 'success')
        return redirect(url_for('admin_product_edit', id=layout.product_id))
    return render_template('admin/layout_form.html', form=form, product=layout.product,
                           title='Редактировать макет', layout=layout)


@app.route('/admin/layouts/<int:id>/delete', methods=['POST'])
@login_required
def admin_layout_delete(id):
    layout = db.session.get(Layout, id) or abort(404)
    product_id = layout.product_id
    db.session.delete(layout)
    db.session.commit()
    flash('Макет удалён', 'success')
    return redirect(url_for('admin_product_edit', id=product_id))


_ALLOWED_ORDER_STATUSES = ('new', 'in_progress', 'done', 'cancelled')


@app.route('/admin/orders')
@login_required
def admin_orders():
    status_filter = request.args.get('status', '')
    if status_filter and status_filter not in _ALLOWED_ORDER_STATUSES:
        status_filter = ''
    query = Order.query.order_by(Order.created_at.desc())
    if status_filter:
        query = query.filter_by(status=status_filter)
    orders = query.all()
    return render_template('admin/orders.html', orders=orders,
                           status_filter=status_filter)


PARAM_LABELS = {
    'ooo': 'ООО (наименование)',
    'ogrn': 'ОГРН',
    'ogrnip': 'ОГРНИП',
    'inn': 'ИНН',
    'city': 'Город',
    'size': 'Размер (мм)',
    'qty': 'Количество (шт)',
    'fio': 'ФИО',
    'spec': 'Специальность',
    'text': 'Текст штампа',
    'lines': 'Кол-во строк',
    'message': 'Комментарий',
}


@app.route('/admin/orders/<int:id>')
@login_required
def admin_order_detail(id):
    import json as _json
    order = db.session.get(Order, id) or abort(404)
    order_params = {}
    if order.params_json:
        try:
            order_params = _json.loads(order.params_json)
        except (ValueError, TypeError):
            pass
    return render_template('admin/order_detail.html', order=order, order_params=order_params,
                           param_labels=PARAM_LABELS)


@app.route('/admin/orders/<int:id>/status', methods=['POST'])
@login_required
def admin_order_status(id):
    order = db.session.get(Order, id) or abort(404)
    new_status = request.form.get('status')
    if new_status in _ALLOWED_ORDER_STATUSES:
        order.status = new_status
        db.session.commit()
        flash('Статус заказа обновлён', 'success')
    return redirect(url_for('admin_order_detail', id=id))


@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    form = SettingsForm()
    if request.method == 'GET':
        form.phone.data = SiteSetting.get('phone', '+7 (902) 815-79-80')
        form.email.data = SiteSetting.get('email', 'pechati5tyumen@ya.ru')
        form.address.data = SiteSetting.get('address', 'г. Тюмень')
        form.work_hours.data = SiteSetting.get('work_hours', 'ПН-ПТ 09:00-17:00')
        form.company_name.data = SiteSetting.get('company_name', 'Печати7')
        form.city.data = SiteSetting.get('city', 'Тюмень')

    if form.validate_on_submit():
        SiteSetting.set('phone', form.phone.data)
        SiteSetting.set('email', form.email.data)
        SiteSetting.set('address', form.address.data)
        SiteSetting.set('work_hours', form.work_hours.data)
        SiteSetting.set('company_name', form.company_name.data)
        SiteSetting.set('city', form.city.data)
        
        if form.logo.data:
            logo_path = safe_save_upload(
                form.logo.data,
                app.config['UPLOAD_FOLDER'],
                {'svg', 'png', 'jpg', 'jpeg'}
            )
            if logo_path:
                SiteSetting.set('logo_path', logo_path)
        
        flash('Настройки сохранены', 'success')
        return redirect(url_for('admin_settings'))

    current_logo = SiteSetting.get('logo_path', 'logo.svg')
    return render_template('admin/settings.html', form=form, current_logo=current_logo)


os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

with app.app_context():
    db.create_all()
    admin_username = os.getenv('ADMIN_USERNAME', '').strip()
    admin_password = os.getenv('ADMIN_PASSWORD', '')
    if not Admin.query.first() and admin_username and admin_password:
        admin = Admin(username=admin_username)
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        app.logger.info('Default admin created from ADMIN_USERNAME/ADMIN_PASSWORD')


if __name__ == '__main__':
    if not app.config.get('DEBUG') and app.config['SECRET_KEY'] == Config._default_secret:
        raise RuntimeError('Set SECRET_KEY in environment for production.')
    app.run(debug=app.config.get('DEBUG', False), port=int(os.getenv('PORT', 5000)))
