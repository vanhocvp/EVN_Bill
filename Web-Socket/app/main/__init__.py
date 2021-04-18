from flask import Blueprint
from configparser import ConfigParser, RawConfigParser
from flask import current_app
main = Blueprint('main', __name__)
config_object = ConfigParser()
config_object.read("config.ini")
api = config_object["URL_API"]
from . import routes, events
