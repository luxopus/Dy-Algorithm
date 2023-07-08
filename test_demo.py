import hashlib
import re
import time
from pprint import pprint

import requests


def str_middle(buff, w1, w2):
    """
    取出文本中间
    :param buff: 源文本
    :param w1: 左边关键词
    :param w2: 右边关键词
    :return: 左右关键词中间内容
    """
    # 清除换行符,请取消下一行注释
    try:
        # buff = buff.replace('\n', '')
        buff = buff.replace('\r', '')
        pat = re.compile(w1 + '(.*?)' + w2, re.S)
        result = pat.findall(buff)
        if len(result) > 0:
            return result[0]
        else:
            return ''
    except:
        return ""


def get_xa(url, data=""):
    headers = {}
    device_id = str_middle(url, "device_id=", "&")
    if data:
        headers['x-ss-stub'] = hashlib.md5(data.encode()).hexdigest().upper()

    xgorgon_result = get_xgorgon(url=url, data=data)
    xKhronos = xgorgon_result['X-Khronos']
    if data:
        x_argus = get_xargus(url, xKhronos, deviceid=device_id, stub=hashlib.md5(data.encode()).hexdigest().upper())
    else:
        x_argus = get_xargus(url, xKhronos, deviceid=device_id)

    x_ladon = get_xladon(xKhronos)
    headers["X-Ladon"] = x_ladon
    headers["X-Argus"] = x_argus
    headers["X-Khronos"] = xKhronos
    headers["X-Gorgon"] = xgorgon_result['X-Gorgon']
    headers['X-SS-REQ-TICKET'] = xgorgon_result['_rticket']
    # pprint(headers)
    return headers


def make_encrypt(url, data, device_info):
    device_id = device_info["device_id"]
    install_id = device_info["install_id"]

    url_prefix, url_suffix = url.split('?')
    url_suffix_map = {i.split("=")[0]: i.split("=")[-1] for i in url_suffix.split("&")}
    url_suffix_map['ts'] = int(time.time())
    url_suffix_map['iid'] = install_id
    url_suffix_map['device_id'] = device_id
    url = url_prefix + '?' + '&'.join([f"{i}={url_suffix_map[i]}" for i in url_suffix_map])

    # print(device_id)

    cookie = f'install_id={install_id};'
    headers = {
        "Cookie": cookie,
        'x-tt-request-tag': 't=1;n=0',
        'activity_now_client': '1667205703111',
        'x-vc-bdturing-sdk-version': '3.1.0.cn',
        'sdk-version': '2',
        'passport-sdk-version': '20374',
        'user-agent': 'okhttp/3.10.0.1',
        # 'user-agent': 'com.ss.android.ugc.aweme/220501 (Linux; U; Android 9; en_US; Pixel 3 XL; Build/PQ3A.190801.002;tt-ok/3.12.13.1)',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    if data:
        headers['x-ss-stub'] = hashlib.md5(data.encode()).hexdigest().upper()

    xgorgon_result = get_xgorgon(url=url, data=data)
    # print(xgorgon_result)
    xKhronos = xgorgon_result['X-Khronos']
    if data:
        x_argus = get_xargus(url, xKhronos, deviceid=device_id, stub=hashlib.md5(data.encode()).hexdigest().upper())
    else:
        x_argus = get_xargus(url, xKhronos, deviceid=device_id)

    x_ladon = get_xladon(xKhronos)

    headers["X-Ladon"] = x_ladon
    headers["X-Argus"] = x_argus
    headers["X-khronos"] = xKhronos
    headers["X-Gorgon"] = xgorgon_result['X-Gorgon']
    headers["x-ss-req-ticket"] = xgorgon_result['_rticket']

    pprint(headers)

    return url, headers


def process_url(url, data=""):
    device_info = {
        "device_brand": "OnePlus",
        "device_type": "HD1910",
        "cdid": "337a00be-b51e-4d41-9547-8922c60bede4",
        "device_id": "2441373511860247",
        "install_id": "3954301513285182",
        "openudid": "6bcc667822444571",
        "uuid": "867124531559524",
        "os_api": "25",
        "os_version": "7.1.2",
    }
    url, headers = make_encrypt(url, data, device_info)
    proxy = '127.0.0.1:7890'
    proxies = {
        'http': 'http://' + proxy,
        'https': 'https://' + proxy,
    }
    proxies = None
    if data:
        response = requests.post(url, headers=headers, data=data, proxies=proxies)
    else:
        response = requests.get(url, headers=headers, proxies=proxies)
    # print(url)
    # print(response.text[:200])
    print(response.status_code)
    print(response.text)


def main_test():
    # 用户视频列表
    url = "https://api5-core-c-lq.amemv.com/aweme/v1/aweme/post/?publish_video_strategy_type=2&source=0&user_avatar_shrink=96_96&video_cover_shrink=248_330&max_cursor=0&sec_user_id=MS4wLjABAAAAWfe7Ghc6TeBpPMiaUI_MRud2PXAou7I2JitcSlGHXKeXW7Yhj1-_3fErUHqBV7xp&count=20&show_live_replay_strategy=1&is_order_flow=0&page_from=2&location_permission=1&familiar_collects=0&locate_item_id=7186718859389390140&post_serial_strategy=0&_rticket=1673337821109&mcc_mnc=46000&ts=1673337821&need_personal_recommend=1&md=0&ac=wifi&aid=1128&appTheme=light&app_name=aweme&app_type=normal&cdid=d9d5cfa7-a9be-4979-bdc1-37585fcb79c6&channel=shenmasem_ls_dy_224&cpu_support64=true&device_brand=OPPO&device_id=157953230906349&device_platform=android&device_type=PCRT00&dpi=240&host_abi=armeabi-v7a&iid=3373749869747975&is_android_pad=0&is_guest_mode=0&language=zh&manifest_version_code=230301&minor_status=0&os=android&os_api=25&os_version=7.1.2&package=com.ss.android.ugc.aweme&resolution=800*1280&ssmix=a&update_version_code=23309900&version_code=230300&version_name=23.3.0"
    process_url(url, "")


if __name__ == '__main__':
    main_test()
