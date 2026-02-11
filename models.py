from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text, default='')
    image = db.Column(db.String(300), default='')
    icon = db.Column(db.String(100), default='')
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    products = db.relationship('Product', backref='category', lazy=True,
                               order_by='Product.sort_order')


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    image = db.Column(db.String(300), default='')
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    price_options = db.relationship('PriceOption', backref='product', lazy=True,
                                    cascade='all, delete-orphan',
                                    order_by='PriceOption.sort_order')
    layouts = db.relationship('Layout', backref='product', lazy=True,
                              cascade='all, delete-orphan',
                              order_by='Layout.sort_order')


class Layout(db.Model):
    __tablename__ = 'layouts'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    image = db.Column(db.String(300), default='')
    price = db.Column(db.Float, default=750)
    sort_order = db.Column(db.Integer, default=0)


class PriceOption(db.Model):
    __tablename__ = 'price_options'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    osnastka_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='')
    image = db.Column(db.String(300), default='')
    price_normal = db.Column(db.Float, nullable=False, default=0)
    sort_order = db.Column(db.Integer, default=0)


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    layout_id = db.Column(db.Integer, db.ForeignKey('layouts.id'), nullable=True)
    price_option_id = db.Column(db.Integer, db.ForeignKey('price_options.id'), nullable=True)
    total_price = db.Column(db.Float, nullable=True)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(200), default='')
    order_type = db.Column(db.String(200), default='')
    osnastka = db.Column(db.String(200), default='')
    message = db.Column(db.Text, default='')
    file_path = db.Column(db.String(300), default='')
    file_path_step3 = db.Column(db.String(300), default='')
    params_json = db.Column(db.Text, default='')
    status = db.Column(db.String(50), default='new')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    needs_delivery = db.Column(db.Boolean, default=False)
    delivery_datetime = db.Column(db.String(200), default='')
    delivery_address = db.Column(db.Text, default='')

    product = db.relationship('Product', backref='orders', lazy=True)
    layout = db.relationship('Layout', backref='orders', lazy=True)
    price_option = db.relationship('PriceOption', backref='orders', lazy=True)

    @property
    def status_label(self):
        labels = {
            'new': 'Новый',
            'in_progress': 'В работе',
            'done': 'Готов',
            'cancelled': 'Отменён'
        }
        return labels.get(self.status, self.status)

    @property
    def status_color(self):
        colors = {
            'new': 'blue',
            'in_progress': 'yellow',
            'done': 'green',
            'cancelled': 'red'
        }
        return colors.get(self.status, 'gray')


class SiteSetting(db.Model):
    __tablename__ = 'site_settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, default='')

    @staticmethod
    def get(key, default=''):
        setting = SiteSetting.query.filter_by(key=key).first()
        return setting.value if setting else default

    @staticmethod
    def set(key, value):
        setting = SiteSetting.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = SiteSetting(key=key, value=value)
            db.session.add(setting)
        db.session.commit()
