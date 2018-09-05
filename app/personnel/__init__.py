# -*- coding: utf-8 -*-
from flask import Blueprint

per = Blueprint('per', __name__)

from . import views
