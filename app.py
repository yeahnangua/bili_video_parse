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

music_cookie = "NMTID=00Oxnp1BwPud1jmtEVRr-DOo2s_JVwAAAGPYO0usA; _iuqxldmzr_=32; WEVNSM=1.0.0; WNMCID=wlvprf.1715318109656.01.0; WM_TID=p0QbvrSCLWlBQEAVAFeBvj0AvfNPJ0C%2B; JSESSIONID-WYYY=CpFReUh1Oad8JJH36z5OmgGTa89twur9bWy67X%2FAnCD5dEkaEAw3Tx6SoOoFcjMNtXary0%2BEhIrslBUU3algJ4hEAWyA%2FVE84eN0sbz2Dc0PeCF3HCvWnSytwZ2FdrBT%5CK3j%2Bvd%2FqdW4B61wAGPGRCQgXDKMQTK4dmXVWXwiGMmUhsQg%3A1721310571639; WM_NI=vQn9QdFKdYAGGz71ODvydxCsBgt4zGqAAJGwcSLfck4CAGN%2Fx81ULvHdqVyANUrtYicJwsiZ6kviyXvIOoEkgCozMUEas2kSjc33aD0kiMkI7kibklOno9mDICe5QorRVU0%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eea2ec62b69da18bb43c8d9a8ea6d85a928e9fadc74fa28ef7b7cc69ab8baf91f22af0fea7c3b92ab68fa2dad4708695acbac44d85a6f9d2ce50b6a7ac99c27982b9bcd5f94db39f8fabc67da18d8487e261f89d8fa8cd25bce8ffb6cf7e8cbcbfb7fc4b8e8bbe95dc63a196b994ec52f6b5ba8afc54b6978190c861a59da19bd05f87bfbdd3ea59aabdfdd4e450f4b5a7aeea43f5b5a783ea688db2a1daf0508b9dabd6d465b28e9ab6b337e2a3; __snaker__id=OoCX1mn9cxEUhUcH; __csrf=74c73378c37b6d5780f57fd4bee3e0d5; MUSIC_U=00132078E105D3085EB6586E0DE8A4BAE2674D7F6570F5137B6AE48FB5E09963AB85D15F5512549244F869CAA11DD27880153879D665F003E5DB701AC8F6CFC27D15C232070655979E29E006ECEC7E548AE447451C9FC6A786B1ACB201EF64690DA2C9548BFBABDD6B1FE2F0FF9B08159847FBD852765AA96A4BB554FBE6D91DD3981868448B450040AD0F7EA464DF6235378F9FC8F2BD88B7947D54011A48F8AC060F165F11509BC8C38A3A85471AB0EB281A97C15284D43F0C9393A192A7AB2227B0A106FDD1F572E5BC754AFE11EB6612BE3433509B0D108C3529712BAFC67FC37D3AB392362C9B07E12E5C57B6B04B62C9FF75E84927F95A01D84D9C7DA3DE7A2741F59503C0A5A743FA6615E356A04398052EE3342113F281C1998EA3EE29EC5763A3D2F4FFE98811B709FAE407C7; gdxidpyhxdE=o7GW0IPNC45%5CYbVSCxq59RJkuZ0lEtJAYnJpMLQnwbC5S%2FeeQs8OHCVeqOeJqOrafftiA%2BYDMsIY60sgJunAVe3B%2F8yZ41EsvNEvEsz%2FzdKPL%2F13Vi3J9puLsCG0ktICJSNO8sk%2BSLi4dDr9COc0Cuk9nIbZQe9OiBh0WHZmAr%5CxWR2f%3A1721310517158"
music_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.0.0.0',
    'Cookie': music_cookie,
    'referer': 'https://music.163.com/'
}


# 解析 Bilibili 视频链接，提取 BV 号
def get_bv_from_url(url):
    if "bilibili.com/video/" in url:
        parts = url.split("/")
        for part in parts:
            if part.startswith("BV"):
                return part
    return None
def get_music_from_url(url):
    return url[6:]


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

def music_hander(url):
    music_id = get_music_from_url(url)
    print(music_id)
    req = requests.get(f"https://music.tongxuewen.me/mv/url?id={music_id}",headers=music_headers)
    print(req)
    print(req.json())
    music_url = req.json()['data'][0]['url']
    print(music_url)
    return music_url



@app.route('/')
def index():
    url = request.args.get('url')
    print(url)
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
        if "mv?id" in url:
            print(url+"123123")
            app.logger.info(url)
            music_url = music_hander(url)
            print(music_url)
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
