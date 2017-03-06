#!/usr/bin/env python
#! -*- coding:utf-8 -*-

import sys, os, logging, re, json, math
from segment_jieba import Segmenter

import ConfigParser

class Preprocess(object):
    def __init__(self, cfg_file_name):
        self.config = ConfigParser.ConfigParser()
        self.cur_dir = os.path.dirname(os.path.abspath(cfg_file_name))
        self.segmenter = Segmenter()
        self.d_models = {}
        self.cfg_parser(cfg_file_name)

    def cfg_parser(self, cfg_file_name):
        """
        Brief: config file parser. (config file: classifier.cfg)
        """
        self.config.read(cfg_file_name)
        
        section = 'segmenter'
        for (key, value) in self.config.items(section):
            if key.startswith('user_dict'):
                dict_name = os.path.join(self.cur_dir, value)
                self.segmenter.add_user_dict(dict_name)

        section = 'preprocess'
        self.stop_words = set()
        self.load_option_words(section, 'stop_file', self.stop_words)

        self.stop_feature = {}
        self.load_option_words(section, 'stop_feature_dir', self.stop_feature) 
        
        self.replace_lst = [(u'!', u','), (u'！', u','), (u'。', u','), (u'，', u','),
                (u'【', u''), (u'】', u''), (u'[', u''), (u']', u''), (u'《', u''), (u'》', u'')]

        section = 'model'
        for (key,value) in self.config.items(section):
            self.d_models[key] = value
            

    def load_option_words(self, section, option, word_set):
        if self.config.has_option(section, option):
            if option == "stop_feature_dir":
                value = self.config.get(section, option)
                if os.path.exists(value):
                    for f in os.listdir(value):
                        if not f.endswith('.stop'):
                            continue
                        filename = os.path.join(value, f)
                        fp = open(filename, 'r')
                        _set = set(word.strip() for word in fp.readlines())
                        word_set[f[:f.find('.stop')]] = list(_set)
                        fp.close()
            else:
                value = self.config.get(section, option)
                filename = os.path.join(self.cur_dir, value)
                fp = open(filename, 'r') 
                for line in fp:
                    if line.startswith('#'):
                        continue
                    word_set.add(line.rstrip().split()[0].decode('utf-8'))
                logging.info("load words %s" %filename)
                fp.close()


    # 检查特征单词是否有效
    def check_valid(self, word, model_name):
        if not word:
            return False
        if word.isnumeric():
            return False
        if self.check_float(word):
            return False
        if len(word) == 1:
            return False
        if word in self.stop_words:
            return False
        if self.stop_feature.has_key(model_name):
            if word in self.stop_feature[model_name]:
                return False 
        return True

    #判断word是否为float
    def check_float(self, word):
        try:
            f = float(word)
            return True
        except:
            return False

    def convert_word_features(self, text, model_name):
        words = self.segmenter.segment(text.strip())
        features = {}

        for word in words:
            word = word.strip().replace(u'（', u'').replace(u'）', u'').replace(u'(', u'').replace(u')', u'')
            if not word:
                continue
            if not self.check_valid(word, model_name):
                continue
            if features.has_key(word):
                features[word] += 1
            else:
                features[word] = 1
        return features


    # 将 数据 转为字典特征
    def process(self, title=u'', content=u'', model_name='null'):
        text = title + content 
        text = self.extract_sentence(text)
        features = self.convert_word_features(text, model_name)
        return features

    def extract_sentence(self, text):            
        for (ostr, rstr) in self.replace_lst:
            text = text.replace(ostr, rstr)
        return text

if __name__ == '__main__':
    preprocess = Preprocess('../classifier.cfg')
    #features = preprocess.process(u'科比篮球a中国行12.3', u'')
    #features = preprocess.process(u'Please read question before you are writing answer! i wasn`t asking where I can do massage!I asked about oil!', u'I advise you to use car oil any type forever like my car. It is helpfull to maintaine your body brigthness.')

    #features = preprocess.process(u'I heard that I have to take green card for vaccinating my child from NHA near Abu Hamour petrol station. Is there any fee for taking green card?', u'for health card there is only a charge for qr 100  but for green card you will have to sell your properties to get it')

    features = preprocess.process(u'IBQ is a very good one, and the customer service is excellent.')

    #print json.dumps(features, ensure_ascii=False).encode('utf-8')
    print features
