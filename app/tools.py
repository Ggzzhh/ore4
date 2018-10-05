# -*- coding: utf-8 -*-
import datetime, base64
from collections import Iterable

from xpinyin import Pinyin

from .const import FIELDS


def filter_field(per_list, fields):
    new_per_list = []
    if isinstance(per_list, Iterable) and isinstance(fields, Iterable):
        for per in per_list:
            L = []
            data = per.to_json()
            _id = data.get('id')
            if _id is None:
                continue
            for field in fields:
                temp = data.get(FIELDS.get(field))
                if temp is None:
                    temp = ' '
                L.append(temp)
            new_per_list.append({'data': L, 'id': _id})
    return new_per_list


def str2pinyin(_str):
    p = Pinyin()
    return p.get_initials(_str, '')


def str2time(_str):
    if _str is None or _str == "" or _str == "None":
        return
    _str = str(_str)
    if '年' in _str:
        result = datetime.datetime.strptime(_str, "%Y年%m月%d日")
    elif '-' in _str:
        result = datetime.datetime.strptime(_str, "%Y-%m-%d")
    else:
        result = None
    return result


def time2str(time):
    if time is None:
        return
    return time.strftime("%Y") + "-" + time.strftime("%m") + "-" + \
           time.strftime("%d")


def str2img(_str, base_url="", _id=""):
    if _str[-4:] == ".jpg":
        return _str
    img = base64.b64decode(_str)
    if _id is None:
        _id = "temp"
    url = base_url + _id + ".jpg"
    with open("app/" + url, "wb") as f:
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


def calculate_age(born):
    today = datetime.datetime.today()
    if born:
        try:
            birthday = born.replace(year=today.year)
        except ValueError:
            birthday = born.replace(year=today.year, day=born.day - 1)
        if birthday > today:
            return today.year - born.year - 1
        else:
            return today.year - born.year