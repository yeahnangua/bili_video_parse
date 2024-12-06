import requests

head={
            'referer':'http://m.music.migu.cn',
            'proxy':'false',
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'
            }
url = 'http://m.music.migu.cn/migu/remoting/scr_search_tag?keyword={}&type={}&pgc={}&rows={}'.format("melody", 2,
                                                                                                     1, 1)
print(requests.get(url,headers=head,timeout=1).json())