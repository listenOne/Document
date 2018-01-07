# 网易云音乐榜单
import json
import re

import requests

# 热门榜单接口
top_list_all = {
    0: ['云音乐新歌榜', '/discover/toplist?id=3779629'],
    1: ['云音乐热歌榜', '/discover/toplist?id=3778678'],
    2: ['网易原创歌曲榜', '/discover/toplist?id=2884035'],
    3: ['云音乐飙升榜', '/discover/toplist?id=19723756'],
    4: ['云音乐电音榜', '/discover/toplist?id=10520166'],
    5: ['UK排行榜周榜', '/discover/toplist?id=180106'],
    6: ['美国Billboard周榜', '/discover/toplist?id=60198'],
    7: ['KTV嗨榜', '/discover/toplist?id=21845217'],
    8: ['iTunes榜', '/discover/toplist?id=11641012'],
    9: ['Hit FM Top榜', '/discover/toplist?id=120001'],
    10: ['日本Oricon周榜', '/discover/toplist?id=60131'],
    11: ['韩国Melon排行榜周榜', '/discover/toplist?id=3733003'],
    12: ['韩国Mnet排行榜周榜', '/discover/toplist?id=60255'],
    13: ['韩国Melon原声周榜', '/discover/toplist?id=46772709'],
    14: ['中国TOP排行榜(港台榜)', '/discover/toplist?id=112504'],
    15: ['中国TOP排行榜(内地榜)', '/discover/toplist?id=64016'],
    16: ['香港电台中文歌曲龙虎榜', '/discover/toplist?id=10169002'],
    17: ['华语金曲榜', '/discover/toplist?id=4395559'],
    18: ['中国嘻哈榜', '/discover/toplist?id=1899724'],
    19: ['法国 NRJ EuroHot 30周榜', '/discover/toplist?id=27135204'],
    20: ['台湾Hito排行榜', '/discover/toplist?id=112463'],
    21: ['Beatport全球电子舞曲榜', '/discover/toplist?id=3812895']
}


