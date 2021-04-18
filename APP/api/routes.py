from flask import Blueprint
from flask_restful import Resource, Api, reqparse, abort, request
from api import api
from api.models import *
from flask import send_file, jsonify
class Init(Resource):
    def get(self):
        x = Conver()
        db.session.add(x)
        db.session.commit()
        return jsonify({'sender_id': str(x.sender_id)})
class Conversation(Resource):
    def get(self):
        pass
    def post(self):
        args = request.json #get args
        # print (self.status_code)
        response = process_request(args)
        return jsonify(response)        
api.add_resource(Init, '/apis/init')
api.add_resource(Conversation, '/apis/conver')