from listen_full.engine.netease.api_netease import NetEase
from listen_full.engine.netease.netease_flac_downloader import NeteaseDownloader
from listen_full.engine.qq.api_qq import QQ
from listen_full.engine.xiami.api_xiami import Xiami

import os


def netease():
    o = NetEase()
    with open('files/temp_netease.txt', 'w', encoding='utf-8') as f:
        f.write('搜索歌手:')
        f.write(str(o.search('刘德华')))
        f.write('\r\n')

        f.write('搜索歌名:')
        f.write(str(o.search('眼泪的错觉')))
        f.write('\r\n')

        f.write('搜索专辑:')
        f.write(str(o.search('十一月的萧邦')))
        f.write('\r\n')

        f.write('搜索歌词:')
        f.write(str(o.search('为什么剩我一人孤独守候')))
        f.write('\r\n')

        f.write('搜索用户:')
        f.write(str(o.search('王夜寒寒寒', type=1002)))
        f.write('\r\n')

        # 热门
        f.write('新碟上架:')
        f.write(str(o.new_albums()))
        f.write('\r\n')

        f.write('精选歌单:')
        f.write(str(o.selected_albums()))
        f.write('\r\n')

        f.write('热门榜单:')
        f.write(str(o.top_song_list()))
        f.write('\r\n')

        f.write('热门歌手:')
        f.write(str(o.top_artists()))
        f.write('\r\n')

        f.write('歌手单曲:')
        f.write(str(o.artist_songs(3691)))
        f.write('\r\n')

        f.write('歌手专辑:')
        f.write(str(o.artist_albums(3691)))
        f.write('\r\n')

        f.write('专辑歌单:')
        f.write(str(o.album_song_ids(10930)))
        f.write('\r\n')

        # 歌曲相关
        f.write('歌词:')
        f.write(str(o.song_lyric(460316578)))
        f.write('\r\n')

        f.write('歌词翻译:')
        f.write(str(o.song_tlyric(460316578)))
        f.write('\r\n')

        f.write('歌曲评论:')
        f.write(str(o.song_comments(460316578)))
        f.write('\r\n')


def netease_flac():
    CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
    NeteaseDownloader(CURRENT_PATH, '/files/netease_flac').downloader('http://music.163.com/#/playlist?id=2039098272')


def qq():
    o = QQ()
    with open('files/temp_qq.txt', 'w', encoding='utf8') as f:
        f.write('搜索歌手:')
        f.write(str(o.search('刘德华')))
        f.write('\r\n')

        f.write('搜索歌名:')
        f.write(str(o.search('眼泪的错觉')))
        f.write('\r\n')

        f.write('搜索专辑:')
        f.write(str(o.search('十一月的萧邦')))
        f.write('\r\n')

        # 歌手
        f.write('歌手:')
        f.write(str(o.get_artist('0025NhlN2yWrP4')))
        f.write('\r\n')

        f.write('专辑:')
        f.write(str(o.get_album('000I5jJB3blWeN')))
        f.write('\r\n')

        f.write('list_playlist:')
        f.write(str(o.list_playlist()))
        f.write('\r\n')

        f.write('get_playlist:')
        f.write(str(o.get_playlist('3591175213')))
        f.write('\r\n')

        f.write('get_url_by_id:')
        f.write(str(o.get_url_by_id('0041WNvp0LQJBI')))
        f.write('\r\n')


def xiami():
    o = Xiami()
    with open('files/temp_xiami.txt', 'w', encoding='utf8') as f:
        f.write('搜索歌手:')
        f.write(str(o.search('刘德华')))
        f.write('\r\n')

        f.write('搜索歌名:')
        f.write(str(o.search('眼泪的错觉')))
        f.write('\r\n')

        f.write('搜索专辑:')
        f.write(str(o.search('十一月的萧邦')))
        f.write('\r\n')

        # 歌手
        f.write('歌手:')
        f.write(str(o.get_artist('1260')))
        f.write('\r\n')

        f.write('专辑:')
        f.write(str(o.get_album('6643')))
        f.write('\r\n')

        f.write('list_playlist:')
        f.write(str(o.list_playlist()))
        f.write('\r\n')

        f.write('get_playlist:')
        f.write(str(o.get_playlist('361475277')))
        f.write('\r\n')

        f.write('get_url_by_id:')
        f.write(str(o.get_url_by_id('1776156051')))
        f.write('\r\n')


if __name__ == '__main__':
    pass
    # netease()
    # qq()
    # xiami()
    netease_flac()
