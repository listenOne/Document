import html
import json
import urllib
from http import cookiejar
from urllib import request
from urllib.parse import quote

header_primary = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'i.y.qq.com',
    'Referer': 'http://y.qq.com/y/static/taoge/taoge_list.html?pgv_ref=qqmusic.y.topmenu',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'
}

# 获取token时的请求头
header_base = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN',
    'Connection': 'keep-alive',
    'Referer': 'y.qq.com',
    'Host': 'base.music.qq.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Listen1/1.2.2 Chrome/59.0.3071.115 Electron/1.8.1 Safari/537.36'
}


class QQ(object):
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
    def search(self, s):
        s = quote(s.encode("utf-8"))
        url = 'http://i.y.qq.com/s.music/fcgi-bin/search_for_qq_cp?g_tk=938407465&uin=0&format=jsonp&inCharset=utf-8&outCharset=utf-8&notice=0&platform=h5&needNewCode=1&w=%s' % s + '&zhidaqu=1&catZhida=1&t=0&flag=1&ie=utf-8&sem=1&aggr=0&perpage=20&n=20&p=1&remoteplace=txt.mqq.all&_=1459991037831&jsonpCallback=jsonp4'
        response = self._http_request(url)
        data = json.loads(response[len('jsonp4('):-len(')')])

        result = []
        for song in data['data']['song']['list']:
            result.append(self._convert_song(song))
        print('search=====> ', result)
        return result

    # # #
    # 歌手
    def get_artist(self, artist_id):
        url = 'http://i.y.qq.com/v8/fcg-bin/fcg_v8_singer_track_cp.fcg?platform=h5page&order=listen&begin=0&num=50&singermid=%s' % artist_id + '&g_tk=938407465&uin=0&format=jsonp&inCharset=utf-8&outCharset=utf-8&notice=0&platform=h5&needNewCode=1&from=h5&_=1459960621777&jsonpCallback=ssonglist1459960621772'
        response = self._http_request(url)
        response = str(response).replace(' ', '')
        data = json.loads(response[len('ssonglist1459960621772('):-len(')')])
        info = dict(
            cover_img_url=self._get_image_url(artist_id, img_type='artist'),
            title=data['data']['singer_name'],
            id='qqartist_' + artist_id)
        result = []
        for song in data['data']['list']:
            result.append(self._convert_song(song['musicData']))
        print('get_artist=====> ', result)
        return dict(tracks=result, info=info)

    # # #
    # 专辑
    def get_album(self, album_id):
        url = 'http://i.y.qq.com/v8/fcg-bin/fcg_v8_album_info_cp.fcg?platform=h5page&albummid=%s' % album_id + '&g_tk=938407465&uin=0&format=jsonp&inCharset=utf-8&outCharset=utf-8&notice=0&platform=h5&needNewCode=1&_=1459961045571&jsonpCallback=asonglist1459961045566'
        response = self._http_request(url)
        data = json.loads(response[len(' asonglist1459961045566('):-len(')')])
        info = dict(
            cover_img_url=self._get_image_url(album_id, img_type='album'),
            title=data['data']['name'],
            id='qqalbum_' + str(album_id))

        result = []
        for song in data['data']['list'] or []:
            result.append(self._convert_song(song))
        print('get_album=====> ', result)
        return dict(tracks=result, info=info)

    # # #
    # 精选歌单(所有歌单)
    def list_playlist(self):
        url = 'http://i.y.qq.com/splcloud/fcgi-bin/fcg_get_diss_by_tag.fcg?categoryId=10000000&sortId=1&sin=0&ein=29&format=jsonp&g_tk=5381&loginUin=0&hostUin=0&format=jsonp&inCharset=GB2312&outCharset=utf-8&notice=0&platform=yqq&jsonpCallback=MusicJsonCallback&needNewCode=0'
        response = self._http_request(url)
        data = json.loads(response[len('MusicJsonCallback('):-len(')')])

        result = []
        for l in data['data']['list']:
            d = dict(
                cover_img_url=l['imgurl'],
                title=html.unescape(l['dissname']),
                play_count=l['listennum'],
                list_id='qqplaylist_' + str(l['dissid']), )
            result.append(d)
        print('list_playlist=====> ', result)
        return result

    # # #
    # 精选歌单(具体歌单歌曲列表)
    def get_playlist(self, playlist_id):
        url = 'http://i.y.qq.com/qzone-music/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg?type=1&json=1&utf8=1&onlysong=0&jsonpCallback=jsonCallback&nosign=1&disstid=%s' % playlist_id + '&g_tk=5381&loginUin=0&hostUin=0&format=jsonp&inCharset=GB2312&outCharset=utf-8&notice=0&platform=yqq&jsonpCallback=jsonCallback&needNewCode=0'
        response = self._http_request(url)
        data = json.loads(response[len('jsonCallback('):-len(')')])
        info = dict(
            cover_img_url=data['cdlist'][0]['logo'],
            title=data['cdlist'][0]['dissname'],
            id='qqplaylist_' + playlist_id)
        result = []
        for song in data['cdlist'][0]['songlist']:
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
    def _get_qqtoken(self):
        token_url = 'http://base.music.qq.com/fcgi-bin/fcg_musicexpress.fcg?json=3&guid=780782017&g_tk=938407465&loginUin=0&hostUin=0&format=jsonp&inCharset=GB2312&outCharset=GB2312&notice=0&platform=yqq&jsonpCallback=jsonCallback&needNewCode=0'
        jc = self._http_request(token_url, extra_headers=header_base)[len("jsonCallback("):-len(");")]
        return json.loads(jc)["key"]

    def _get_image_url(self, qqimgid, img_type):
        if img_type == 'artist':
            category = 'mid_singer_300'
        elif img_type == 'album':
            category = 'mid_album_300'
        else:
            return None
        url = 'http://imgcache.qq.com/music/photo/%s/%s/%s/%s.jpg'
        image_url = url % (category, qqimgid[-2], qqimgid[-1], qqimgid)
        return image_url

    # 转成16进制[标准json]
    def _gen_url_params(self, d):
        for k, v in d.items():
            # d[k] = v.encode('utf-8')
            pass
        return urllib.parse.urlencode(d)

    def _convert_song(self, song):
        d = {
            'id': 'qqtrack_' + str(song['songmid']),
            'title': song['songname'],
            'artist': song['singer'][0]['name'],
            'artist_id': 'qqartist_' + str(song['singer'][0]['mid']),
            'album': song['albumname'],
            'album_id': 'qqalbum_' + str(song['albummid']),
            'img_url': self._get_image_url(song['albummid'], img_type='album'),
            'source': 'qq',
            'source_url': 'http://y.qq.com/#type=song&mid=' + str(song['songmid']) + '&tpl=yqq_song_detail',
        }
        params = self._gen_url_params(d)
        d['url'] = '/track_file?' + params
        return d

    # 歌曲链接
    # # #
    def get_url_by_id(self, qqsid):
        token = self._get_qqtoken()
        song_url = 'http://dl.stream.qqmusic.qq.com/C200%s' % qqsid + '.m4a?vkey=%s' % token + '&fromtag=0&guid=780782017'
        print('=====> ', song_url)

