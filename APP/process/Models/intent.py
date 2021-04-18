from transformers import AutoTokenizer, TFAutoModel
import numpy as np
# from tf.keras.preprocessing.sequence import pad_sequences
# from keras.utils.np_utils import to_categorical
import tensorflow as tf
import os
import configparser
class INTENT_CLS:
    def __init__(self):
        checkpoint_path = "/home/vanhocvp/Code/SmartCall/EVN_bill/APP/process/Models/training_1/training_1/cp1.ckpt"
        checkpoint_dir = os.path.dirname(checkpoint_path)
        # self.tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base")
        self.tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base", use_fast=False)
        self.model = self.creat_model(checkpoint_path)
        # config = configparser.ConfigParser()
        # config.read('/home/vanhocvp/Code/SmartCall/training/api/model/config.ini')
        # self.intent_list = config.get('DEFAULT','intent').split(',\n')
        self.intent_list = {0:'intent_this_phone', 1:'intent_affirm', 2:'intent_provide_code_customer', 3:'intent_provide_address', 4:'intent_cant_hear', 5:'intent_deny_confirm', 6:'intent_provide_name', 7:'intent_provide_number_phone'}
        print (self.intent_list)

    def creat_model(self, checkpoint_dir):
        phobert = TFAutoModel.from_pretrained("vinai/phobert-base")
        MAX_LEN = 30
        ids = tf.keras.layers.Input(shape=(30), dtype=tf.int32)
        mask = tf.keras.layers.Input(shape=(30,), name='attention_mask', dtype='int32')
        # For transformers v4.x+: 

        embeddings = phobert(ids,attention_mask = mask)[0]
        X =tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(256))(embeddings)
        y = tf.keras.layers.Dense(8, activation='softmax', name='outputs')(X)
        model = tf.keras.models.Model(inputs=[ids,mask], outputs=[y])
        # model.summary()
        model.layers[2].trainable = False
        model.compile(optimizer='adam',loss = 'categorical_crossentropy',metrics='accuracy')
        #### LOAD WEIGHT ###
        latest = tf.train.latest_checkpoint(checkpoint_dir)
        model.load_weights(checkpoint_dir)
        return model
    def encoding(self, sent,max_length = 30):
        all_sent = []
        all_mask_sent = []
        sent = [sent]
        for line in sent:
            line = line.lower()
            tokens = self.tokenizer.encode_plus(line, max_length=max_length,
                                        truncation=True, padding='max_length',
                                        add_special_tokens=True, return_attention_mask=True,
                                        return_token_type_ids=False, return_tensors='tf')
            umk = np.array(tokens['input_ids']).reshape(-1)
            mk = np.array(tokens['attention_mask']).reshape(-1)
            all_sent.append(umk)
            all_mask_sent.append(mk)

        all_sent = self.padding(all_sent,max_length=max_length)
        all_mask_sent = self.padding(all_mask_sent,max_length=max_length)
        all_sent = np.array(all_sent)
        all_mask_sent = np.array(all_mask_sent)
        return all_sent,all_mask_sent
    def padding(self, encoded, max_length):
        return tf.keras.preprocessing.sequence.pad_sequences(encoded,30,padding = 'post') 
    def get_intent(self, mess):
        x = self.encoding(mess)
        pred = self.model.predict(x)
        index = np.argmax(pred)
        return self.intent_list[index], pred[0][index]

# x = INTENT_CLS()
# text  = ["không nghe rõ",
#         "đúng vậy",
#         "không nha",
#         "tra cứu theo số hộ anh",
#         "cô tìm kiếm mã vị trí",
#         "tra theo mã",
#         "mình tên là cam bối trọng nhé",
#         'tra dùm anh luôn số này']
# for i in text:
#     pre, score = x.get_intent(i)
#     print (pre, '\t', score,'\t', i)