class NetEase(object):
    def __init__(self):
        self.session = requests.Session()
        self.time_out = 10
        self.header = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'music.163.com',
            'Referer': 'http://music.163.com/search/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36'
        }

    def _raw_request(self, action, query=None, method='POST', urlencoded=None, callback=None, timeout=None):

        if method == 'GET':
            url = action if query is None else action + '?' + query
            connection = self.session.get(url, headers=self.header, timeout=self.time_out)

        elif method == 'POST':
            connection = self.session.post(action, data=query, headers=self.header, timeout=self.time_out)

        connection.encoding = 'UTF-8'
        return connection.text

    def _http_request(self, action, query=None, method='POST', urlencoded=None, callback=None, timeout=None):
        connection = json.loads(self._raw_request(action, query, method, urlencoded, callback, timeout))
        return connection

    # *-* 搜索[支持歌词]
    # type--> 单曲(1) | 歌手(100) | 专辑(10) | 歌单(1000) | 用户(1002)
    def search(self, s, type=1, offset=0, total='true', limit=60):
        action = 'http://music.163.com/api/search/get'
        query = {'s': s, 'type': type, 'offset': offset, 'total': total, 'limit': limit}
        return self._http_request(action, query)

    # *-1 新碟上架
    def new_albums(self, offset=0, limit=50):
        action = 'http://music.163.com/api/album/new?area=ALL&offset={}&total=true&limit={}'.format(offset, limit)
        try:
            data = self._http_request(action, method='GET')
            return data['albums']
        except requests.exceptions.RequestException as e:
            return []

    # *-2 精选歌碟
    def selected_albums(self, category='全部', order='hot', offset=0, limit=50):
        action = 'http://music.163.com/api/playlist/list?cat={}&order={}&offset={}&total={}&limit={}'.format(category, order, offset, 'true' if offset else 'false', limit)
        try:
            data = self._http_request(action, method='GET')
            return data['playlists']
        except requests.exceptions.RequestException as e:
            return []

    # *-3 热门榜单
    def top_song_list(self, idx=0, offset=0, limit=100):
        action = 'http://music.163.com' + top_list_all[idx][1]

        try:
            connection = requests.get(action, headers=self.header, timeout=self.time_out)
            connection.encoding = 'UTF-8'
            song_list_ids = re.findall(r'/song\?id=(\d+)', connection.text)
            if not song_list_ids:
                return []
            song_list_ids = _unique(song_list_ids)
            return self.songs_url(song_list_ids)
        except requests.exceptions.RequestException as e:
            return []

    # *-3-1 热门榜单歌曲列表 song_ids --> songs_url
    def songs_url(self, song_list_ids, offset=0):
        tmp_ids = song_list_ids[offset:]
        tmp_ids = tmp_ids[0:100]
        tmp_ids = list(map(str, tmp_ids))
        action = 'http://music.163.com/api/song/detail?ids=[{}]'.format(','.join(tmp_ids))
        try:
            data = self._http_request(action, method='GET')
            # the order of data['songs'] is no longer the same as tmpids, so just make the order back
            data['songs'].sort(key=lambda song: tmp_ids.index(str(song['id'])))
            return data['songs']
        except requests.exceptions.RequestException as e:
            return []

    # *-1 热门歌手
    def top_artists(self, offset=0, limit=100):
        action = 'http://music.163.com/api/artist/top?offset={}&total=false&limit={}'.format(offset, limit)
        try:
            data = self._http_request(action, method='GET')
            return data['artists']
        except requests.exceptions.RequestException as e:
            return []

    # *-2 歌手单曲
    def artist_songs(self, artist_id):
        action = 'http://music.163.com/api/artist/{}'.format(artist_id)
        try:
            data = self._http_request(action, method='GET')
            return data['hotSongs']
        except requests.exceptions.RequestException as e:
            return []

    # *-3 歌手专辑 artist_id --> artist_album
    def artist_albums(self, artist_id, offset=0, limit=50):
        action = 'http://music.163.com/api/artist/albums/{}?offset={}&limit={}'.format(artist_id, offset, limit)
        try:
            data = self._http_request(action, method='GET')
            return data['hotAlbums']
        except requests.exceptions.RequestException as e:
            return []

    # *-3-1 专辑歌单 album_id --> album_song_ids
    def album_song_ids(self, album_id):
        action = 'http://music.163.com/api/album/{}'.format(album_id)
        try:
            data = self._http_request(action, method='GET')
            return data['album']['songs']
        except requests.exceptions.RequestException as e:
            return []

    # 歌词 | 翻译 | 评论
    # ABOUT_SPECIFIC_SONG lyric
    def song_lyric(self, song_id):
        action = 'http://music.163.com/api/song/lyric?os=osx&id={}&lv=-1&kv=-1&tv=-1'.format(song_id)
        try:
            data = self._http_request(action, method='GET')
            if 'lrc' in data and data['lrc']['lyric'] is not None:
                lyric_info = data['lrc']['lyric']
            else:
                lyric_info = '未找到歌词'
            return lyric_info
        except requests.exceptions.RequestException as e:
            return []

    # ABOUT_SPECIFIC_SONG tlyric
    def song_tlyric(self, song_id):
        action = 'http://music.163.com/api/song/lyric?os=osx&id={}&lv=-1&kv=-1&tv=-1'.format(song_id)
        try:
            data = self._http_request(action, method='GET')
            if 'tlyric' in data and data['tlyric'].get('lyric') is not None:
                lyric_info = data['tlyric']['lyric'][1:]
            else:
                lyric_info = '未找到歌词翻译'
            return lyric_info
        except requests.exceptions.RequestException as e:
            return []

    # ABOUT_SPECIFIC_SONG song_comments
    def song_comments(self, music_id, offset=0, total='false', limit=100):
        action = 'http://music.163.com/api/v1/resource/comments/R_SO_4_{}/?rid=R_SO_4_{}&\offset={}&total={}&limit={}'.format(music_id, music_id, offset, total, limit)
        try:
            comments = self._http_request(action, method='GET')
            return comments
        except requests.exceptions.RequestException as e:
            return []


#
# #
# # #
# # # #
# 方法支持
# # # #
# # #
# #
#
# 去重
def _unique(arr):
    result = list(set(arr))
    result.sort(key=arr.index)
    return result

