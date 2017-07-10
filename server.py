from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import os
import requests
import re
import json
 
# App config.
DEBUG = False
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = os.urandom(30)
 
class WebForm(Form):
    link = TextField('Nhập link bài hát:', validators=[validators.required()])
 
@app.route("/", methods=['GET', 'POST'])
def hello():
    form = WebForm(request.form)
 
    if request.method == 'POST':
        link=request.form['link']
 
        if form.validate():
            link128 = Process(link)
            flash(link128)
        else:
            flash('Lỗi: Bạn cần nhập link bài hát vào.')
 
    return render_template('main.html', form=form)

def Process(link):
    mp3_valid = re.match("(https?:\/\/)?mp3\.zing\.vn\/bai-hat\/[\w\d\-]+/([\w\d]{8})\.html", link)
    nct_valid = re.match("https?:\/\/www\.nhaccuatui\.com\/bai-hat\/[-.a-z0-9A-Z]+\.html", link)

    if mp3_valid:
        string_valid = re.search("([A-Z0-9]{8})", link).group(1)
        content = requests.get('http://phulieuminhkhang.com/images/Sanpham/api.php?parameter='+string_valid).text
        decoded = json.loads(content)
        link128 = decoded['link_download']['128']
        link320 = decoded['source']['320']
        return link128
    elif nct_valid:
        content = requests.get(link).text
        xml = re.search("https?:\/\/www\.nhaccuatui\.com\/flash\/xml\?key1=[0-9a-z]{30,40}", content).group(0)
        headers = {'content-type': 'application/xml'}
        xmlcontent = requests.get(xml, headers=headers).text
        link128 = re.search("https?:\/\/[^\/]+\.nixcdn\.com\/[-_\/a-zA-Z0-9]+\.mp3", xmlcontent).group(0)
        link320 = "Empty"
        return link128
    else:
        result = "Link bạn vừa nhập vào không chính xác, vui lòng kiểm tra lại"
        return result



if __name__ == "__main__":
    app.run()