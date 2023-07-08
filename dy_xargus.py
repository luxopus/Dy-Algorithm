import base64
import hashlib
import random
import struct

from Crypto.Cipher import AES
from pysmx.SM3 import SM3  # pip install snowland-smx

from douyin import argus_protobuf_pb2

unpad = lambda s: s[: -ord(s[len(s) - 1:])]
pad = lambda s: s + (chr((16 - (len(s) % 16))).encode() * (16 - (len(s) % 16)))


def calcProtobuf3(d):
    high = (d << 1) & 0xFFFFFFFF
    return high ^ (d >> 31)


def calc_sm3(data):
    sm3 = SM3()
    sm3.update(data)
    return sm3.digest()


def ror4(num, k):
    result = ""
    while num < 0:
        num += 0x10000000000000000
    if len(hex(num)[2:]) > 16:
        num = int(hex(num)[-8:], 16)

    lst = bin(num)[2:]
    for i in range(0, 64):
        if i < len(lst):
            result = result + lst[i]
        else:
            result = "0" + result
    return int(result[-k:] + result[:-k], 2)


def enc_ts(ts):
    high = 0
    r3 = (ts << 1) & 0xFFFFFFFF
    low = r3 ^ (high >> 31)
    r3 = (high << 1) & 0xFFFFFFFF
    r0 = r3 | (ts >> 31)
    t = r0 ^ (high >> 31)  # 高位
    return low | (t << 32)


def check_log(temp_list, label=""):
    tmp = []
    for item in temp_list:
        tmp.append(hex(item))
    print(label, "长度:{}  内容:{}\n".format(len(tmp), tmp))


def RBIT(num):
    result = ""
    tmp_string = bin(num)[2:]
    while len(tmp_string) < 8:
        tmp_string = "0" + tmp_string
    for i in range(0, 8):
        result = result + tmp_string[7 - i]
    return int(result, 2)


def hex_string(num):
    tmp_string = hex(num)[2:]
    if len(tmp_string) < 2:
        tmp_string = "0" + tmp_string
    return tmp_string


def reverse(num):
    tmp_string = hex_string(num)
    return int(tmp_string[1:] + tmp_string[:1], 16)


def aes_encrypt(ciphertext, key, iv):
    text = ciphertext
    text = pad(text)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    de_text = cipher.encrypt(text)
    return de_text


def aes_decrypt(ciphertext, key, iv):
    real_bytes = ciphertext
    cipher = AES.new(key, AES.MODE_CBC, iv)
    content = cipher.decrypt(real_bytes)
    return unpad(content)


def bfi(rd, rn, lsb, width):
    ls = 0xFFFFFFFF >> (32 - width)
    rn = (rn & ls) << lsb
    ls = ~(ls << lsb)
    rd = rd & ls
    rd = rd | rn
    return rd


def get_xargus(url, xkhronos, deviceid="", stub=""):
    xa = Xargus(url[url.index("?") + 1:], int(xkhronos), deviceid, stub)
    return xa.mainEncrypt()


