from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from models import User

class LoginForm(FlaskForm):
    username = StringField('Foydalanuvchi nomi', validators=[DataRequired()])
    password = PasswordField('Parol', validators=[DataRequired()])
    remember = BooleanField('Eslab qolish')
    submit = SubmitField('Kirish')

class RegistrationForm(FlaskForm):
    username = StringField('Foydalanuvchi nomi', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Parol', validators=[DataRequired()])
    confirm_password = PasswordField('Parolni tasdiqlash', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Ro\'yxatdan o\'tish')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Bu nom allaqachon band.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Bu email allaqachon ro\'yxatdan o\'tgan.')

class UpdateAccountForm(FlaskForm):
    username = StringField('Foydalanuvchi nomi', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Profil rasmi', validators=[FileAllowed(['jpg', 'png'], 'Faqat rasmlar!')])
    bio = TextAreaField('O\'zingiz haqida (Bio)')
    submit = SubmitField('Yangilash')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Bu nom allaqachon band.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Bu email allaqachon ro\'yxatdan o\'tgan.')

class PostForm(FlaskForm):
    title = StringField('Sarlavha', validators=[DataRequired()])
    category = SelectField('Kategoriya', coerce=int)
    image = FileField('Muqova Rasmi', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'webp'], 'Faqat rasmlar!')])
    video = FileField('Video', validators=[FileAllowed(['mp4', 'mov', 'avi'], 'Faqat video (mp4, mov, avi)!')])
    audio = FileField('Audio', validators=[FileAllowed(['mp3', 'wav', 'ogg', 'm4a', 'flac', 'aac'], 'Faqat audio (mp3, wav, m4a, flac, aac, ogg)!')])
    summary = TextAreaField('Qisqacha mazmun')
    content = TextAreaField('Maqola matni')  # DataRequired removed because SimpleMDE syncs via JS
    submit = SubmitField('Saqlash')

class CommentForm(FlaskForm):
    author = StringField('Ismingiz', validators=[DataRequired()])
    content = TextAreaField('Fikringiz', validators=[DataRequired()])
    submit = SubmitField('Yuborish')

class ContactForm(FlaskForm):
    name = StringField('Ismingiz', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Xabar', validators=[DataRequired()])
    submit = SubmitField('Yuborish')

class SiteSettingsForm(FlaskForm):
    site_name = StringField('Sayt Nomi')
    telegram = StringField('Telegram')
    instagram = StringField('Instagram')
    github = StringField('GitHub')
    twitter = StringField('Twitter')
    youtube = StringField('YouTube')
    submit = SubmitField('Saqlash')
