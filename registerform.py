from io import BytesIO

from flask import Flask, render_template, Response, session, request
from flask_appconfig import AppConfig
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, ValidationError, SubmitField
from wtforms.validators import InputRequired, EqualTo

from captcha import ImageCaptcha


class Length(object):
    def __init__(self, min_len=-1, max_len=-1, message=None):
        self.min_len = min_len
        self.max_len = max_len
        if not message:
            message = '须输入%i～%i个字符' % (min_len, max_len)
        self.message = message

    def __call__(self, form, field):
        field_len = field.data and len(field.data) or 0
        if field_len < self.min_len or self.max_len != -1 and field_len > self.max_len:
            raise ValidationError(self.message)


class RegisterForm(FlaskForm):
    user_name = StringField('用户名', validators=[Length(6, 18)],
                            description='6~18个字符，可使用字母、数字、下划线，需以字母开头')
    password = PasswordField('密码',
                             validators=[ Length(6, 18)],
                             description='6~16个字符，区分大小写')
    confirm = PasswordField('确认密码', validators=[ EqualTo('password', message='两次输入密码必须一致')], description='请再次填写密码')

    captch_code = None
    captch = StringField('验证码',  description='请填写图片中的字符，不区分大小写')

    def validate_captch(self, field):
        print('bingin validate  ', field.data)
        if field.data.upper() != self.captch_code:
            print('validate', '  input:  ', field.data.upper(), '  generate:  ', self.captch_code)
            raise ValidationError('验证码输入错误')

    submit = SubmitField('注册')


def create_app(configfile=None):
    app = Flask(__name__)
    AppConfig(app, configfile)  # Flask-Appconfig is not necessary, but
    # highly recommend =)
    # https://github.com/mbr/flask-appconfig
    Bootstrap(app)

    # in a real app, these should be configured through Flask-Appconfig
    app.config['SECRET_KEY'] = 'devkey'
    app.config['RECAPTCHA_PUBLIC_KEY'] = \
        '6Lfol9cSAAAAADAkodaYl9wvQCwBMr3qGR_PPHcw'

    @app.route('/', methods=('GET', 'POST'))
    def index():
        print('index  ', request.method)
        form = RegisterForm()
        if request.method == 'POST':
            form.captch_code = session['captcha']
            if form.validate_on_submit():
                print('validate ok')
        # to get error messages to the browser
        # flash('critical message', 'critical')
        # flash('error message', 'error')
        # flash('warning message', 'warning')
        # flash('info message', 'info')
        # flash('debug message', 'debug')
        # flash('different message', 'different')
        # flash('uncategorized message')
        return render_template('register2.html', form=form)

    @app.route('/generate')
    def generate():
        captcha = ImageCaptcha()
        chars = captcha.generate_text(5)
        im = captcha.generate_image(chars)
        out = BytesIO()
        im.save(out, 'PNG')
        out.seek(0)
        session['captcha'] = chars
        print('generate img:', chars)
        # return send_file(out,mimetype='image/png')
        return Response(out, mimetype='image/png')
        # return "hello world"
        # return send_file(filename, mimetype='image/gif')
        # pass

    return app


if __name__ == '__main__':
    create_app().run(debug=True)
