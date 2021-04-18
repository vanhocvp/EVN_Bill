import tensorflow as tf
import tensorflow.keras.backend as K
import tensorflow.keras.layers as L
from tensorflow_addons.text import crf_log_likelihood, crf_decode
from transformers import AutoTokenizer, TFAutoModel
import numpy as np
# from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.layers import Dense
# from tf.keras.preprocessing.sequence import pad_sequences
# from keras.utils.np_utils import to_categorical
import tensorflow as tf
import os
import configparser
class CRF(L.Layer):
    def __init__(self,
                 output_dim,
                 sparse_target=True,
                 **kwargs):
        """    
        Args:
            output_dim (int): the number of labels to tag each temporal input.
            sparse_target (bool): whether the the ground-truth label represented in one-hot.
        Input shape:
            (batch_size, sentence length, output_dim)
        Output shape:
            (batch_size, sentence length, output_dim)
        """
        super(CRF, self).__init__(**kwargs)
        self.output_dim = int(output_dim) 
        self.sparse_target = sparse_target
        self.input_spec = L.InputSpec(min_ndim=3)
        self.supports_masking = False
        self.sequence_lengths = None
        self.transitions = None

    def build(self, input_shape):
        assert len(input_shape) == 3
        f_shape = tf.TensorShape(input_shape)
        input_spec = L.InputSpec(min_ndim=3, axes={-1: f_shape[-1]})

        if f_shape[-1] is None:
            raise ValueError('The last dimension of the inputs to `CRF` '
                             'should be defined. Found `None`.')
        if f_shape[-1] != self.output_dim:
            raise ValueError('The last dimension of the input shape must be equal to output'
                             ' shape. Use a linear layer if needed.')
        self.input_spec = input_spec
        self.transitions = self.add_weight(name='transitions',
                                           shape=[self.output_dim, self.output_dim],
                                           initializer='glorot_uniform',
                                           trainable=True)
        self.built = True

    def compute_mask(self, inputs, mask=None):
        # Just pass the received mask from previous layer, to the next layer or
        # manipulate it if this layer changes the shape of the input
        return mask

    def call(self, inputs, sequence_lengths=None, training=None, **kwargs):
        sequences = tf.convert_to_tensor(inputs, dtype=self.dtype)
        if sequence_lengths is not None:
            assert len(sequence_lengths.shape) == 2
            assert tf.convert_to_tensor(sequence_lengths).dtype == 'int32'
            seq_len_shape = tf.convert_to_tensor(sequence_lengths).get_shape().as_list()
            assert seq_len_shape[1] == 1
            self.sequence_lengths = K.flatten(sequence_lengths)
        else:
            self.sequence_lengths = tf.ones(tf.shape(inputs)[0], dtype=tf.int32) * (
                tf.shape(inputs)[1]
            )

        viterbi_sequence, _ = crf_decode(sequences,
                                         self.transitions,
                                         self.sequence_lengths)
        output = K.one_hot(viterbi_sequence, self.output_dim)
        return K.in_train_phase(sequences, output)

    @property
    def loss(self):
        def crf_loss(y_true, y_pred):
            y_pred = tf.convert_to_tensor(y_pred, dtype=self.dtype)
            log_likelihood, self.transitions = crf_log_likelihood(
                y_pred,
                tf.cast(K.argmax(y_true), dtype=tf.int32) if self.sparse_target else y_true,
                self.sequence_lengths,
                transition_params=self.transitions,
            )
            return tf.reduce_mean(-log_likelihood)
        return crf_loss

    @property
    def accuracy(self):
        def viterbi_accuracy(y_true, y_pred):
            # -1e10 to avoid zero at sum(mask)
            mask = K.cast(
                K.all(K.greater(y_pred, -1e10), axis=2), K.floatx())
            shape = tf.shape(y_pred)
            sequence_lengths = tf.ones(shape[0], dtype=tf.int32) * (shape[1])
            y_pred, _ = crf_decode(y_pred, self.transitions, sequence_lengths)
            if self.sparse_target:
                y_true = K.argmax(y_true, 2)
            y_pred = K.cast(y_pred, 'int32')
            y_true = K.cast(y_true, 'int32')
            corrects = K.cast(K.equal(y_true, y_pred), K.floatx())
            return K.sum(corrects * mask) / K.sum(mask)
        return viterbi_accuracy

    def compute_output_shape(self, input_shape):
        tf.TensorShape(input_shape).assert_has_rank(3)
        return input_shape[:2] + (self.output_dim,)

    def get_config(self):
        config = {
            'output_dim': self.output_dim,
            'sparse_target': self.sparse_target,
            'supports_masking': self.supports_masking,
            'transitions': K.eval(self.transitions)
        }
        base_config = super(CRF, self).get_config()
        return dict(base_config, **config)
