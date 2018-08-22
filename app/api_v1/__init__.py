# -*- coding: utf-8 -*-
from flask import Blueprint

api_v1 = Blueprint('v1', __name__)

from . import views