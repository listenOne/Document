import json
import urllib
from http import cookiejar
from urllib import request
from urllib.parse import quote, unquote

header_primary = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'api.xiami.com',
    'Referer': 'http://m.xiami.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'
}

# 获取歌曲链接时的请求头
header_base = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'www.xiami.com',
    'Referer': 'http://m.xiami.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Listen1/1.2.2 Chrome/59.0.3071.115 Electron/1.8.1 Safari/537.36'
}


class Xiami(object):
    def _http_request(self, url, extra_headers=header_primary):
        cookie = cookiejar.CookieJar()
        cookie_support = request.HTTPCookieProcessor(cookie)
        opener = request.build_opener(cookie_support)
        req = request.Request(url=url, headers=extra_headers)
        response = opener.open(req)
        result = response.read().decode('utf-8')
        return result

    # # #
    # *-* 搜索[不支持歌词]
    def search(self, keyword):
        keyword = quote(keyword.encode("utf8"))
        search_url = 'http://api.xiami.com/web?v=2.0&app_key=1&key=%s' + keyword + '&page=1&limit=50&callback=jsonp154&r=search/songs'
        response = self._http_request(search_url)
        data = json.loads(response[len('jsonp154('):-len(')')])

        result = []
        for song in data['data']["songs"]:
            result.append(self._convert_song(song))
        print('search=====> ', result)
        return result

    # # #
    # 歌手
    def get_artist(self, artist_id):
        url = 'http://api.xiami.com/web?v=2.0&app_key=1&id=%s' % str(artist_id) + '&page=1&limit=20&_ksTS=1459931285956_216&callback=jsonp217&r=artist/detail'
        response = self._http_request(url)
        data = json.loads(response[len('jsonp217('):-len(')')])
        artist_name = data['data']['artist_name']
        info = dict(
            cover_img_url=self._retina_url(data['data']['logo']),
            title=artist_name,
            id='xmartist_' + artist_id)

        url = 'http://api.xiami.com/web?v=2.0&app_key=1&id=%s' % str(artist_id) + '&page=1&limit=20&_ksTS=1459931285956_216&callback=jsonp217&r=artist/hot-songs'
        response = self._http_request(url)
        data = json.loads(response[len('jsonp217('):-len(')')])
        result = []
        for song in data['data']:
            d = {
                'id': 'xmtrack_' + str(song['song_id']),
                'title': song['song_name'],
                'artist': artist_name,
                'artist_id': 'xmartist_' + artist_id,
                'album': '',
                'album_id': '',
                'img_url': '',
                'source': 'xiami',
                'source_url': 'http://www.xiami.com/song/' + str(song['song_id']),
            }
            params = self._gen_url_params(d)
            d['url'] = '/track_file?' + params
            result.append(d)
        print('get_artist=====> ', result)
        return dict(tracks=result, info=info)

    # # #
    # 专辑
    def get_album(self, album_id):
        url = 'http://api.xiami.com/web?v=2.0&app_key=1&id=%s' % str(album_id) + '&page=1&limit=20&_ksTS=1459931285956_216&callback=jsonp217&r=album/detail'
        response = self._http_request(url)
        data = json.loads(response[len('jsonp217('):-len(')')])
        artist_name = data['data']['artist_name']
        info = dict(
            cover_img_url=self._retina_url(data['data']['album_logo']),
            title=data['data']['album_name'],
            id='xmalbum_' + album_id)
        result = []
        for song in data['data']['songs']:
            d = {
                'id': 'xmtrack_' + str(song['song_id']),
                'title': song['song_name'],
                'artist': artist_name,
                'artist_id': 'xmartist_' + str(song['artist_id']),
                'album': song['album_name'],
                'album_id': 'xmalbum_' + str(song['album_id']),
                'img_url': song['album_logo'],
                'source': 'xiami',
                'source_url': 'http://www.xiami.com/song/' + str(song['song_id']),
            }
            params = self._gen_url_params(d)
            d['url'] = '/track_file?' + params
            result.append(d)
        print('get_album=====> ', result)
        return dict(tracks=result, info=info)

    # # #
    # 精选歌单
    def list_playlist(self):
        url = 'http://api.xiami.com/web?v=2.0&app_key=1&_ksTS=1459927525542_91&page=1&limit=60&callback=jsonp92&r=collect/recommend'
        response = self._http_request(url)
        data = json.loads(response[len('jsonp92('):-len(')')])
        result = []
        for l in data['data']:
            d = dict(
                cover_img_url=l['logo'],
                title=l['collect_name'],
                play_count=0,
                list_id='xmplaylist_' + str(l['list_id']), )
            result.append(d)
        print('list_playlist=====> ', result)
        return result

    # # #
    # 具体精选歌单
    def get_playlist(self, playlist_id):
        url = 'http://api.xiami.com/web?v=2.0&app_key=1&id=%s' % playlist_id + '&_ksTS=1459928471147_121&callback=jsonp122&r=collect/detail'
        response = self._http_request(url)
        data = json.loads(response[len('jsonp122('):-len(')')])

        info = dict(
            cover_img_url=self._retina_url(data['data']['logo']),
            title=data['data']['collect_name'],
            id='xmplaylist_' + playlist_id)
        result = []
        for song in data['data']['songs']:
            result.append(self._convert_song(song))
        print('get_playlist=====> ', result)
        return dict(tracks=result, info=info)

    #
    # #
    # # #
    # # # #
    # 方法支持
    # # # #
    # # #
    # #
    #
    def _caesar(self, location):
        num = int(location[0])
        avg_len = int(len(location[1:]) / num)
        remainder = int(len(location[1:]) % num)
        result = [
            location[i * (avg_len + 1) + 1: (i + 1) * (avg_len + 1) + 1]
            for i in range(remainder)]
        result.extend(
            [
                location[(avg_len + 1) * remainder:]
                [i * avg_len + 1: (i + 1) * avg_len + 1]
                for i in range(num - remainder)])
        url = unquote(
            ''.join([
                ''.join([result[j][i] for j in range(num)])
                for i in range(avg_len)
            ]) +
            ''.join([result[r][-1] for r in range(remainder)])).replace('^', '0')
        return url

    # 转成16进制[标准json]
    def _gen_url_params(self, d):
        for k, v in d.items():
            # d[k] = unicode(v).encode('utf-8')
            # d[k] = v.encode('utf-8')
            pass
        return urllib.parse.urlencode(d)

    def _convert_song(self, song):
        d = {
            'id': 'xmtrack_' + str(song['song_id']),
            'title': song['song_name'],
            'artist': song['artist_name'],
            'artist_id': 'xmartist_' + str(song['artist_id']),
            'album': song['album_name'],
            'album_id': 'xmalbum_' + str(song['album_id']),
            'source': 'xiami',
            'source_url': 'http://www.xiami.com/song/' + str(song['song_id']),
        }
        if 'logo' in song:
            d['img_url'] = song['logo']
        else:
            d['img_url'] = ''
        params = self._gen_url_params(d)
        d['url'] = '/track_file?' + params
        return d

    def _retina_url(self, s):
        return s[:-6] + s[-4:]

    # 歌曲链接
    # # #
    def get_url_by_id(self, song_id):
        url = 'http://www.xiami.com/song/playlist/id/%s' % song_id + '/object_name/default/object_id/0/cat/json'
        response = self._http_request(url, extra_headers=header_base)
        secret = json.loads(response)['data']['trackList'][0]['location']
        song_url = self._caesar(secret)
        print('=====> ', song_url)
        return song_url

