import datetime
import requests
from flask import Flask, request, redirect, send_from_directory
import re
import logging

app = Flask(__name__)

logging.basicConfig(filename='app.log', level=logging.DEBUG)

# Bilibili 配置
bilibili_cookie = "buvid3=AEFFCF15-C2E9-793B-491D-008BF0C90F7181101infoc; b_nut=1708509581; i-wanna-go-back=-1; b_ut=7; _uuid=A45D2A41-E510A-7825-6D71-583425B31DB260284infoc; buvid4=61A85774-CD3B-69A8-C2BC-924829AB4E1582108-024022109-wOq%2F528XLFNoA5mFMDlDvw%3D%3D; buvid_fp=2cf80278a68c3a68b477341ad2413cc4; header_theme_version=CLOSE; DedeUserID=305501959; DedeUserID__ckMd5=4be9a350f49fb1fc; rpdid=|(YYYYYRmuY0J'u~|)l|m)u); enable_web_push=ENABLE; iflogin_when_web_push=1; fingerprint=48be66a35f4e388b3068541117bcbd81; CURRENT_FNVAL=4048; LIVE_BUVID=AUTO8517086005952981; PVID=3; home_feed_column=5; browser_resolution=1482-706; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDkxMjgxODksImlhdCI6MTcwODg2ODkyOSwicGx0IjotMX0.nXakkRyuJ6CmUHwKVMq8B_oK2IkAm5CLNaE3SqVD3Go; bili_ticket_expires=1709128129; SESSDATA=59cbf0df%2C1724557449%2C8be7e%2A22CjDmTFA_A9qpH15TbD83W33LB9hnLq-MS_4XGl5eTQ0o3desbTUFp7qMxFGtrFlVTDESVlJWV193dlBpNVlSZG96LTIzYXZFbkQ3SzVOYUFyeFBPYXE0ME9XUTlSdVphUl9MU0oxYUR0WmUwLWVqVUZWdWxXYlpFNnBwLWFwU0tjOTJLUHFpMFRnIIEC; bili_jct=5e8563e6de2034002aebe8fec18a76e9; sid=6vsco01x; CURRENT_QUALITY=120; bp_video_offset_305501959=903138786663202832"  # 请在这里填入你的 Bilibili Cookie
bilibili_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.0.0.0',
    'Cookie': bilibili_cookie,
    'platform': 'html5',
    'referer': 'https://www.bilibili.com'
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
