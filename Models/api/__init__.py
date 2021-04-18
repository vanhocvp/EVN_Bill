from flask import Flask
from flask_restful import Resource, Api, reqparse, abort
from flask_marshmallow import Marshmallow
# from config import Config
from models import Models
# def create_app():
# print (x)   
app = Flask(__name__)
# app.config.from_object(Config)
models = Models()
# model = Models()
# graph = Graph() 
api = Api(app)
# from api import models
from api import routes
