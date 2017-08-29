#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, flash, request, Response
from wtforms import Form, TextField, validators
from flask_wtf import FlaskForm
from caesarcipher import CaesarCipher
from config import cookies, apikey, fshare, acc4share
import os
import requests
import re
import json
import youtube_dl
import base64
 
# App config.
DEBUG = False
app = Flask(__name__, static_url_path='/static')
app.config.from_object(__name__)
app.config['SECRET_KEY'] = os.urandom(30)

class WebForm(FlaskForm):
    link = TextField('link', validators=[validators.required()])

@app.route("/", methods=['GET', 'POST'])
def hello():
    form = WebForm()
 
    if request.method == 'POST':

        raw = request.form['link']
        link = raw.split(" | ")[0]
        mp3_valid = re.match("(https?:\/\/)?(m.)?mp3\.zing\.vn\/bai-hat\/[\w\d\-]+/([\w\d]{8})\.html", link)
        nct_valid = re.match("https?:\/\/www\.nhaccuatui\.com\/bai-hat\/[-.a-z0-9A-Z]+\.html", link)
        sc_valid = re.match("https:\/\/soundcloud.com\/[-a-z0-9]+\/[-a-z0-9]+", link)
        fs_valid = re.match("https:\/\/www.fshare.vn\/file\/[0-9A-Z]+\/?", link)
        fourshare = re.match("https?:\/\/4share.vn/f/([0-9a-z]+)/?(.+)?", link)
 
        if form.validate_on_submit():

            if mp3_valid:

                try:
                    player, title, artist, thumbnail, link128, link320, lossless = MP3(link)
                    flash(u"Get link thành công!", 'success')
                    flash(link128, '128Kbps')
                    if link320:
                        flash(link320, '320Kbps')
                    if lossless:
                        flash(lossless, 'Lossless')
                    flash(player, 'player')
                    flash(title, 'title')
                    flash(artist, 'artist')
                    flash(thumbnail, 'thumbnail')
                except:
                    msg = MP3(link)
                    if msg:
                        flash("Bài hát này có bản quyền", 'copyright')
                    else:
                        flash("Lỗi nghiêm trọng đã xảy ra.", 'fail')


            elif nct_valid:

                try:
                    title, artist, thumbnail, link128, link320, lossless = NCT(link)
                    flash(u"Get link thành công!", 'success')
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
                except:
                    flash("Lỗi nghiêm trọng đã xảy ra.", 'fail')

            elif sc_valid:

                try:
                    title, thumbnail, link128 = SC(link)
                    flash(u"Get link thành công!", 'success')
                    player = link128
                    flash(link128, 'linksc')
                    flash(player, 'player')
                    flash(title, 'title')
                    flash('mrvir', 'artist')
                    flash(thumbnail, 'thumbnail')

                except:
                    flash("Lỗi nghiêm trọng đã xảy ra.", 'fail')

            elif fs_valid:

                try:
                    pw = raw.split(" | ")[1]
                except:
                    pw = ""

                try:
                    fslink = FS(link, pw)
                    flash(u"Get link thành công!", 'success')
                    flash(fslink, 'fslink')
                except:
                    flash("Lỗi nghiêm trọng đã xảy ra.", 'fail')

            elif fourshare:

                try:
                    link4share = get4S(link)
                    flash(u"Get link thành công!", 'success')
                    flash(link4share, 'link4share')
                except:
                    flash("Lỗi nghiêm trọng đã xảy ra.", 'fail')

            else:
                flash(u"Link bạn vừa nhập vào không chính xác, vui lòng kiểm tra lại", 'error')

        else:
            flash(u'Bạn cần nhập link vào.', 'error')
 
    return render_template('main.html', form=form)

@app.route("/api", methods=['GET'])
def api():
    global apikey
    key = request.args.get('key')
    url = request.args.get('url')
    try:
        pw = request.args.get('pw')
    except:
        pw = ""

    mp3_valid = re.match("(https?:\/\/)?mp3\.zing\.vn\/bai-hat\/[\w\d\-]+/([\w\d]{8})\.html", url)
    mp3v_valid = re.match("(https?:\/\/)?mp3\.zing\.vn\/video-clip\/[\w\d\-]+/([\w\d]{8})\.html", url)
    nct_valid = re.match("https?:\/\/www\.nhaccuatui\.com\/bai-hat\/[-.a-z0-9A-Z]+\.html", url)
    sc_valid = re.match("https:\/\/soundcloud.com\/[-a-z0-9]+\/[-a-z0-9]+", url)
    fs_valid = re.match("https:\/\/www.fshare.vn\/file\/[0-9A-Z]+\/?", url)
    fourshare = re.match("https?:\/\/4share.vn/f/([0-9a-z]+)/?(.+)?", url)

    if key not in apikey:
        return "Incorrect API Key!"
    else:
        if mp3_valid:
            player, title, artist, thumbnail, link128, link320, lossless = MP3(url)
            data = {'title':title, 'artist':artist, 'thumbnail':thumbnail, 'link128':link128, 'link320':link320, 'lossless':lossless}
            resp = Response(response=json.dumps(data), status=200, mimetype="application/json")
            return resp
        elif mp3v_valid:
            v360, v480, v720, v1080= MP3V(url)
            data = {'v360':v360, 'v480':v480, 'v720':v720, 'v1080':v1080}
            resp = Response(response=json.dumps(data), status=200, mimetype="application/json")
            return resp
        elif nct_valid:
            title, artist, thumbnail, link128, link320, lossless = NCT(url)
            data = {'title':title, 'artist':artist, 'thumbnail':thumbnail, 'link128':link128, 'link320':link320, 'lossless':lossless}
            resp = Response(response=json.dumps(data), status=200, mimetype="application/json")
            return resp
        elif sc_valid:
            title, thumbnail, link128 = SC(url)
            data = {'title':title, 'thumbnail':thumbnail, 'link128':link128 }
            resp = Response(response=json.dumps(data), status=200, mimetype="application/json")
            return resp
        elif fs_valid:
            result = FS(url, pw)
            link = encodeURL(result)
            data = {'link':link}
            resp = Response(response=json.dumps(data), status=200, mimetype="application/json")
            return resp
        elif fourshare:
            link = get4S(url)
            data = {'link':link}
            resp = Response(response=json.dumps(data), status=200, mimetype="application/json")
            return resp
        else:
            return "Incorrect URL!"