class Xargus:
    def __init__(self, data, khronos, device="", stub=""):
        self._data = data
        self._stub = stub
        self._argusVersion = 0x4020100
        self._appversion = "15.7.0"
        self._unknown8 = "v04.02.01-ml-android"
        self._device_id = device
        self._khronos = khronos
        self._unknown16 = "AbEP0QSeJStUszOoH-i5-Q7nE"
        self._signKey1 = [
            0x8E,
            0xBD,
            0xFA,
            0x38,
            0x06,
            0xEC,
            0xC5,
            0xCE,
            0xE7,
            0x94,
            0x23,
            0xE6,
            0x02,
            0x9E,
            0xD8,
            0x25,
        ]
        self._signKey2 = [
            0x40,
            0xBC,
            0x22,
            0x18,
            0xBB,
            0x7E,
            0xAE,
            0xF7,
            0x1C,
            0xB6,
            0x91,
            0xF7,
            0xAA,
            0x8A,
            0xA2,
            0xF5,
        ]
        self._aesKey = bytes(hashlib.md5(bytes(self._signKey1)).digest())
        self._aesIv = bytes(hashlib.md5(bytes(self._signKey2)).digest())
        self._rdm = random.randint(0x10000000, 0xFFFFFFFF)
        # self._rdm = 0x37076aa5
        self._apd = []

    def _encryptRandom(self, key):
        A = 0
        T = 0
        for i in range(0, len(key), 2):
            B = key[i] ^ A
            C = (T >> 0x3) & 0xFFFFFFFF
            D = C ^ B
            E = D ^ T
            F = (E >> 0x5) & 0xFFFFFFFF
            G = (E << 0xB) & 0xFFFFFFFF
            H = key[i + 1] | G
            I = F ^ H
            J = I ^ E
            T = ~J & 0xFFFFFFFF
            # A = (T << 7) & 0xFFFFFFFF
            return T

    def _gen_key(self):
        data = (
                self._signKey1
                + self._signKey2
                + list(struct.pack("<I", self._rdm))
                + self._signKey1
                + self._signKey2
        )
        sm3 = SM3()
        sm3.update(bytes(data))
        res = sm3.hexdigest()

        res_list = []
        for i in range(0, len(res), 2):
            res_list.append(int(res[i: i + 2], 16))
        sm3_list = []
        for i in range(0, len(res_list), 4):
            c = struct.unpack("<I", bytes(res_list[i: i + 4]))
            sm3_list.append(c[0])
        res_list = res_list[:8]
        for i in range(0x47):
            t = i % 0x3E
            off = (0x20 - t) & 0xFF
            A = (0x3DC94C3A << off) & 0xFFFFFFFF
            B = ((0x46D678B >> t) & 0xFFFFFFFF) | A
            off_1 = t - 0x20
            if off_1 >= 0:
                B = 0x3DC94C3A >> off_1
            H = (sm3_list[6] >> 3) & 0xFFFFFFFF
            H |= (sm3_list[7] << 29) & 0xFFFFFFFF
            # print(hex(H), hex(sm3_list[2]))
            C = H ^ sm3_list[2]
            # bfi = (B & 1) | 0xFFFFFFFD
            bfi_v = bfi(B, 0x7FFFFFFE, 1, 0x1F)
            D = bfi_v ^ sm3_list[0] ^ C
            H = (sm3_list[7] >> 3) & 0xFFFFFFFF
            H |= (sm3_list[6] << 29) & 0xFFFFFFFF
            # print("H==========", hex(H))
            E = H ^ sm3_list[3]
            # 根据E判断是否进位
            if E & 1:
                B = (C >> 1) | 0x80000000
            else:
                B = C >> 1
            H = (C << 31) & 0xFFFFFFFF
            F = (E >> 1) | H
            G = F ^ sm3_list[1] ^ E
            A = ~G & 0xFFFFFFFF
            F = D ^ B
            for j in range(6):
                sm3_list[j] = sm3_list[j + 2]
            sm3_list[6] = F
            sm3_list[7] = A
            for j in range(2):
                for d in list(struct.pack("<I", sm3_list[j])):
                    res_list.append(d)
        return res_list

    def _gen_protobuf(self):

        argus = argus_protobuf_pb2.Argus()
        argus.header = 1077940818
        argus.version = 2
        # argus.random = calcProtobuf3(random.randint(0x10000000, 0x8FFFFFFF))
        argus.random = 422182720
        argus.stub = "1128"
        argus.deviceId = self._device_id
        argus.unknown6 = "1588093228"
        argus.appVersion = self._appversion
        argus.unknown8 = self._unknown8
        argus.argusVersion = calcProtobuf3(self._argusVersion)
        argus.unknown10 = b"\x00\x01\x00\x00\x00\x00\x00\x00"
        argus.khronosOne = enc_ts(self._khronos)

        if self._stub == "":
            sm3_data = (
                b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            )
        else:
            sm3_data = self._stub.encode()
        stubSm3 = calc_sm3(sm3_data)
        urlSm3 = calc_sm3(self._data)

        self._apd.append(stubSm3[0])
        self._apd.append(urlSm3[0])
        argus.sm3One = stubSm3[:6]
        argus.sm3Two = urlSm3[:6]

        unknownStruct15 = argus_protobuf_pb2.UnknownStruct15()
        unknownStruct15.unknown1 = 0
        unknownStruct15.unknown2 = 0
        unknownStruct15.unknown3 = 0
        argus.unknown15.CopyFrom(unknownStruct15)

        # argus.unknown16 = self._unknown16
        argus.khronosTwo = enc_ts(self._khronos)
        # argus.unknown18 = b'\xE2\x94\x54\xF0\xE2\xD5\xC8\xC3\xB1\x31\x6F\x89\xB9\xC3\xFA\x5E'
        # argus.unknown19 = b'\x66\x21\xDA\xE6\xEC\x54\x76\x48\x32\x91\xE4\xDE\x40\xA8\x86\xB7\x32\xA3\xC5\x0E\xA2\x58\x6A\x97\x7C\x58\x82\xB0\x88\x0A\xED\x29'
        argus.unknown20 = "none"
        argus.unknown21 = "738"
        return argus.SerializeToString()

    def encrypt(self, proto, key):
        sm3_list = []
        for i in range(0, len(key), 4):
            c = struct.unpack("<I", bytes(key[i: i + 4]))
            sm3_list.append(c[0])

        for i in range(len(sm3_list)):
            t = i % 4
            AA = (proto[3 - t] >> 0x18) | ((proto[(2 + t) % 4] << 0x08) & 0xFFFFFFFF)
            BB = ((proto[(2 + t) % 4] << 0x1) & 0xFFFFFFFF) | (proto[3 - t] >> 0x1F)
            CC = AA & BB
            DD = proto[t] ^ CC
            EE = (proto[3 - t] >> 0x1E) | ((proto[(2 + t) % 4] << 0x02) & 0xFFFFFFFF)
            proto[t] = sm3_list[i] ^ DD ^ EE
        res_list = []
        for i in range(4):
            res_list += struct.pack("<I", proto[i])
        return res_list

    def decrypt(self, proto, key):
        sm3_list = []
        for i in range(0, len(key), 4):
            c = struct.unpack("<I", bytes(key[i: i + 4]))
            sm3_list.append(c[0])
        i = len(sm3_list) - 1
        while i >= 0:
            t = i % 4
            AA = (proto[3 - t] >> 0x18) | ((proto[(2 + t) % 4] << 0x08) & 0xFFFFFFFF)
            BB = ((proto[(2 + t) % 4] << 0x1) & 0xFFFFFFFF) | (proto[3 - t] >> 0x1F)
            CC = AA & BB
            DD = proto[t] ^ CC
            EE = (proto[3 - t] >> 0x1E) | ((proto[(2 + t) % 4] << 0x02) & 0xFFFFFFFF)
            proto[t] = sm3_list[i] ^ DD ^ EE
            i -= 1
        res_list = []
        for i in range(4):
            res_list += struct.pack("<I", proto[i])
        return res_list

    def _eor_data(self, key, data):
        rdm_list = self._encryptRandom(key)
        rdm_list = struct.pack(">I", rdm_list)
        for i in range(len(data)):
            data[i] ^= rdm_list[i % 4]
        return data

    def mainEncrypt(self):
        res = []
        enc_key = self._gen_key()
        self._proto = pad(self._gen_protobuf())

        for i in range(0, len(self._proto), 16):
            data = []
            for j in range(i, i + 16, 4):
                c = struct.unpack("<I", bytes(self._proto[j: j + 4]))
                data.append(c[0])
            res += self.encrypt(data, enc_key)
        random_arr = list(struct.pack("<I", self._rdm))
        key = random_arr[2:4]
        b64_header = random_arr[0:2]
        # 拼接eor数据
        res = res[::-1]
        res += [0x0, 0x1, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0][::-1]
        res = self._eor_data(key, res)
        res += key
        headers = [
            0x35,  # 固定
            random.randint(0x10, 0xFF),
            random.randint(0x10, 0xFF),
            random.randint(0x10, 0xFF),
            random.randint(0x10, 0xFF),  # 随机
            0x00,
            # self._apd[0] & 0x3f, self._apd[1] & 0x3f,         # 0x2F, 0x05, 好像是某个值
            self._apd[0] & 0x3F,
            0x02,  # 0x2F, 0x05, 好像是某个值 0x0f 和protobuf10 有关
            0x18,
        ]
        headers += res

        res = aes_encrypt(bytes(headers), self._aesKey, self._aesIv)
        content = bytes(b64_header) + res
        return base64.b64encode(content).decode()
