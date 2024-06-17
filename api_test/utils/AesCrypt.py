# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: AesSypto.py

# @Software: PyCharm
from Crypto.Cipher import AES
import base64

from Crypto.Util.Padding import pad


class AesCrypt:
    """
    aes加密封装
    """
    def __init__(self, model, iv, encode_, key='abcdefghijklmnop'):
        self.encrypt_text = ''
        self.decrypt_text = ''
        self.encode_ = encode_
        self.model = {'ECB': AES.MODE_ECB, 'CBC': AES.MODE_CBC}[model]
        self.key = self.add_16(key)
        if model == 'ECB':
            self.aes = AES.new(self.key, self.model)  # 创建一个aes对象
        elif model == 'CBC':
            self.aes = AES.new(self.key, self.model, iv)  # 创建一个aes对象

        # 这里的密钥长度必须是16、24或32，目前16位的就够用了

    def add_16(self, par):
        par = par.encode(self.encode_)
        while len(par) % 16 != 0:
            par += b'\x00'
        return par

    # 加密
    def aesencrypt(self, text):
        text = pad(text.encode('utf-8'), AES.block_size, style='pkcs7')
        self.encrypt_text = self.aes.encrypt(text)
        return base64.encodebytes(self.encrypt_text).decode().strip()

    # 解密
    def aesdecrypt(self, text):
        text = base64.decodebytes(text.encode(self.encode_))
        self.decrypt_text = self.aes.decrypt(text)
        return self.decrypt_text.decode(self.encode_).strip('\0').strip("\n").strip().replace("\x06", "").replace("\x05", "").replace("\x07", "")


if __name__ == '__main__':
    pr = AesCrypt('ECB', '', 'utf-8', 'abcdefghijklmnop')
    pr1 = AesCrypt("ECB", "", "utf-8")
    en_text = pr.aesencrypt('jmdevcd')
    print('密文:', en_text)
    print('明文:', pr1.aesdecrypt("r1ThEqAQfffooVzZFGoG2gIjg=="))