@app.route("/redirector", methods=['GET'])
def decode():

    code = request.args.get('code')
    try:
        cipher = CaesarCipher(code, offset=14).decoded
        link = base64.b64decode(cipher.encode('ascii'))
        flash(u"Giải mã URL thành công!", 'success')
        flash(link.decode('ascii'), 'link')
    except:
        flash("Giải mã URL thất bại!", 'fail')

    return render_template('link.html')

def MP3(link):

    global cookies
    
    link = link.replace("m.", "")
    s = requests.Session()
    r = s.get(link, cookies=cookies)

    code = re.search('data-code=\"([a-zA-Z0-9]{20,30})\"', r.text).group(1)
    xml = re.search('data-xml=\"(.+)\"', r.text).group(1)
    
    data = s.get("http://mp3.zing.vn"+xml, cookies=cookies).text
    dedata = json.loads(data)

    title = dedata['data'][0]['name']
    artist = dedata['data'][0]['artist']
    thumbnail = dedata['data'][0]['cover']

    content = s.get("http://mp3.zing.vn/json/song/get-download?code="+code, cookies=cookies).text
    decoded = json.loads(content)

    msg = decoded['msg']

    if msg:
        return msg

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


def MP3V(link):

    global cookies
    
    link = link.replace("m.", "")
    s = requests.Session()
    r = s.get(link, cookies=cookies)

    xml = re.search('data-xml=\"(.+)\"', r.text).group(1)
    
    data = s.get("http://mp3.zing.vn"+xml, cookies=cookies).text
    dedata = json.loads(data)

    v360 = dedata['data']['item'][0]['source_list'][0]

    try:
        v480 = dedata['data']['item'][0]['source_list'][1]
    except:
        v480 = ""
    try:
        v720 = dedata['data']['item'][0]['source_list'][2]
    except:
        v720 = ""
    try:
        v1080 = dedata['data']['item'][0]['source_list'][3]
    except:
        v1080 = ""

    return v360, v480, v720, v1080

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

def SC(link):

    ydl = youtube_dl.YoutubeDL()
    result = ydl.extract_info(link, download=False)
    link128 = result['url']
    title = result['title']
    thumbnail = result['thumbnail']

    return title, thumbnail, link128

def FS(link, pw):

    global fshare
    r = requests.Session()
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    loginpage = r.get("https://www.fshare.vn/login", headers=headers)
    cookies = loginpage.cookies
    csrftoken = re.search('<input type=\"hidden\" value=\"([0-9a-z]+)\" name=\"fs_csrf\" \/>', loginpage.text).group(1)
    payload =  {'fs_csrf': csrftoken, 
                'LoginForm[email]': fshare[0], 
                'LoginForm[password]': fshare[1], 
                'LoginForm[rememberMe]': 1, 
                'LoginForm[checkloginpopup]': 0, 
                'yt0': 'Đăng nhập'}
    response = r.post("https://www.fshare.vn/login", data=payload, headers=headers, cookies=cookies)
    id = re.search('https:\/\/www.fshare.vn\/file\/([0-9A-Z]+)\/?', link).group(1)
    downloadpage = r.get(link, headers=headers)
    csrftoken = re.search('<input type=\"hidden\" value=\"([0-9a-z]+)\" name=\"fs_csrf\" \/>', downloadpage.text).group(1)
    dl_data =  {'fs_csrf': csrftoken,
                "DownloadForm[pwd]": pw,
                "DownloadForm[linkcode]": id,
                "ajax": "download-form",
                "undefined": "undefined"}
    getlink = r.post("https://www.fshare.vn/download/get", headers=headers, data=dl_data).text
    result = json.loads(getlink)

    return result['url']

def get4S(link):

    global acc4share
    id = re.search('https?:\/\/4share.vn/f/([0-9a-z]+)/?(.+)?', link).group(1)
    payload = "/{0}/{1}/{2}/".format(acc4share[0], acc4share[1], id)
    encoded = base64.b64encode(payload.encode('ascii'))
    link4share = 'https://4share.vn/tool/?dlfile=' + encoded.decode("ascii")

    return link4share

def encodeURL(link):

    encoded = base64.b64encode(link.encode('ascii'))
    ciphertext = CaesarCipher(encoded.decode('ascii'), offset=14).encoded
    result = "https://mp3zing.download/redirector?code=" + ciphertext

    return result

if __name__ == "__main__":
    app.run()