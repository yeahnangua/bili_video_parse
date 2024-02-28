import datetime
import requests
from flask import Flask, request, redirect, send_from_directory
import re

app = Flask(__name__)

# Bilibili 配置
bilibili_cookie = ""  # 请在这里填入你的 Bilibili Cookie
bilibili_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.0.0.0',
    'Cookie': bilibili_cookie,
    'platform': 'html5',
    'referer': 'https://www.bilibili.com'
}

# 网易云音乐配置
netease_headers = {
    'Cookie': bilibili_cookie,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}

# 解析 Bilibili 视频链接，提取 BV 号
def get_bv_from_url(url):
    if "bilibili.com/video/" in url:
        parts = url.split("/")
        for part in parts:
            if part.startswith("BV"):
                return part
    return None

# 使用 Bilibili API 获取视频直链
def get_video_direct_url(bv):
    # 获取 cid
    pagelist_url = f"https://api.bilibili.com/x/player/pagelist?bvid={bv}"
    pagelist_response = requests.get(pagelist_url, headers=bilibili_headers)
    if pagelist_response.status_code == 200:
        try:
            pagelist_data = pagelist_response.json()
            cid = pagelist_data['data'][0]['cid']
        except (KeyError, IndexError):
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

# 网易云音乐解析逻辑（示例，需要实际实现）
def netease_music_handler(url):
    # 这里应实现对网易云音乐歌曲ID的解析或歌曲名搜索，以及获取下载链接的逻辑
    # 由于实现细节可能涉及版权问题，这里仅提供框架代码
    #歌曲url
    if re.match(r'^\d{5,}$', url):
        id=url
    else:
        id=requests.get(f"https://wwy.浙江原神学院.com/search?keywords={url}&limit=1",headers=netease_headers).json()['result']['songs'][0]['id']
    song_download_url=requests.get(f"https://wwy.浙江原神学院.com/song/url/v1?id={id}&level=standard",headers=netease_headers).json()['data'][0]['url']
    return song_download_url

def live_handler(url):
    #直播url
    url_default=re.search(r'live.bilibili.com/(\d+)',url).group(1)
    room_id=requests.get(f"https://api.live.bilibili.com/room/v1/Room/get_info?room_id={url_default}",headers=bilibili_headers).json()['data']['room_id']
    live_url=requests.get(f"https://api.live.bilibili.com/room/v1/Room/playUrl?cid={room_id}",headers=bilibili_headers).json()['data']['durl'][0]['url']
    return live_url

@app.route('/')
def index():
    url = request.args.get('url')
    print(datetime.datetime.now())
    if url:
        if "bilibili.com/video/" in url:
            bv = get_bv_from_url(url)
            if bv:
                direct_url = get_video_direct_url(bv)
                if direct_url:
                    return redirect(direct_url)
                else:
                    return 'Failed to get video direct link', 500
            else:
                return 'Invalid Bilibili video URL', 400
        if "live.bilibili.com" in url:
            print(url)
            live_url=live_handler(url)
            if live_url:
                return redirect(live_url)
            else:
                return 'Failed to get live direct link', 500
        else:
            # 处理网易云音乐链接或搜索歌曲名
            print(url)
            download_url = netease_music_handler(url)
            if download_url:
                return redirect(download_url)
            else:
                return 'Failed to get music download link', 500

    else:
        return send_from_directory('static', 'no_video.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
