from intent import INTENT_CLS
from ner import NER

class Models:
    def __init__(self):
        self.intent = INTENT_CLS()
        self.ner  = NER()
    def get_intent(self, message):
        return self.intent.get_intent(message)
    def get_ne(self, message):
        return self.ner.get_entities(message)
# x = Models()
# print(x.get_intent('vanhocvp'))