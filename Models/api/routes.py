# from flask import Blueprint
from flask_restful import Resource, Api, reqparse, abort, request
from api import *
# from api.models import *
from flask import send_file, jsonify
class Init(Resource):
    def get(self):
        pass
        # x = Conver()
        # db.session.add(x)
        # db.session.commit()
        # return jsonify({'sender_id': str(x.sender_id)})
class Intent(Resource):
    def get(self):
        pass
    def post(self):
        args = request.json #get args
        # print (self.status_code)
        message = args['message']
        response = models.get_intent(message)
        return jsonify(response)      
class NER(Resource):
    def get(self):
        pass
    def post(self):
        args = request.json #get args
        # print (self.status_code)
        message = args['message']
        response = models.get_ne(message)
        return jsonify(response)    
api.add_resource(Init, '/apis/init')
api.add_resource(Intent, '/apis/intent')
api.add_resource(NER, '/apis/ner')