import os
from app import app, db
from models import Category, Product, PriceOption, Layout, SiteSetting, Admin

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'change-me')


def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()

        PriceOption.query.delete()
        Layout.query.delete()
        Product.query.delete()
        Category.query.delete()
        SiteSetting.query.delete()
        db.session.commit()

        categories_data = [
            {'name': 'Печать организации', 'slug': 'ooo', 'icon': 'building',
             'description': 'Печати для организаций (ООО, АО)', 'sort_order': 1},
            {'name': 'ИП', 'slug': 'ip', 'icon': 'briefcase',
             'description': 'Печати для индивидуальных предпринимателей', 'sort_order': 2},
            {'name': 'Печать врача', 'slug': 'medics', 'icon': 'heart-pulse',
             'description': 'Медицинские печати для врачей', 'sort_order': 3},
            {'name': 'Факсимиле', 'slug': 'faksimile', 'icon': 'pen-nib',
             'description': 'Факсимиле — штамп-подпись', 'sort_order': 4},
            {'name': 'Штампы', 'slug': 'stamps', 'icon': 'rectangle-list',
             'description': 'Штампы различных видов', 'sort_order': 5},
            {'name': 'По оттиску', 'slug': 'ottisk', 'icon': 'copy',
             'description': 'Восстановление печати по оттиску', 'sort_order': 6},
        ]

        cats = {}
        for cd in categories_data:
            c = Category(**cd)
            db.session.add(c)
            db.session.flush()
            cats[cd['slug']] = c

        products_data = [
            {'category': 'ooo', 'name': 'Печать организации', 'description': 'Круглая печать для организаций (ООО, АО)',
             'sort_order': 1, 'prices': [
                 {'osnastka_type': 'Клише (без оснастки)', 'description': 'Простое клише без оснастки. Отлично подходит для замены клише в существующей печати.', 'price_normal': 0, 'sort_order': 0},
                 {'osnastka_type': 'Карманная оснастка Colop Mouse R40', 'description': 'Качественная оснастка известного австрийского производителя. Высокое качество оттиска, удобные в использовании боковые кнопки.', 'price_normal': 800, 'sort_order': 1},
                 {'osnastka_type': 'Автоматическая оснастка Colop Printer R40', 'description': 'Оснастка австрийского производства. Отличное качество оттиска, бесшумный и плавный механизм.', 'price_normal': 800, 'sort_order': 2},
                 {'osnastka_type': 'Автоматическая оснастка GRM Office', 'description': 'Надёжная автоматическая оснастка для офисного использования.', 'price_normal': 800, 'sort_order': 3},
             ]},
            {'category': 'ip', 'name': 'Печать ИП', 'description': 'Круглая печать для ИП',
             'sort_order': 1, 'prices': [
                 {'osnastka_type': 'Клише (без оснастки)', 'description': 'Простое клише без оснастки. Отлично подходит для замены клише в существующей печати.', 'price_normal': 0, 'sort_order': 0},
                 {'osnastka_type': 'Карманная оснастка Colop Mouse R40', 'description': 'Качественная оснастка известного австрийского производителя. Высокое качество оттиска, удобные в использовании боковые кнопки.', 'price_normal': 800, 'sort_order': 1},
                 {'osnastka_type': 'Автоматическая оснастка Colop Printer R40', 'description': 'Оснастка австрийского производства. Отличное качество оттиска, бесшумный и плавный механизм.', 'price_normal': 800, 'sort_order': 2},
                 {'osnastka_type': 'Автоматическая оснастка GRM Office', 'description': 'Надёжная автоматическая оснастка для офисного использования.', 'price_normal': 800, 'sort_order': 3},
             ]},
            {'category': 'medics', 'name': 'Печать врача', 'description': 'Треугольная или круглая печать для медиков',
             'sort_order': 1, 'prices': [
                 {'osnastka_type': 'Клише (без оснастки)', 'description': 'Простое клише без оснастки. Отлично подходит для замены клише в существующей печати.', 'price_normal': 0, 'sort_order': 0},
                 {'osnastka_type': 'Автоматическая оснастка Trodat printy 4630', 'description': 'Оснастка Trodat — это компромисс между доступной ценой, стилем и надёжностью эксплуатации.', 'price_normal': 800, 'sort_order': 1},
                 {'osnastka_type': 'Карманная оснастка Colop Mouse R40', 'description': 'Качественная оснастка известного австрийского производителя. Высокое качество оттиска, удобные в использовании боковые кнопки.', 'price_normal': 800, 'sort_order': 2},
             ]},
            {'category': 'faksimile', 'name': 'Факсимиле', 'description': 'Точное воспроизведение подписи',
             'sort_order': 1, 'prices': [{'osnastka_type': 'Стандарт', 'description': '', 'price_normal': 1200, 'sort_order': 1}], 'no_layouts': True},
            {'category': 'stamps', 'name': 'Новый штамп', 'description': 'Штамп любого размера',
             'sort_order': 1, 'prices': [{'osnastka_type': 'Стандарт', 'description': '', 'price_normal': 1000, 'sort_order': 1}], 'no_layouts': True},
            {'category': 'ottisk', 'name': 'Печать по оттиску', 'description': 'Восстановление печати по оттиску',
             'sort_order': 1, 'prices': [{'osnastka_type': 'Стандарт', 'description': '', 'price_normal': 1750, 'sort_order': 1}], 'no_layouts': True},
        ]

        for pd in products_data:
            cat = cats[pd['category']]
            p = Product(
                category_id=cat.id,
                name=pd['name'],
                description=pd['description'],
                sort_order=pd['sort_order'],
                is_active=True
            )
            db.session.add(p)
            db.session.flush()

            if not pd.get('no_layouts'):
                layout = Layout(product_id=p.id, name='Стандартный', price=750, sort_order=1)
                db.session.add(layout)

            for price in pd['prices']:
                po = PriceOption(
                    product_id=p.id,
                    osnastka_type=price['osnastka_type'],
                    description=price.get('description', ''),
                    price_normal=price['price_normal'],
                    sort_order=price.get('sort_order', 0)
                )
                db.session.add(po)

        settings = {
            'company_name': 'Печати7',
            'city': 'Тюмень',
            'phone': '+7 (902) 815-79-80',
            'email': 'pechati5tyumen@ya.ru',
            'address': 'г. Тюмень, ул. Широтная, д. 113, к. 1, с. 1 (офис 7)',
            'work_hours': 'ПН-ПТ 09:00-17:00',
        }
        for k, v in settings.items():
            db.session.add(SiteSetting(key=k, value=v))

        if not Admin.query.first():
            admin = Admin(username=ADMIN_USERNAME)
            admin.set_password(ADMIN_PASSWORD)
            db.session.add(admin)
        db.session.commit()


if __name__ == '__main__':
    seed()
