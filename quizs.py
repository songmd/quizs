from flask import Flask, render_template, request, redirect, url_for, send_file, Response

from datamgr import DataMgr

from wtforms import Form, BooleanField, StringField, PasswordField, SubmitField

import flask_login

import os

from io import StringIO

from flask_wtf import FlaskForm

from wtforms.validators import DataRequired


from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename

from flask_bootstrap import Bootstrap

class PhotoForm(FlaskForm):
    photo = FileField('photo', validators=[FileRequired()])
    submit = SubmitField('上传')

class LoginForm(Form):
    username = StringField('Username')
    password = PasswordField('Password')

class MyForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])

app = Flask(__name__)
app.secret_key = 'super secret string'
app.config['MONGO_USERNAME'] = 'root'
app.config['MONGO_PASSWORD'] = '888888'

data_mgr = DataMgr(app)

login_manager = flask_login.LoginManager()

login_manager.login_view = 'login'

login_manager.init_app(app)

Bootstrap(app)

import random
from PIL import Image, ImageDraw, ImageFont
class GenerateImg():
    def generate_text(self, len):
        chars, ret = 'abcdefghijklmnopqrstuvwxyz',''
        for i in range(len):
            ret += random.choice(chars)
        return ret.upper()

    @staticmethod
    def getsize(font, text):
        if hasattr(font, 'getoffset'):
            return tuple([x + y for x, y in zip(font.getsize(text), font.getoffset(text))])
        else:
            return font.getsize(text)

    @staticmethod
    def makeimg(size, bgcolor):
        if bgcolor == "transparent":
            image = Image.new('RGBA', size)
        else:
            image = Image.new('RGB', size, bgcolor)
        return image

    @staticmethod
    def noise_dots(draw, image):
        size = image.size
        for p in range(int(size[0] * size[1] * 0.1)):
            draw.point((random.randint(0, size[0]), random.randint(0, size[1])), fill='#001100')
        return draw

    @staticmethod
    def post_smooth(image):
        from PIL import ImageFilter
        return image.filter(ImageFilter.SMOOTH)


    def generate_img(self, text, scale=1):
        fontpath = os.path.normpath(os.path.join(os.path.dirname(__file__), '.', 'fonts/Vera.ttf'))
        fontsize = 22
        font = ImageFont.truetype(fontpath, fontsize * scale)
        rotation = (-35,35)
        DISTNACE_FROM_TOP = 4

        settingsize = (201,97)
        imgsize = None
        # bgcolor = 'transparent'
        bgcolor = '#001100'

        if settingsize:
            imgsize = settingsize
        else:
            imgsize = self.getsize(font, text)
            imgsize = (imgsize[0] * 2, int(imgsize[1] * 1.4))

        image = self.makeimg(imgsize,bgcolor)
        xpos = 2

        for char in text:
            fgimage = Image.new('RGB', imgsize, '#001100')
            charimage = Image.new('L', self.getsize(font, ' %s ' % char), '#000000')
            chardraw = ImageDraw.Draw(charimage)
            chardraw.text((0, 0), ' %s ' % char, font=font, fill='#ffffff')



            if rotation:
                charimage = charimage.rotate(random.randrange(*rotation), expand=0,
                                             resample=Image.BICUBIC)
            charimage = charimage.crop(charimage.getbbox())


            maskimage = Image.new('L', imgsize)

            maskimage.paste(charimage,
                            (xpos, DISTNACE_FROM_TOP, xpos + charimage.size[0], DISTNACE_FROM_TOP + charimage.size[1]))
            imgsize = maskimage.size
            image = Image.composite(fgimage, image, maskimage)
            xpos = xpos + 2 + charimage.size[0]
            with open('/Users/hero101/temp/%s.png' % char, 'wb') as out2:
                maskimage.save(out2, 'PNG')


        if imgsize:
            # centering captcha on the image
            tmpimg = self.makeimg(imgsize, bgcolor)
            tmpimg.paste(image, (int((imgsize[0] - xpos) / 2), int((imgsize[1] - charimage.size[1]) / 2 - DISTNACE_FROM_TOP)))
            image = tmpimg.crop((0, 0, imgsize[0], imgsize[1]))
        else:
            image = image.crop((0, 0, xpos + 1, imgsize[1]))
        draw = ImageDraw.Draw(image)

        # self.noise_dots(draw, image)
        #
        # self.post_smooth(image)

        out = StringIO()
        with open('/Users/hero101/temp/%s.png' % text, 'wb') as out2:
            image.save(out2,'PNG')
        # image.save(out, "PNG")
        # out.seek(0)

users = {'foo@bar.tld': {'password': 'secret'}}

class User(flask_login.UserMixin):
    pass

@app.route('/bootstrap')
def show_bootsrap():
    return render_template('bootstrap.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = PhotoForm()
    if form.validate_on_submit():
        f = form.photo.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(
            '/Users/hero101', 'photos', filename
        ))
        return redirect(url_for('index'))

    return render_template('upload.html', form=form)

@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['password'] == users[email]['password']

    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        form = LoginForm()
        return render_template('login.html',form=form)
        return '''
               <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'/>
                <input type='password' name='password' id='password' placeholder='password'/>
                <input type='submit' name='submit'/>
               </form>
               '''

    email = request.form['email']
    if email in users and request.form['password'] == users[email]['password']:
        user = User()
        user.id = email
        flask_login.login_user(user)
        return redirect(url_for('protected'))

    return 'Bad login'


@app.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.id

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'

# @login_manager.unauthorized_handler
# def unauthorized_handler():
#     return 'Unauthorized'

@app.route('/submit', methods=('GET', 'POST'))
def submit():
    form = MyForm()
    if form.validate_on_submit():
        return redirect('/')
    return render_template('submit.html', form=form)

from io import BytesIO
from captcha import ImageCaptcha
@app.route('/generate')
def generate():
    captcha = ImageCaptcha()
    chars = captcha.generate_text(5)
    im = captcha.generate_image(chars)
    out = BytesIO()
    im.save(out, 'PNG')
    out.seek(0)
    # return send_file(out,mimetype='image/png')
    return Response(out, mimetype='image/png')
    # return "hello world"
    # return send_file(filename, mimetype='image/gif')
    # pass

@app.route('/')
def index():
    return render_template('register.html')
    # users = data_mgr.get_user_list()
    #
    # print(users)

    # author = 'fxf'
    # stem = ['解释加粗字的意思。', '解落三秋叶', '#img:/var/www/temp.jpg']
    # options = dict(A='排泄，解手', B='知道，懂得', C='分析，讲解')
    # answer = ['B']
    # analysis = '本题考察学生的诗词知识， 。。。。故应选 B'
    #
    # result = data_mgr.add_question(author, stem, options, answer, analysis)
    # print(result)

    # data_mgr.add_record('songmd1981', '5a5611ce37a8ce9644a89014', ['A', 'B', 'C'], False)
    # print(data_mgr.get_question('songmd1980'))

    # result = data_mgr.add_user('songwenyan2')
    # print('result:', result)

    # print(data_mgr.is_user_exist('songmd1983'))
    #
    # print(data_mgr.is_user_exist('songmd1980'))s
    #
    # print(data_mgr.is_user_exist('songwenyan'))

    q = data_mgr.get_new_question('songmd1980')
    print(q)
    return render_template('hello.html', question=q)

    # print(data_mgr.get_new_question('songmd1980'))
    # print(data_mgr.get_new_question('songmd1983'))
    # print(data_mgr.get_new_question('songwenyan'))
    # return 'Hello World!'


if __name__ == '__main__':
    app.run()
