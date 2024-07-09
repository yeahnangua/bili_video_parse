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

# 网易云音乐配置
wwy_cookie="NMTID=00Ow57IsMYQgJ-KJEU5l36BmyganKsAAAGN7QjnmA; _iuqxldmzr_=32; WM_NI=SZWpOMHbUV8U2cNDPBA2Fw5ThC90iPQHUH8eIYzivIxRy3oVCt8xafROVJE11CvasY7DXkJhwHMumWLEGG71Q5FmWmDKAUu0BP8tX1bO145YQJAPpoe2NxVd3O0Mh2a5MXU%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee97d65da191bda2d459ae928ba7d15e878e9f87c87cf5b2fea6dc64979298a6c12af0fea7c3b92a91869991ce478cbe9bb7bb5ff2bd82a5d34a83ee8a98b860ac9df7d1ec5c93989ba9bb6f8b87b68af543bc8eb7d4ee5e81acf899e46e92919aabc83bf39dba82f253f59c988cc964b5988396f05d909b89a8b63b93eb8a8ed66788958fb6f83c8290f895db3ba291ffd5b85393968fb1f365a7ee8299d570f19100aeeb3aa3eb83b9d837e2a3; WEVNSM=1.0.0; WNMCID=pfnlcp.1709078841847.01.0; sDeviceId=YD-IfLxJUQkNKlAQxAEQEKRtrynQZhUzziK; ntes_utid=tid._.r99HRLxzQ19FQ0RAUQaVsvyiQYlViyDL._.0; WM_TID=Du729UFpv%2F9BEBQBFReQ9rynVckFBn%2Fr; __snaker__id=7ZgVGgD6BfN4I7as; __csrf=7c9c1c87d93c7aa22956ef8390e6ef6d; MUSIC_U=006759CEC55561C620A7BE13EBDE141C2E68E87C7D612E464136DFBD36FBF2D4B8D3F52E471FECAA6A8143DD4940B8F9026A58BB6695E31851057A64746B0943F97BC31F3E393F32A5F2EEF215AE274CFA6291B2D9A4B44ED4E2EB469BCEBBBA4267D0CA0CA4255B555200BE61472D7DF4D04043467819E81CA35D25680A0DC1D1E324F59766CF8DC4F30B050BBEAB0A64335EA7123D849D3733851E8A2E040018B376D3704794651AA55C1E2EB1CA3927CEA7F5D8CC527343945836A08570E75BA64C587C6057DC7E710FDBDEB87C440BAB25C72D3959DE2CDEBA105B9BC148ED4886B2AF088BCC9B2FE8698E31CDECC9BF9484C206999985EFEBE83DB74BE3AA453C542860621DB18028D4B77CB60B2814414FDA8FD7E9C6AE10A48332AE0A559E3D054B837F4D8F26E8188860DC97F5F580E03C283FE8E4C928C66DA7511E0C9CFB07ABEF211E72510747A2ECA408A2740A1933B1256A894DCAB63A791A7170; ntes_kaola_ad=1; JSESSIONID-WYYY=8zJ%2FB3XVscuIQEiE6MjsTC%5C0NKqtBfRiO3Yog79nVtFJOvApPAo8rm78SfzuZzrSJj2nEJJVin5Zko9jThmVOXv%2BVA2UDfKz4ndX25gM3n42WX%5C53JZQH1B%2B2QgXu35Osppa7ch29IM%2FrWejYXYE7s7QmnVSsTEBRN5zeoOcdYOiqPur%3A1709084120168; gdxidpyhxdE=DvEdd8m9O%2Bk2oLVe%2FUZXmKPpjvloJmIAnWzBfpG4JwDXmcA71PuLU8IiUR37IEKefAT12EBUcNa5xvUd%2BpTxwCUPeViDRyyyVaqmJ%5C7iQ8pi%2Bn8iKsngkNAQqXQmHJrKqDUHXNCPEGntmn%2B7ia0mnDUOiSPv6c9TfCxmeUC%2FaR%2FP2xeA%3A1709083965184"
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
