from .policy import Policy
from .process_action import Process_Action
import json
import requests
# from process.Models.models import Models
class Proces_Request:
    def __init__(self):
        self.policy = Policy()
        self.process_action = Process_Action()
        # self.models = Models()
        self.intent_api = 'http://localhost:8000/apis/intent'
        self.ner_api = 'http://localhost:8000/apis/ner'
    def process_request(self, sender_id, message, pre_conv):
        res = self.get_intent(message)
        intent = res['intent']
        score = res['score']
        entities = self.get_ner(message)
        print ('===============================')
        print ('INTENT: ', intent)
        print ('SCORE: ', score)
        print ('ENTITIES: ', entities)
        print ('---------------------')
        final_intent, context, pre_conv, entities = self.policy.get_final_intent(message, intent, score, entities, pre_conv)
        pre_conv.pre_context = context
        # forward to process_action
        
        print ('---------------------')       
        print ('FINAL_INTENT = {}'.format(final_intent))
        print ('CONTEXT = {}'.format(context))
        print ('---------------------')

        action, message, pro_conv = self.process_action.get_final_action(final_intent, pre_conv, entities)
        pre_conv.pre_action = action
        print ('HERE:', pre_conv.pre_context)
        return action, message, context, entities, pre_conv
    def get_intent(self, mess):
        res = (eval(requests.post(url = self.intent_api, json={'message':mess}).content))
        res['score'] = float(res['score'])
        return res
    def get_ner(self, mess):
        res = eval(requests.post(url = self.ner_api, json={'message':mess}).content)
        # if res == None:
        #     return {'entities' : ''}
        return res
