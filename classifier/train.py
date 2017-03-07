#!/usr/bin/evn python
# -*- coding:utf-8 -*-

import sys, logging, json
from sklearn.linear_model import SGDClassifier
from feature.feature_word import WordFeature
#from feature.feature_topic import TopicFeature

from sklearn.preprocessing  import LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.grid_search import GridSearchCV
from sklearn.naive_bayes import BernoulliNB
from sklearn.naive_bayes import MultinomialNB
from sklearn import svm

try:
    import cPickle as pickle
except:
    import pickle

class Train(object):
    """
    训练类
    """
    def __init__(self, vec_space='word', params={}):
        self.label_encoder = LabelEncoder()
        self.feature_coef = {}
        if vec_space == 'word':
            Feature = WordFeature
        elif vec_space == 'topic':
            #Feature = TopicFeature
            pass
        else:
            print 'ERROR: vec_space in train.py does not assigned !!'
            Feature = u''
            

        self.vectorizer = DictVectorizer() 
        self.feature_select = Feature(user_params=params)
        #self.clf = LogisticRegression(penalty='l2', C=1.0, class_weight='auto')  
        #self.clf = SGDClassifier(shuffle=True)   
        self.clf = svm.LinearSVC(dual=False)      

        self.params = params
        # 训练pipeline：将词频特征转换为向量 -> 特征选择 -> 分类。
        self.pipeline = Pipeline([
                        ('vec',   self.vectorizer),
                        ('feat',  self.feature_select),
                        ('clf',   self.clf)
                        #('clf',   BernoulliNB(alpha=0.01, fit_prior=True))
                        #('clf',   SGDClassifier(shuffle=True))
                 ])

    def train(self, features, labels):
        """
        训练方法
        :param features: 训练集特征，列表类型，每个元素是一个特征词频统计字典，[{word1: count, word2: count, ...}, ...]
        :param labels: 训练集类标识，列表类型，长度与特征列表相等。[y1, y2, y3, ...]
        """
        # 转换类标识
        y = self.label_encoder.fit_transform(labels)
        self.pipeline.fit(features, y)
        #把选出来的特征和系数存储到{}
        self.save_support_features()

    def save_support_features(self):
        """
        获取支持特征，并存储在字典中
        """
        cates = self.label_encoder.classes_
        word_dict = {str(value): key for key, value in self.vectorizer.vocabulary_.items()}
        features_support = self.feature_select.get_support_features()
        for i in range(len(self.clf.coef_)):
            if self.feature_coef.has_key(cates[i]) == False:
                self.feature_coef[cates[i]] = {}
            for j in range(len(features_support)):
                self.feature_coef[cates[i]][word_dict[str(features_support[j])]] = self.clf.coef_[i][j]

    def get_feature_coef(self):
        """
        get features coefficent.
        """
        return self.feature_coef


    def grid_train(self, features, labels, cv=2, n_jobs=1, verbose=0):
        """
        采用GridSearch方法找到分类器最佳参数。
        """
        y = self.label_encoder.fit_transform(labels)
        k = self.params['select_k']
        param_grid = { 'feat__select_k': [k, k*2, k/2, k*3] }
        grids = GridSearchCV(estimator=self.pipeline, param_grid=param_grid, cv=cv, n_jobs=n_jobs, verbose=verbose)
        grids.fit(features, y)
        self.pipeline = grids.best_estimator_
        logging.info("best param", grids.best_params_)
        return grids.best_params_
 
    def dump_model(self, dumpfile):
        """
        Brief: dump the model to disk.
        """
        self.model = (self.pipeline, self.label_encoder)
        with open(dumpfile, 'wb') as f:
           pickle.dump(self.model, f)
