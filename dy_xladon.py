import base64
import hashlib
import random
import struct

unpad = lambda s: s[: -ord(s[len(s) - 1:])]
pad = lambda s: s + (chr((16 - (len(s) % 16))).encode() * (16 - (len(s) % 16)))


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


def encrypt(xk: str, key: list):
    # 1662603888 应该为x-khronos
    # 固定1662603888-1588093228-1128
    salt = (xk + "-1588093228-1128").encode()
    salt = pad(salt)
    res = []
    for j in range(0, len(salt), 16):
        data1 = struct.unpack("<Q", bytes(salt[j: j + 8]))[0]
        data0 = struct.unpack("<Q", bytes(salt[j + 8: j + 16]))[0]

        # data0 = 0x30383835312d3838
        # data1 = 0x3833303632363631

        for i in range(0, len(key) - 8, 8):
            data2 = struct.unpack("<Q", bytes(key[i: i + 8]))[0]
            A = ror4(data0, 8) & 0xFFFFFFFFFFFFFFFF
            B = (data1 + A) & 0xFFFFFFFFFFFFFFFF
            C = data2 ^ B
            D = ror4(data1, 0x3D)
            E = C ^ D
            data0 = C
            data1 = E

        l = struct.pack("<Q", E)
        r = struct.pack("<Q", C)
        res += list(l) + list(r)
    return res


def gen_key(data: str):
    # d24755c1700bfc7129a8df55cde5b611
    data = data.encode()
    d_list = []
    for i in range(0, len(data), 8):
        t = struct.unpack("<Q", bytes(data[i: i + 8]))[0]
        d_list.append(t)
    res_list = []
    res_list += data[:8]
    for i in range(34):
        x9 = d_list[0]
        x8 = d_list[1]
        x8 = (x8 & 0xFF) << 56 | (x8 >> 8)
        x8 = (x8 + x9) & 0xFFFFFFFFFFFFFFFF
        x8 = x8 ^ i
        tmp = x8
        x8 = x8 ^ ror4(x9, 61)
        d_list[0] = x8
        d_list[1] = d_list[2]
        d_list[2] = d_list[3]
        d_list[3] = tmp
        t = struct.pack("<Q", x8)
        res_list += t
    return res_list


def get_xladon(xk):
    rdm = random.randint(0x10000000, 0xFFFFFFFF)
    r = struct.pack("<I", rdm)
    md5_res = hashlib.md5(r + "1128".encode()).hexdigest()
    key = gen_key(md5_res)
    res = encrypt(str(xk), key)
    return base64.b64encode(r + bytes(res)).decode()
