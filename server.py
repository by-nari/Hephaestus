from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import os
import requests
import re
import json
import config
 
# App config.
DEBUG = False
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = os.urandom(30)
cookies = config.cookies
apikey = config.apikey

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

                player, title, artist, thumbnail, link128, link320, lossless = MP3(link)
                flash(link128, '128Kbps')
                if link320:
                    flash(link320, '320Kbps')
                if lossless:
                    flash(lossless, 'Lossless')
                flash(player, 'player')
                flash(title, 'title')
                flash(artist, 'artist')
                flash(thumbnail, 'thumbnail')


            elif nct_valid:
                
                title, artist, thumbnail, link128, link320, lossless = NCT(link)
                player = link128
                flash(link128, '128Kbps')

                if "hq.mp3" in link320:
                    flash(link320, '320Kbps')

                if ".flac" in lossless:
                    flash(lossless, 'Lossless')
                    
                flash(player, 'player')
                flash(title, 'title')
                flash(artist, 'artist')
                flash(thumbnail, 'thumbnail')

            else:
                flash("Link bạn vừa nhập vào không chính xác, vui lòng kiểm tra lại", 'error')

        else:
            flash('Lỗi: Bạn cần nhập link bài hát vào.', 'error')
 
    return render_template('main.html', form=form)

@app.route("/api", methods=['GET'])
def api():
    global apikey
    key = request.args.get('key')
    url = request.args.get('url')
    mp3_valid = re.match("(https?:\/\/)?mp3\.zing\.vn\/bai-hat\/[\w\d\-]+/([\w\d]{8})\.html", url)
    nct_valid = re.match("https?:\/\/www\.nhaccuatui\.com\/bai-hat\/[-.a-z0-9A-Z]+\.html", url)
    if key not in apikey:
        return "Incorrect API Key!"
    else:
        if mp3_valid:
            player, title, artist, thumbnail, link128, link320, lossless = MP3(url)
            data = {'title':title, 'artist':artist, 'thumbnail':thumbnail, 'link128':link128, 'link320':link320, 'lossless':lossless}
            return json.dumps(data)
        elif nct_valid:
            title, artist, thumbnail, link128, link320, lossless = NCT(url)
            data = {'title':title, 'artist':artist, 'thumbnail':thumbnail, 'link128':link128, 'link320':link320, 'lossless':lossless}
            return json.dumps(data)
        else:
            return "Incorrect URL!"

def MP3(link):

    global cookies
    s = requests.Session()
    r = s.get(link, cookies=config.cookies)

    code = re.search('data-code=\"([a-zA-Z0-9]{20,30})\"', r.text).group(1)
    xml = re.search('data-xml=\"(.+)\"', r.text).group(1)
    
    data = s.get("http://mp3.zing.vn"+xml, cookies=cookies).text
    dedata = json.loads(data)

    title = dedata['data'][0]['name']
    artist = dedata['data'][0]['artist']
    thumbnail = dedata['data'][0]['cover']

    content = s.get("http://mp3.zing.vn/json/song/get-download?code="+code, cookies=cookies).text
    decoded = json.loads(content)

    link128 = s.get('http://mp3.zing.vn' + decoded['data']['128']['link'], cookies=cookies, allow_redirects=False).headers['Location']
    player = link128
    try:
        link320 = s.get('http://mp3.zing.vn' + decoded['data']['320']['link'], cookies=cookies, allow_redirects=False).headers['Location']
    except:
        link320 = ""
        lossless = ""
        return player, title, artist, thumbnail, link128, link320, lossless
    try:
        lossless = s.get('http://mp3.zing.vn' + decoded['data']['lossless']['link'], cookies=cookies, allow_redirects=False).headers['Location']
    except:
        lossless = ""
        return player, title, artist, thumbnail, link128, link320, lossless

    return player, title, artist, thumbnail, link128, link320, lossless


def NCT(link):
    
    id = link.split('.')[3]
    url = 'https://graph.nhaccuatui.com/v1/commons/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Host': 'graph.nhaccuatui.com', 'Connection': 'Keep-Alive'}

    payload = {'deviceinfo': '{"DeviceID":"dd03852ada21ec149103d02f76eb0a04","DeviceName":"AppTroLyBeDieu", \
"OsName":"WINDOWS","OsVersion":"8.0","AppName":"NCTTablet","AppTroLyBeDieu":"1.3.0", \
"UserName":"0","QualityPlay":"128","QualityDownload":"128","QualityCloud":"128","Network":"WIFI","Provider":"NCTCorp"}', \
'md5': 'ebd547335f855f3e4f7136f92ccc6955', 'timestamp': '1499177482892'}

    r = requests.post(url, data=payload, headers=headers)
    decoded = json.loads(r.text)
    token = decoded['data']['accessToken']

    gurl = 'https://graph.nhaccuatui.com/v1/songs/'+id+'?access_token='+token
    content = requests.get(gurl)
    result = json.loads(content.text)

    link128 = result['data']['11']
    link320 = result['data']['12']
    lossless = result['data']['19']
    title = result['data']['2']
    artist = result['data']['3']
    thumbnail = result['data']['8']


    return title, artist, thumbnail, link128, link320, lossless


if __name__ == "__main__":
    app.run()