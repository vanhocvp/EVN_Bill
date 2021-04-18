""" GET NEXT ACTION AND MESSAGE RESPONSE

    use: final_intent + Graph => action
        GET message
    
    return:
        action
        message
        json_response
        conver

"""
from process.Graph.graph import Graph
import random
class Process_Action:
    def __init__(self):
        self.graph = Graph()
        self.list_mess_response = self.graph.get_mess_response()
    def get_final_action(self, final_intent, pre_conv, entities):
        pre_action = pre_conv.pre_action
        # if pre_action == 'action_loop':
        #     pre_conv.main_action = 'method'
        print (final_intent, pre_action)
        action = self.graph.get_next_node(pre_action, final_intent)
        print (action)
        if action == 'action_check_bill':
            rand = random.randint(1,4)
            action += '_'+str(rand)
        if 'action_loop' in action or action == 'action_get_method_2':
            pre_main_action = pre_conv.main_action
            pre_conv.main_action = 'loop'
            # pre_conv.pre_context = 'method'
            list_entities_method = []
            list_entities_method.append(pre_conv.phone_number)
            list_entities_method.append(pre_conv.code)
            list_entities_method.append(pre_conv.address)
            
            if list_entities_method.count(None) < 2:
                if pre_main_action == 'get_phone_number':
                    txt = 'số điện thoại'
                if pre_main_action == 'get_code_customer':
                    txt = 'mã khách hàng'
                if pre_main_action == 'get_address':
                    txt = 'địa chỉ'
                if pre_main_action == 'get_name':
                    txt = 'họ và tên'
                print ('==> ', action)
                print (pre_main_action)
                mess_response = self.list_mess_response['action_loop_forward'].format(main_action = txt)
                if action[-2] == '_':
                    action = action[:-2]
                pre_conv.pre_context = 'end_loop'
                return action, mess_response, pre_conv
            else:
                
                # pre_conv.context = 'method'
                ind = [i for i, e in enumerate(list_entities_method) if e == None]
                tmp = {0: 'số điện thoại', 1 : 'mã khách hàng', 2 : 'địa chỉ'}
                tmp_1 = [ tmp[i] for i in ind]
                method_1 = tmp_1[0]
                method_2 = tmp_1[1]
                print ('==> ', action)
                mess_response = self.list_mess_response[action].format(method_1 = method_1, method_2 = method_2)
                if action[-2] == '_':
                    action = action[:-2]
                return action, mess_response, pre_conv
        if 'action_loop' in action and final_intent == 'intent_affirm':
            pre_conv.pre_context = 'method'
        if 'acton_confirm_address' in action and final_intent == 'intent_affirm':
            pre_conv.pre_context = 'method'
        if action == 'no_next_node':
            print (final_intent)
            if 'fallback' in pre_conv.pre_context:
                final_intent = 'intent_fallback_2'
            else:
                final_intent = 'intent_fallback_1'
                pre_conv.pre_context = 'fallback_' + pre_conv.pre_context
            action = self.graph.get_next_node(pre_action, final_intent)
        # if pre_action == 'action_loop' or pre_action == 'action_get_method'
        print ('==> ', action)
        mess_response = self.list_mess_response[action]
        if action[-2] == '_':
            action = action[:-2]
        if action == 'action_confirm_code_customer':
            print (entities)
            mess_response = mess_response.format(code = pre_conv.code)
        if action == 'action_confirm_phone_number':
            print (mess_response)
            mess_response = mess_response.format(phone_number = pre_conv.phone_number)
        if action == 'action_confirm_address':
            mess_response = mess_response.format(address = pre_conv.address)
        if action == 'action_confirm_name':
            mess_response = mess_response.format(name = pre_conv.name)
        return action, mess_response, pre_conv

# x= Process_Action()
# print (x.get_final_action('intent_provide_address_no_exist_1'))