# -*- coding: utf-8 -*-

from . import api_v1


@api_v1.route('/')
def test():
    return "欢迎来到英雄联盟"
