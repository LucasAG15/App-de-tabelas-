from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length


class RegisterForm(FlaskForm):
    username = StringField('Usuário', validators=[
                           InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Senha', validators=[
                             InputRequired(), Length(min=6)])
    submit = SubmitField('Registrar')


class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[
                           InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Senha', validators=[
                             InputRequired(), Length(min=6)])
    submit = SubmitField('Entrar')
