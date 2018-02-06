from quizs import GenerateImg
from captcha import ImageCaptcha

def test_captcha():
    captcha = ImageCaptcha()

    chars = captcha.generate_text(5)
    im = captcha.generate_image(chars)

    with open('/Users/hero101/temp/%s.png' % chars, 'wb') as out2:
        im.save(out2, 'PNG')

def test_generate_text():
    print('')
    # gi = GenerateImg()
    # for i in range(2,8):
    #     text = gi.generate_text(i)
    #     print(text)
    #     gi.generate_img(text)
