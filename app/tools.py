# -*- coding: utf-8 -*-
import datetime, base64


def str2time(_str):
    if _str is None or _str == "":
        return
    return datetime.datetime.strptime(_str, "%Y年%m月%d日")


def str2img(_str, base_url="", _id=""):
    img = base64.b64decode(_str)
    if _id is None:
        _id = "temp"
    url = base_url + _id + ".jpg"
    with open(url, "wb") as f:
        f.write(img)
    return url


def replace2none(dic):
    for keys in dic:

        if isinstance(dic[keys], list):
            for dic1 in dic[keys]:
                for key in dic1:
                    if dic1[key] == "":
                        dic1[key] = None

        if isinstance(dic[keys], dict):
            for key in dic[keys]:
                for d in dic[keys]:
                    if dic[keys][d] == "":
                        dic[keys][d] = None

    return dic
