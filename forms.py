from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, PasswordField, FloatField, IntegerField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, Optional, Length, InputRequired


class OrderForm(FlaskForm):
    name = StringField('Ваше имя', validators=[DataRequired(message='Введите имя'), Length(max=200)])
    phone = StringField('Телефон', validators=[DataRequired(message='Введите телефон'), Length(max=50)])
    email = StringField('Email', validators=[Optional(), Email(message='Некорректный email')])
    order_type = SelectField('Тип печати', choices=[
        ('', 'Выберите тип...'),
        ('Печать организации', 'Печать организации'),
        ('Печать ИП', 'Печать ИП'),
        ('Печать врача', 'Печать врача'),
        ('Факсимиле', 'Факсимиле'),
        ('Штамп новый', 'Штамп новый'),
        ('Штамп по оттиску', 'Штамп по оттиску'),
        ('Печать по оттиску', 'Печать по оттиску'),
        ('Другое', 'Другое'),
    ])
    osnastka = SelectField('Тип оснастки', choices=[
        ('', 'Выберите оснастку...'),
        ('Пластиковая (ручная)', 'Пластиковая (ручная)'),
        ('Автоматическая', 'Автоматическая'),
        ('Карманная', 'Карманная'),
    ])
    message = TextAreaField('Комментарий', validators=[Optional(), Length(max=2000)])
    consent_pd = BooleanField('Даю согласие на обработку персональных данных', validators=[DataRequired(message='Необходимо дать согласие на обработку персональных данных')])
    file = FileField('Загрузить оттиск', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'pdf'], 'Только изображения и PDF')
    ])


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])


class CategoryForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired(), Length(max=200)])
    slug = StringField('URL-имя (slug)', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Описание', validators=[Optional()])
    icon = StringField('Иконка (CSS класс)', validators=[Optional()])
    sort_order = IntegerField('Порядок сортировки', default=0)
    is_active = BooleanField('Активна', default=True)
    image = FileField('Картинка', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Только изображения')])


class ProductForm(FlaskForm):
    category_id = SelectField('Категория', coerce=int, validators=[DataRequired()])
    name = StringField('Название', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Описание', validators=[Optional()])
    sort_order = IntegerField('Порядок сортировки', default=0)
    is_active = BooleanField('Активен', default=True)
    image = FileField('Картинка', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Только изображения')])


class PriceOptionForm(FlaskForm):
    osnastka_type = StringField('Тип оснастки', validators=[DataRequired()])
    description = TextAreaField('Описание оснастки', validators=[Optional()])
    price_normal = FloatField('Цена', validators=[InputRequired()])
    sort_order = IntegerField('Порядок', default=0)
    image = FileField('Картинка оснастки', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Только изображения')])


class LayoutForm(FlaskForm):
    name = StringField('Название макета', validators=[DataRequired(), Length(max=200)])
    price = FloatField('Цена макета, руб.', default=750)
    sort_order = IntegerField('Порядок', default=0)
    image = FileField('Картинка макета', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Только изображения')])


class SettingsForm(FlaskForm):
    phone = StringField('Телефон')
    email = StringField('Email')
    address = StringField('Адрес')
    work_hours = StringField('Режим работы')
    company_name = StringField('Название компании')
    city = StringField('Город')
