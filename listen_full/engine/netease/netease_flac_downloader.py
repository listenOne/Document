import json
import os
import re
import urllib.error
import urllib.request
import requests


# 请支持原作者谢谢 --> https://github.com/YongHaoWu/NeteaseCloudMusicFlac

# 本方法可下载网易云任意歌单的所有无损音乐[flac格式][无损歌单从这里找 --> http://music.163.com/#]

# 注意 --> 海外由于版权问题无法下载歌曲解决办法[修改DNS配置] --> https://github.com/YongHaoWu/NeteaseCloudMusicFlac/issues/1

class NeteaseDownloader(object):
    def __init__(self, root_dir, song_dir):
        self.minimum_size = 10
        self.root_dir = root_dir
        self.song_dir = song_dir
        # self.song_dir = r'D:\catface\IDEA\Python\src\listen_full\engine\netease\flac_musics'

    def downloader(self, url):
        print("fetching msg from %s \n" % url)
        url = re.sub("#/", "", url).strip()
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36'})
        contents = r.text
        res = r'<ul class="f-hide">(.*?)</ul>'
        mm = re.findall(res, contents, re.S | re.M)
        CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
        if mm:
            contents = mm[0]
        else:
            print('Can not fetch information form URL. Please make sure the URL is right.\n')
            os._exit(0)

        res = r'<li><a .*?>(.*?)</a></li>'
        mm = re.findall(res, contents, re.S | re.M)

        for value in mm:
            url = 'http://sug.music.baidu.com/info/suggestion'
            payload = {'word': value, 'version': '2', 'from': '0'}
            value = value.replace('\\xa0', ' ')  # windows cmd 的编码问题
            print('song name: \t%s' % value)

            r = requests.get(url, params=payload)
            contents = r.text
            d = json.loads(contents, encoding="utf-8")
            if d is not None and 'data' not in d:
                continue
            songid = d["data"]["song"][0]["songid"]
            print("song id: \t%s" % songid)

            url = "http://music.baidu.com/data/music/fmlink"
            payload = {'songIds': songid, 'type': 'flac'}
            r = requests.get(url, params=payload)
            contents = r.text
            d = json.loads(contents, encoding="utf-8")
            if ('data' not in d) or d['data'] == '':
                continue
            songlink = d["data"]["songList"][0]["songLink"]
            # print("find songlink: ")
            if len(songlink) < 10:
                print("\tdo not have flac\n")
                continue
            print("song link: \t%s" % songlink)

            if not os.path.exists(self.song_dir):
                os.makedirs(self.song_dir)

            songname = d["data"]["songList"][0]["songName"]
            artistName = d["data"]["songList"][0]["artistName"]
            print("%s/%s/%s-%s.flac" % (self.root_dir, self.song_dir, songname, artistName))
            filename = ("%s/%s/%s-%s.flac" % (self.root_dir, self.song_dir, songname, artistName))

            f = urllib.request.urlopen(songlink)
            headers = requests.head(songlink).headers
            if 'Content-Length' in headers:
                size = round(int(headers['Content-Length']) / (1024 ** 2), 2)
            else:
                continue

            # Download unfinished Flacs again.
            if not os.path.isfile(filename) or os.path.getsize(filename) < self.minimum_size:  # Delete useless flacs
                print("%s is downloading now ......\n\n" % songname)
                if size >= self.minimum_size:
                    with open(filename, "wb") as code:
                        code.write(f.read())
                else:
                    print("the size of %s (%r Mb) is less than 10 Mb, skipping" %
                          (filename, size))
            else:
                print("%s is already downloaded. Finding next song...\n\n" % songname)

        print("\n================================================================\n")
        print("Download finish!\nSongs' directory is %s/songs_dir" % os.getcwd())