class NER:
    def __init__(self):
        checkpoint_path = "/home/vanhocvp/Code/SmartCall/EVN_bill/APP/process/Models/training_2/training_2/cp1.ckpt"
        checkpoint_dir = os.path.dirname(checkpoint_path)
        self.tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base", use_fast=False)
        # self.crf_layer = CRF()
        self.model = self.create_model(checkpoint_path)
        
        # config = configparser.ConfigParser()
        # config.read('/home/vanhocvp/Code/SmartCall/training/api/model/config.ini')
        # self.intent_list = config.get('DEFAULT','intent').split(',\n')
        self.ne_list = {0:'B-DIS', 1:'B-PER', 2:'B-PROV', 3:'B-STR', 4:'I-DIS', 5:'I-PER', 6:'I-PROV',  7:'I-STR', 8:'O'}
        # print (self.intent_list)

    def create_model(self, checkpoint_path):
        phobert = TFAutoModel.from_pretrained("vinai/phobert-base")
        MAX_LEN = 30
        ids = tf.keras.layers.Input(shape=(30,), dtype=tf.int32)
        mask = tf.keras.layers.Input(shape=(30,), name='attention_mask', dtype='int32')
        # For transformers v4.x+: 

        embeddings = phobert(ids,attention_mask = mask)[0]
        # print(embeddings[:,0,:])
        # X = tf.keras.layers.TimeDistributed(Dense(50, activation='relu'))(embeddings)
        X =tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(256,return_sequences=True))(embeddings)
        # X = tf.keras.layers.BatchNormalization()(X)
        # X =  Attention1()(X)
        # X = tf.keras.layers.Dense(128, activation='relu')(X)
        # X = tf.keras.layers.Dropout(0.5)(X)
        # yy = tf.keras.layers.TimeDistributed(Dense(9, activation='softmax'))(X)
        X = tf.keras.layers.TimeDistributed(Dense(9, activation='relu'))(X)
        crf = CRF(9)
        out = crf(X)
        model = tf.keras.models.Model(inputs=[ids,mask], outputs=[out])
        model.summary()
        model.layers[2].trainable = False
        # model.layers[2].roberta.embeddings.trainable = True
        # model.compile(optimizer=tf.keras.optimizers.Adam(lr=0.0001),loss = crf.loss,metrics=crf.accuracy)
        model.compile(optimizer='adam',loss = crf.loss,metrics=crf.accuracy)
        model.load_weights(checkpoint_path)
        return model
    
    def encoding(self,sent,max_length = 30):
        all_sent = []
        all_mask_sent = []
        for line in sent:
            
            # print(line)
            # l = tokenizer.encode(line)
            tokens = self.tokenizer.encode_plus(line, max_length=max_length,
                                        truncation=True, padding='max_length',
                                        add_special_tokens=True, return_attention_mask=True,
                                        return_token_type_ids=False, return_tensors='tf')
            umk = np.array(tokens['input_ids']).reshape(-1)
            mk = np.array(tokens['attention_mask']).reshape(-1)
            all_sent.append(umk)
            all_mask_sent.append(mk)
            # print(np.array(all_sent).shape)
        # print(all_sent)
        # print(all_mask_sent[0])
        #   all_sent = padding(all_sent,max_length=max_length)
        #   all_mask_sent = padding(all_mask_sent,max_length=max_length)
        return np.array(all_sent),np.array(all_mask_sent)
    def padding(self, encoded, max_length):
        return tf.keras.preprocessing.sequence.pad_sequences(encoded, 30, padding = 'post') 
    def get_entities(self, mess):
        # return 'vanhocvp'
        entities = {}
        mess = mess.split()
        len_mess = len(mess)
        list_mess = [mess]
        
        x, mask = self.encoding(list_mess)
        pred = self.model.predict((x, mask))
        pred = np.argmax(pred, axis = 2)[0][:len_mess]
        print (pred)
        label = []
        for i in pred:
            label.append(self.ne_list[i])
        print (label)
        
        for ind, tag in enumerate (label):
            if tag == 'B-STR':
                entities['STR'] = mess[ind]
            if tag == 'B-DIS':
                entities['DIS'] = mess[ind]
            if tag == 'B-PROV':
                entities['PROV'] = mess[ind]
            if tag == 'B-PER':
                entities['PER'] = mess[ind]
            if tag == 'I-STR':
                entities['STR'] += ' ' + mess[ind]
            if tag == 'I-DIS':
                entities['DIS'] += ' ' + mess[ind]
            if tag == 'I-PROV':
                entities['PROV'] += ' ' + mess[ind]
            if tag == 'I-PER':
                entities['PER'] += ' ' + mess[ind]
            
        # index = np.argmax(pred).axis[2]
        print (entities)
        return entities





# x = NER()
# y = x.get_entities('thanh')
# print (y)





