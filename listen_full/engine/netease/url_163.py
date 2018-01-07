# -*- coding:utf-8 -*-

import base64
import binascii
import hashlib
import json
import random
import string
from http import cookiejar
from urllib import request

import pyaes

# 歌曲加密算法, 基于https://github.com/yanunon/NeteaseCloudMusic脚本实现

modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b72' + \
          '5152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbd' + \
          'a92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe48' + \
          '75d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
nonce = '0CoJUm6Qyw8W8jud'
pubKey = '010001'

def _encrypted_id(id):
    magic = bytearray('3go8&$8*3*3h0k(2)2')
    song_id = bytearray(id)
    magic_len = len(magic)
    for i in range(len(song_id)):
        song_id[i] = song_id[i] ^ magic[i % magic_len]
    m = hashlib.md5(song_id)
    result = m.digest().encode('base64')[:-1]
    result = result.replace('/', '_')
    result = result.replace('+', '-')
    return result


def _create_secret_key(size):
    # randlist = map(lambda xx: (hex(ord(xx))[2:]), os.urandom(size))
    # randlist = map(lambda xx: (hex((ord(str(xx))))[2:]), os.urandom(size))
    # return (''.join(randlist))[0:16]
    return ''.join(random.sample(string.ascii_letters + string.digits, 16))


def _aes_encrypt(text, sec_key):
    # print('text is %s, sec_key is %s' %(text, sec_key))
    # pad = 16 - len(text) % 16
    #
    # print(type(pad))
    #
    #
    # text = text + pad * chr(pad)
    # print('ttt is', text)
    # encryptor = AES.new(sec_key, 2, '0102030405060708')
    # ciphertext = encryptor.encrypt(text)
    # ciphertext = base64.b64encode(ciphertext)
    # print('ciphertext is: ', ciphertext)
    # return ciphertext
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    # aes = pyaes.AESModeOfOperationCBC(sec_key, iv='0102030405060708')
    aes = pyaes.AESModeOfOperationCBC(sec_key, iv=bytes('0102030405060708', encoding='utf8'))
    ciphertext = ''
    while text != '':
        ciphertext += aes.encrypt(text[:16])
        text = text[16:]
    ciphertext = base64.b64encode(ciphertext)
    return ciphertext


def _rsa_encrypt(text, pub_key, modulus):
    text = text[::-1]
    # rs = int(text.encode('hex'), 16) ** int(pubKey, 16) % int(modulus, 16)
    # rs = int(binascii.b2a_hex(text.encode('utf-8')), 16) ** int(pubKey, 16) % int(modulus, 16)
    rs = int(binascii.hexlify(text.encode('utf-8')), 16) ** int(pubKey, 16) % int(modulus, 16)
    return format(rs, 'x').zfill(256)


def _encrypted_request(text):
    text = json.dumps(text)
    sec_key = _create_secret_key(16)
    print('text is: ', text)
    print('sec_key is: ', sec_key)
    enc_text = _aes_encrypt(_aes_encrypt(text, nonce), sec_key)
    enc_sec_key = _rsa_encrypt(sec_key, pubKey, modulus)
    data = {
        'params': enc_text,
        'encSecKey': enc_sec_key
    }
    return data


def h(
        url, v=None, progress=False, extra_headers={},
        post_handler=None, return_post=False):
    '''
    base http request
    progress: show progress information
    need_auth: need douban account login
    '''
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) ' + \
                 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86' + \
                 ' Safari/537.36'
    headers = {'User-Agent': user_agent}
    headers.update(extra_headers)

    cookie = cookiejar.CookieJar()
    cookie_support = request.HTTPCookieProcessor(cookie)
    opener = request.build_opener(cookie_support)
    req = request.Request(url=url, data=v, headers=extra_headers)
    response = opener.open(req)
    result = response.read().decode('utf-8')
    print('=====> ' % result)
    return result


def _ne_h(url, v=None):
    # http request
    extra_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'music.163.com',
        'Referer': 'http://music.163.com/search/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2)' +
                      ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome' +
                      '/33.0.1750.152 Safari/537.36'
    }
    return h(url, v=v, extra_headers=extra_headers)


def get_url_by_id(song_id):
    csrf = ''
    d = {
        "ids": [song_id],
        "br": 12800,
        "csrf_token": csrf
    }
    url = 'http://music.163.com/weapi/song/enhance/player/url?csrf_token='
    request = _encrypted_request(d)
    response = json.loads(_ne_h(url, request))
    return response['data'][0]['url']


if __name__ == '__main__':
    print(get_url_by_id(460316578))
