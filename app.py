from flask import Flask, request, redirect, send_from_directory
import requests

app = Flask(__name__)

cookie="a"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.0.0.0',
    'Cookie': cookie,
    'platform':'html5',
    'referer':'https://www.bilibili.com'
}


# 解析Bilibili视频链接，提取BV号
def get_bv_from_url(url):
    print(url)
    if "bilibili.com/video/" in url:
        parts = url.split("/")
        for part in parts:
            if part.startswith("BV"):
                print(part)
                return part
    return None


# 使用Bilibili API获取视频直链
def get_video_direct_url(bv):
    # 获取cid
    pagelist_url = f"https://api.bilibili.com/x/player/pagelist?bvid={bv}"
    pagelist_response = requests.get(pagelist_url, headers=headers)
    if pagelist_response.status_code == 200:
        try:
            pagelist_data = pagelist_response.json()
            cid = pagelist_data['data'][0]['cid']
            print(cid)
        except (KeyError, IndexError):
            print("Error parsing pagelist response:", pagelist_response.text)
            return None
    else:
        print("Pagelist request failed:", pagelist_response.status_code)
        return None

    # 获取视频直链
    playurl_url = f"https://api.bilibili.com/x/player/wbi/playurl?bvid={bv}&cid={cid}"
    playurl_response = requests.get(playurl_url, headers=headers)
    if playurl_response.status_code == 200:
        try:
            playurl_data = playurl_response.json()
            video_url = playurl_data['data']['durl'][0]['url']
            print(video_url)
            return video_url
        except (KeyError, IndexError):
            print("Error parsing playurl response:", playurl_response.text)
            return None
    else:
        print("Playurl request failed:", playurl_response.status_code)
        return None


@app.route('/')
def index():
    video_url = request.args.get('url')
    if video_url:
        bv = get_bv_from_url(video_url)
        if bv:
            direct_url = get_video_direct_url(bv)
            if direct_url:
                print("success")
                print("\n\n\n")
                return redirect(direct_url)
            else:
                print("Failed to get video direct link")
                print("\n\n\n")
                return 'Failed to get video direct link', 500
        else:
            print("Invalid Bilibili video URL")
            print("\n\n\n")
            return 'Invalid Bilibili video URL', 400
    else:
        print("No video URL provided")
        print("\n\n\n")
        return send_from_directory('static', 'no_video.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

