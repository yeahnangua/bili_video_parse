import datetime
import requests
from flask import Flask, request, redirect, send_from_directory
import re
import logging

app = Flask(__name__)

logging.basicConfig(filename='app.log', level=logging.DEBUG)

# Bilibili 配置
bilibili_cookie = ""  # 请在这里填入你的 Bilibili Cookie
bilibili_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.0.0.0',
    'Cookie': bilibili_cookie,
    'platform': 'html5',
    'referer': 'https://www.bilibili.com'
}

# 网易云音乐配置
wwy_cookie=""
netease_headers = {
    'Cookie': bilibili_cookie,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}
migu_head={
            'referer':'http://m.music.migu.cn',
            'proxy':'true',
            'Cookie':"migu_cookie_id=8102c5b3-74c9-4092-8682-61e4cbef3153-n41709986285789; mg_uem_user_id_9fbe6599400e43a4a58700a822fd57f8=27106c8a-acc5-47aa-af4d-95d4570712b4; cookieId=iPWZd2ObI1NT7NzaqVORmtegzcqhph71709986342312; idmpauth=true@passport.migu.cn; migu_music_status=true; migu_music_uid=91181714096; migu_music_avatar=; migu_music_nickname=%E5%92%AA%E5%92%95%E9%9F%B3%E4%B9%90%E7%94%A8%E6%88%B7; migu_music_level=0; migu_music_credit_level=1; migu_music_platinum=0; migu_music_msisdn=nCSbdmuLOmYoBiolJwqzkQ%3D%3D; migu_music_email=; migu_music_passid=609049552082860128; migu_music_sid=s%3A0V4rf7nZtA_ro-VcIu9-JqvD4bsiRjLS.lbOBKMsN9FAmmawcHKFHDPvqLiZdbXYr1qGDQ45e8KE; player_stop_open=0; playlist_adding=1; addplaylist_has=1; audioplayer_new=1; add_play_now=1; audioplayer_open=1; playlist_change=0; audioplayer_exist=1; WT_FPC=id=2b8d1e7b5f77a5e95011709986286725:lv=1710040781466:ss=1710040754751",
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'
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
    # 歌曲url
    url = 'https://m.music.migu.cn/migu/remoting/scr_search_tag?keyword={}&type={}&pgc={}&rows={}'.format(url, 2,

                                                                                                         1, 1)
    proxies = {
        "http": "http://118.25.84.151:8888",
        "https": "http://118.25.84.151:8888",
    }
    req = requests.get(url, headers=migu_head, timeout=5,proxies=proxies)
    print(req)
    app.logger.info(req)
    print(req.json())
    url=req.json()["musics"][0]["mp3"]
    print(url)
    app.logger.info(url)
    mp3_index = url.find(".mp3")

    # 截取从开始到 ".mp3"（包含）为止的所有内容
    if mp3_index != -1:
        trimmed_url = url[:mp3_index + 4]  # 加4是因为".mp3"有4个字符，我们想包含这四个字符
    else:
        trimmed_url = url  # 如果找不到".mp3"，则返回原始字符串

    return trimmed_url




def live_handler(url):
    # 直播url
    url_default = re.search(r'live.bilibili.com/(\d+)', url).group(1)
    room_id = requests.get(f"https://api.live.bilibili.com/room/v1/Room/get_info?room_id={url_default}",
                           headers=bilibili_headers).json()['data']['room_id']
    live_url = requests.get(f"https://api.live.bilibili.com/room/v1/Room/playUrl?cid={room_id}&platform=h5",
                            headers=bilibili_headers).json()['data']['durl'][0]['url']
    print(live_url)
    app.logger.info(live_url)
    return live_url


@app.route('/')
def index():
    url = request.args.get('url')
    print(datetime.datetime.now())
    app.logger.info(datetime.datetime.now())
    if url:
        if "bilibili.com/video/" in url:
            bv = get_bv_from_url(url)
            if bv:
                direct_url = get_video_direct_url(bv)
                if direct_url:
                    print("success")
                    app.logger.info("success")
                    print("\n\n\n")
                    app.logger.info("\n\n\n")
                    return redirect(direct_url)
                else:
                    print("Failed to get video direct link")
                    app.logger.info("Failed to get video direct link")
                    print("\n\n\n")
                    app.logger.info("\n\n\n")
                    return 'Failed to get video direct link', 500
            else:
                print("Invalid Bilibili video URL")
                app.logger.info("Invalid Bilibili video URL")
                print("\n\n\n")
                app.logger.info("\n\n\n")
                return 'Invalid Bilibili video URL', 400
        if "live.bilibili.com" in url:
            print(url)
            app.logger.info(url)
            live_url = live_handler(url)
            if live_url:
                print("success")
                app.logger.info("success")
                print("\n\n\n")
                app.logger.info("\n\n\n")
                return redirect(live_url)
            else:
                print("Failed to get LIVE direct link")
                app.logger.info("Failed to get LIVE direct link")
                print("\n\n\n")
                app.logger.info("\n\n\n")
                return 'Failed to get live direct link', 500
        else:
            # 处理网易云音乐链接或搜索歌曲名
            print(url)
            app.logger.info(url)
            download_url = netease_music_handler(url)
            if download_url:
                print("success")
                app.logger.info("success")
                print("\n\n\n")
                app.logger.info("\n\n\n")
                return redirect(download_url)
            else:
                return 'Failed to get music download link', 500

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
