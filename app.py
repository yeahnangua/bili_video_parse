import datetime
import requests
from flask import Flask, request, redirect, send_from_directory
import re
import logging
import os

app = Flask(__name__)

logging.basicConfig(filename='app.log', level=logging.DEBUG)

# Bilibili 配置
bilibili_cookie = os.environ.get('BILIBILI_COOKIE')
bilibili_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.0.0.0',
    'Cookie': bilibili_cookie,
    'platform': 'html5',
    'referer': 'https://www.bilibili.com'
}

music_cookie = os.environ.get('MUSIC_COOKIE')
music_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.0.0.0',
    'Cookie': music_cookie,
    'referer': 'https://music.163.com/'
}

if not bilibili_cookie or not music_cookie:
    raise ValueError("Cookie environment variables are not set.")

# 解析 Bilibili 视频链接，提取 BV 号
def get_bv_from_url(url):
    if "bilibili.com/video/" in url:
        parts = url.split("/")
        for part in parts:
            if part.startswith("BV"):
                return part[0:12]
    return None
def get_fenp_from_url(url):
    try:
        if "bilibili.com/video/" in url:
            parts = url.split("/")
            for part in parts:
                if part.startswith("BV"):
                    query_string = part.split("?")[1] if '?' in part else ''
                    parameters = query_string.split("&")
                    for param in parameters:
                        if param.startswith("p="):
                            p_value = param[2:]
                            if "&" in p_value:
                                p_value = p_value.split("&")[0]
                            printt(p_value)
                            printt("获取到分p")
                            return int(p_value)
        else:
            printt("URL不是Bilibili视频链接")
            return None
    except Exception as e:
        printt(f"解析分P时发生错误: {e}")
        return None


    return 1
def get_music_from_url(url):
    return url[6:]


# 使用 Bilibili API 获取视频直链
def get_video_direct_url(bv,p):
    # 获取 cid
    pagelist_url = f"https://api.bilibili.com/x/player/pagelist?bvid={bv}"
    pagelist_response = requests.get(pagelist_url, headers=bilibili_headers)
    if pagelist_response.status_code == 200:
        printt("pagelist返回200")
        try:
            pagelist_data = pagelist_response.json()
            #printt(pagelist_data)
            #printt(p)
            cid = pagelist_data['data'][p-1]['cid']
            printt(cid)
        except Exception as e:
            printt(f"!!!!!\nException: {str(e)} {bv} {pagelist_data}\n!!!")
            return None
    else:
        return None

    # 获取视频直链
    playurl_url = f"https://api.bilibili.com/x/player/wbi/playurl?bvid={bv}&cid={cid}"
    playurl_response = requests.get(playurl_url, headers=bilibili_headers)
    if playurl_response.status_code == 200:
        try:
            playurl_data = playurl_response.json()
            video_url = playurl_data['data']['durl'][0]['url']
            return video_url
        except (KeyError, IndexError):
            return None
    else:
        return None






def live_handler(url):
    # 直播url
    url_default = re.search(r'live.bilibili.com/(\d+)', url).group(1)
    room_id = requests.get(f"https://api.live.bilibili.com/room/v1/Room/get_info?room_id={url_default}",
                           headers=bilibili_headers).json()['data']['room_id']
    live_url = requests.get(f"https://api.live.bilibili.com/room/v1/Room/playUrl?cid={room_id}&platform=h5",
                            headers=bilibili_headers).json()['data']['durl'][0]['url']
    printt(live_url)
    app.logger.info(live_url)
    return live_url

def music_hander(url):
    music_id = get_music_from_url(url)
    printt(music_id)
    req = requests.get(f"http://127.0.0.1/mv/url?id={music_id}",headers=music_headers)
    printt(req)
    reqq=req.json()
    printt(reqq)
    music_url = reqq['data']['url']
    printt(music_url)
    return music_url


def printt(a):
    if(tz == False): print(a)


@app.route('/')
def index():
    global tz
    tz=False
    url = request.args.get('url')
    if(url == 'https://www.bilibili.com/video/BV1MBNieHEfb/?spm_id_from=..search-card.all.click'):
        tz=True
        app.logger.setLevel(logging.INFO)
    printt(url)
    printt(datetime.datetime.now())
    if not tz:
        app.logger.info(datetime.datetime.now())
    if url:
        if "bilibili.com/video/" in url:
            bv = get_bv_from_url(url)
            fenp=get_fenp_from_url(url)
            if bv:
                direct_url = get_video_direct_url(bv,fenp)
                if direct_url:
                    printt("success")
                    if not tz:
                        app.logger.info("success")
                    printt("\n\n\n")

                    return redirect(direct_url)
                else:
                    printt("Failed to get video direct link")
                    app.logger.info("Failed to get video direct link")
                    printt("\n\n\n")

                    return 'Failed to get video direct link', 500
            else:
                printt("Invalid Bilibili video URL")
                app.logger.info("Invalid Bilibili video URL")
                printt("\n\n\n")

                return 'Invalid  video URL', 400
        if "live.bilibili.com" in url:
            printt(url)
            app.logger.info(url)
            live_url = live_handler(url)
            if live_url:
                printt("success")
                app.logger.info("success")
                printt("\n\n\n")

                return redirect(live_url)
            else:
                printt("Failed to get LIVE direct link")
                app.logger.info("Failed to get LIVE direct link")
                printt("\n\n\n")

                return 'Failed to get live direct  link', 500
        if "mv?id" in url:
            printt(url+"123123")
            app.logger.info(url)
            music_url = music_hander(url)
            printt(music_url)
            return redirect(music_url)


    else:
        return send_from_directory('static', 'no_video.html')


@app.route('/ts3_download')
def ts3_download_page():
    return send_from_directory('static', 'ts3_download.html')

@app.route('/logs')
def show_logs():
    with open('app.log', 'r') as f:
        log_content = f.read()
    return '<pre>' + log_content + '</pre>'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
