# -*- coding: cp936 -*-

try:
    from Crypto.Cipher import AES,\
         ARC2,Blowfish,CAST,DES3
    from Crypto.Hash import HMAC,MD2,MD4,MD5,\
         RIPEMD,SHA,SHA224,SHA256,SHA384,SHA512
except ImportError:
    raise NoCryptoModule('Crypto is not installed')

import os

import chacha20
import salsa20

__all__=['Cipher']

_CryptoModule=['aes','arc2','blowfish','cast','des3','chacha20','salsa20']

_CryptoMethod={
    'aes-128-cfb': (16, 16, AES.MODE_CFB, AES),
    'aes-192-cfb': (24, 16, AES.MODE_CFB, AES),
    'aes-256-cfb': (32, 16, AES.MODE_CFB, AES),
    'bf-cfb': (16, 8, Blowfish.MODE_CFB, Blowfish),
    'cast-cfb': (16, 8, CAST.MODE_CFB, CAST),
    'des3-cfb': (24, 8, DES3.MODE_CFB, DES3),
    'rc2-cfb': (16, 8, ARC2.MODE_CFB, ARC2),
    'chacha20': (32, 8, None, chacha20),
    'salsa20': (32, 8, None, salsa20)
    }

class CryptoModuleError(Exception):pass

class Cipher(object):
    def __init__(self,key,method):
        method=method.lower()
        if not method in _CryptoMethod:
            raise CryptoModuleError('Wrong crypto module')
        keysize=_CryptoMethod[method][0]
        
        self.key=self.sha256(key)[:keysize]
        
        self.type=_CryptoMethod[method][-1]
        self.mode=_CryptoMethod[method][-2]
        self.iv_length=_CryptoMethod[method][-3]

    def md5(self,data):
        h=MD5.new()
        h.update(data)
        return h.hexdigest()

    def sha1(self,data):
        h=SHA.new()
        h.update(data)
        return h.hexdigest()

    def sha224(self,data):
        h=SHA224.new()
        h.update(data)
        return h.hexdigest()

    def sha256(self,data):
        h=SHA256.new()
        h.update(data)
        return h.hexdigest()

    def sha384(self,data):
        h=SHA384.new()
        h.update(data)
        return h.hexdigest()

    def sha512(self,data):
        h=SHA512.new()
        h.update(data)
        return h.hexdigest()

    def hmac(self,data):
        h=HMAC.new(self.key)
        h.update(data)
        return h.hexdigest()

    def get_iv_length(self):
        return self.iv_length

    def encrypt(self,data):
        iv=os.urandom(self.iv_length)
        obj=self.type.new(self.key,self.mode,iv)
        return iv + obj.encrypt(data)

    def decrypt(self,data):
        iv=data[:self.iv_length]
        data=data[self.iv_length:]
        obj=self.type.new(self.key,self.mode,iv)
        return obj.decrypt(data)

if __name__ == "__main__":
    #print c.md5('你好')
    #print c.md5(text)
    #print c.sha1(text)
    #print c.sha224(text)
    #print c.sha256(text)
    #print c.sha384(text)
    #print c.sha512(text)
    #print c.hmac(text)
    for i in _CryptoMethod:
        m=i
        print '='*20,' ',m,':','\n'
        c=Cipher('pass',m)
        #text=os.urandom(32*1024)
        #text=''
        text='$'*60
        t=c.encrypt(text)
        print len(t),t
        x=c.decrypt(t)
        print len(x),x
