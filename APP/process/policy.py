# from Models.models import Models
from process.Graph.graph import Graph
import re
""" GET FINAL INTENT """
domain = ['Nghệ An', 'Thanh Hóa', 'Quảng Trị', 'Quảng Bình', 'Thừa Thiên Huế', 'Hà Tĩnh',
'Đà Nẵng', 'Quảng Nam', 'Quảng Ngãi', 'Bình Định', 'Phú Yên', 'Khánh Hòa', 'Ninh Thuận','Bình Thuận',
'Kon Tum', 'Đắk Lắk', 'Gia Lai', 'Đắk Nông','Lâm Đồng']
domain = [i.lower() for i in domain]
class Policy:
    def __init__(self):
        self.str_province = self.get_str_province()
        self.graph = Graph()
    def get_final_intent(self, message, intent, score, entities, pre_conv):
        pre_context = pre_conv.pre_context
        pre_action = pre_conv.pre_action
        print ('pre_action: ', pre_action)
        print ('pre_context:', pre_context)
        message = message.lower()
        if score < 0.8:
            if pre_context == None or 'fallback' in pre_context:
                intent = 'intent_fallback_2'
            else:
                intent = 'intent_fallback_1'
        if len(re.findall("[pP].{5}\d{7}", message)) != 0:
            intent = 'intent_provide_code_customer'
        elif len(re.findall("\d{10}", message)) != 0:
            intent = 'intent_provide_phone_number'
        final_intent = intent
        context = final_intent[7:] ###
        if pre_action == None:
            action = 'action_start'
            context = 'start'
            final_intent = 'intent_start'
            return final_intent, context, pre_conv, entities
        #### START
        # and intent == 'intent_provide_address'
        if pre_action == 'action_start' or pre_action == 'action_start_2':
            print (self.str_province, message)
            if re.search(self.str_province, message) == None:
                final_intent = intent + '_no_exist'
                if pre_context == 'start':
                    final_intent += '_1'
                    context = 'start_2'
                if pre_context == 'start_2':
                    final_intent += '_2'
            else:    
                intent = 'intent_provide_address'
                have_support = 0
                for i in domain:
                    if i in message.lower():
                        have_support = 1
                        break
                if have_support == 0:
                    final_intent = intent + '_have_not_support'
                    context = final_intent[7:]
                else:
                    final_intent = intent + '_have_support'
                    context = 'method'
            return final_intent, context, pre_conv, entities
        # LOOP
        if pre_action == 'action_loop':
            if  (('code' in final_intent and pre_conv.code != None)
                    or ('phone_number' in final_intent and pre_conv.phone_number != None)
                    or ('address' in final_intent and pre_conv.address != None)):
                    if 'fallback' in pre_conv.pre_context:
                        final_intent = 'intent_fallback_2'
                    else:
                        final_intent = 'intent_fallback_1'
                    pre_conv.pre_context = 'fallback_' + pre_conv.pre_context
                    # action = self.graph.get_next_node(pre_action, final_intent)
                    # if action[-2] == '_':
                    #     action = action[:-2]
        # ##### Graph to cls fallback
        if self.graph.get_next_node(pre_action, final_intent) == 'no_next_node':
            if 'fallback_1' in pre_context:
                final_intent = 'intent_fallback_2'
            else:
                final_intent = 'intent_fallback_1'
        main_action = pre_conv.main_action
        if pre_context == 'method' or main_action == 'loop' or pre_context == 'fallback_1_method':
            if 'provide' in final_intent:
                if 'phone_number' in final_intent:
                    main_action = 'get_phone_number'
                if 'code_customer' in final_intent:
                    main_action = 'get_code_customer'
                if 'address' in intent:
                    main_action = 'get_address'
                pre_context = 'method'
            if 'fallback_1' in final_intent and pre_context == 'method':
                context = 'fallback_1_method'
            if 'fallback_1' in  final_intent and pre_context == 'fallback_1_method':
                context = 'end'

        if 'get_name' in pre_action:
            main_action = 'get_name'
        
        pre_conv.main_action = main_action
        ### MAIN ACTION
        
        if main_action == 'get_code_customer':
            NE = re.findall("[pP].{5}\d{7}", message)
            entities = {}
            if len(NE) == 0:
                entities = 'unknow'
                if pre_conv.code == None:
                    pre_conv.code = entities
            else:
                entities['code'] = NE[0]
                pre_conv.code = NE[0]
            final_intent, context = self.script(main_action, pre_context, final_intent.split('intent_')[1], score, entities)
            if pre_context == 'method':
                # pre_conv = 
                if 'no_entities' in final_intent:
                    final_intent = intent + '_no_entities'
                else:
                    final_intent = 'intent_'+final_intent
            else:
                final_intent = 'intent_'+final_intent
        
        if main_action == 'get_phone_number':
            NE = re.findall("\d{10}", message)
            entities = {}
            if len(NE) == 0:
                entities = 'unknow'
                if pre_conv.phone_number == None:
                    pre_conv.phone_number = entities
            else:
                entities['phone_number'] = NE[0]
                pre_conv.phone_number = NE[0]
            final_intent, context = self.script(main_action, pre_context, final_intent.split('intent_')[1], score, entities)
            if pre_context == 'method':
                # pre_conv = 
                if 'no_entities' in final_intent:
                    final_intent = intent + '_no_entities'
                else:
                    final_intent = 'intent_'+final_intent
            else:
                final_intent = 'intent_'+final_intent

        if main_action == 'get_address':
            print (entities)
            if  len(entities.keys()) == 0:
                entities = 'unknow'
                if pre_conv.address == None:
                    pre_conv.address = entities
            else:
                
                entities['address'] = ''
                list_ne = ['STR', 'DIS', 'PROV']
                for i in list_ne:
                    try:
                        entities['address'] += entities[i] + ' '
                    except:
                        pass
                pre_conv.address = entities['address'][:-1]
            final_intent, context = self.script(main_action, pre_context, final_intent.split('intent_')[1], score, entities)
            if pre_context == 'method':
                # pre_conv = 
                if 'no_entities' in final_intent:
                    final_intent = intent + '_no_entities'
                else:
                    final_intent = 'intent_'+final_intent
            else:
                final_intent = 'intent_'+final_intent
        if main_action == 'get_name':
            if  len(entities.keys()) == 0:
                entities = 'unknow'
                if pre_conv.name == None:
                    pre_conv.name = entities
            else:
                entities['name'] = ''
                for i in entities['PER'].split(' '):
                    entities['name'] += i.capitalize() + ' '
                # entities['name'] = ' '.join(i.capitalize()) for i in entities['PER'].split()
                pre_conv.name = entities['name'][:-1]
            final_intent, context = self.script(main_action, pre_context, final_intent.split('intent_')[1], score, entities)
            if pre_context == 'method':
                # pre_conv = 
                if 'no_entities' in final_intent:
                    final_intent = intent + '_no_entities'
                else:
                    final_intent = 'intent_'+final_intent
            else:
                final_intent = 'intent_'+final_intent    
        return final_intent, context, pre_conv, entities
    def get_str_province(self):
        list_province = []
        with open('/home/vanhocvp/Code/SmartCall/EVN_bill/APP/process/province.txt', 'r') as f:
            list_province = f.readlines()
        str_province = ''
        for i in list_province:
            str_province += '|' +i.split('\n')[0].lower()
        return str_province[1:]   
    def script(self, main_action, pre_context, intent, score, entities):
        context = intent
        print ('VANHOC: ', intent, pre_context, entities)
        if 'fallback' in pre_context:
            if 'fallback' in intent:
                intent = 'fallback_2'
                context = 'method'
                return intent, context 
            else:
                pre_context = pre_context[9:]
        if 'method' in pre_context or pre_context == 'recall': # 12 - 13
            if 'provide' in intent:
                if entities == 'unknow':
                    if pre_context == 'method':
                        intent = 'no_entities'
                        context = 'provide_0'
                    elif pre_context == 'recall':
                        intent = 'provide_no_entities_2'
                        context = 'method'
                    else:                        
                        intent = 'provide_no_entities_1'
                        context = 'provide_no_entities_1' # ==> action: no entities
                else:
                    # intent = intent = providec
                    context = 'provide'
                    if pre_context == 'recall':
                        context = 'provide_1'
                     # = provide
            if 'fallback' in intent:
                intent = 'fallback_1'
                context = 'fallback_' + pre_context
        
        

        if pre_context == 'provide_no_entities_1':
            if 'provide' in intent:
                if entities == 'unknow':
                    intent = 'provide_no_entities_2'
                    context = 'method' # ==> action: no entities
                else:
                    # intent = intent = provide
                    context = 'provide_1'               # ==> action: confirm
            if 'fallback' in intent:
                    intent = 'fallback_2'
                    context = 'fallback'
        if 'deny_confirm'  in pre_context:
            if 'provide' in intent:
                if entities == 'unknow':
                    intent = 'deny_confirm_2'
                    context = 'method' # ==> action: no entities
                else:
                    # intent = 'deny_confirm_2'
                    context = 'provide_1'              # ==> action: confirm
            if 'fallback' in intent:
                    intent = 'fallback_1'
                    context = 'fallback_' + pre_context
        if pre_context == 'provide_0':
            if 'fallback' in intent:
                intent = 'fallback_1'
                context = 'fallback_' + pre_context
            if 'provide' in intent:
                if entities == 'unknow':
                    intent = 'provide_no_entities_1'
                    context = 'provide_no_entities_1'
                else:
                    context = 'provide' 
        if pre_context == 'provide':
            if 'fallback' in intent:
                intent = 'fallback_1'
                context = 'fallback_' + pre_context
            # if intent == 'affirm': khong gi dac biet
            if 'deny_confirm' in intent:
                intent = 'deny_confirm_1'
                context = intent
            if 'provide' in intent:
                if entities == 'unknow':
                    intent = 'deny_confirm_1'
                    context = 'recall'
                else:
                    context = 'provide_1'
        if pre_context == 'provide_1': ######### deny_confirm_2 ====> action_loop
            if 'fallback' in intent:
                intent = 'fallback_1'
                context = 'fallback_' + pre_context
            # if intent == 'affirm': khong gi dac biet
            if 'deny_confirm' in intent:
                intent = 'deny_confirm_2'
                context = 'method'
            if 'provide' in intent:
                if entities == 'unknow':
                    intent = 'provide_no_entities_2'
                    context = 'method'
                else:
                    intent = 'provide_no_entities_2'
                    context = 'method'    
        return intent, context


# x = re.search('Ha Noi|Thanh Hoa', 'toi o')
# print (x)






# x = Policy(1,2,3,4)
# print (x.get_str_province())