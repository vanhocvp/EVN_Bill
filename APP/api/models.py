from api import db, process
# , graph, model

import io, random

class Conver(db.Model):
    __table__args__ = {'extend_existing': True}
    sender_id = db.Column(db.Integer, primary_key = True)
    main_action = db.Column(db.String(50))
    pre_action = db.Column(db.String(50))
    pre_context = db.Column(db.String(50))
    province = db.Column(db.String(50))
    phone_number = db.Column(db.String(50))
    code = db.Column(db.String(50))
    address = db.Column(db.String(50))
    name = db.Column(db.String(50))
    def __repr__(self):
        return '<Conver {}>'.format(self.intent)
def process_request(args):
    sender_id = args['sender_id']
    message = args['message']
    pre_conv = Conver.query.get(sender_id)
    # return dict({'text': pre_conv.pre_action})
    action, mess, context, entities, pre_conv = process.process_request(sender_id, message, pre_conv)
    # SAVE TO SQL
    # pre_conv.pre_action = action
    # pre_conv.pre_context = context
    db.session.commit()
    res = {}
    res['sender_id'] = sender_id
    res['text'] = mess
    print (res)
    return res
     
