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
        mp3_valid = re.match("(https?:\/\/)?mp3\.zing\.vn\/bai-hat\/[\w\d\-]+/([\w\d]{8})\.html", link)
        nct_valid = re.match("https?:\/\/www\.nhaccuatui\.com\/bai-hat\/[-.a-z0-9A-Z]+\.html", link)
 
        if form.validate():

            if mp3_valid:
                link128 =MP3(link)
                flash(link128)

            elif nct_valid:
                
                link128, link320, lossless = NCT(link)
                flash(link128)

                if "hq.mp3" in link320:
                    flash(link320)

                if ".flac" in lossless:
                    flash(lossless)

            else:
                flash("Link bạn vừa nhập vào không chính xác, vui lòng kiểm tra lại")

        else:
            flash('Lỗi: Bạn cần nhập link bài hát vào.')
 
    return render_template('main.html', form=form)

def MP3(link):

    string_valid = re.search("([A-Z0-9]{8})", link).group(1)
    content = requests.get('http://phulieuminhkhang.com/images/Sanpham/api.php?parameter='+string_valid).text
    decoded = json.loads(content)
    link128 = decoded['link_download']['128']
    link320 = decoded['source']['320']
    return link128

def NCT(link):
    
    id = link.split('.')[3]
    url = 'https://graph.nhaccuatui.com/v1/commons/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Host': 'graph.nhaccuatui.com', 'Connection': 'Keep-Alive'}

    payload = {'deviceinfo': '{"DeviceID":"dd03852ada21ec149103d02f76eb0a04","DeviceName":"AppTroLyBeDieu", \
"OsName":"WINDOWS","OsVersion":"8.0","AppName":"NCTTablet","AppTroLyBeDieu":"1.3.0", \
"UserName":"0","QualityPlay":"128","QualityDownload":"128","QualityCloud":"128","Network":"WIFI","Provider":"NCTCorp"}', \
'md5': 'ebd547335f855f3e4f7136f92ccc6955', 'timestamp': '1499177482892'}

    r = requests.post(url, data=payload)
    decoded = json.loads(r.text)
    token = decoded['data']['accessToken']

    gurl = 'https://graph.nhaccuatui.com/v1/songs/'+id+'?access_token='+token
    content = requests.get(gurl)
    result = json.loads(content.text)
    link128 = result['data']['11']
    link320 = result['data']['12']
    lossless = result['data']['19']

    return link128, link320, lossless


if __name__ == "__main__":
    app.run()