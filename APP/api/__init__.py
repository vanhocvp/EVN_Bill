from flask import Flask
from flask_restful import Resource, Api, reqparse, abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from process.process_request import Proces_Request 
# from graph.graph import Graph
# from model.models import Models
from config import Config
# def create_app():
# print (x)   
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
ma = Marshmallow(app)
# model = Models()
# graph = Graph() 
api = Api(app)
process = Proces_Request()
from api import models
from api import routes