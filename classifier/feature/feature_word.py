#!/usr/bin/env python
#! -*- coding:utf-8 -*-

import logging
import json, sys
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_selection import SelectPercentile, chi2
reload(sys)
sys.setdefaultencoding('utf-8')

class WordFeature(object):
    '''
        使用TFIDF值计算单词空间内向量
    '''
    def __init__(self, user_params):
        params = {
            'tfidf_sublinear_tf'   : False,
            'select_score_func' : 'chi2',
            'select_percentile'  : 10
        } 
        for key,value in user_params.iteritems():
            if not key in params:
                logging.warn('Invalid parameter %s ' 'for estimator %s' % (key, self.__class__.__name__))
            params[key] = user_params[key]
        self.init(tfidf_sublinear_tf=params['tfidf_sublinear_tf'], select_score_func=params['select_score_func'], select_percentile=params['select_percentile'] )

    def init(self, tfidf_sublinear_tf=False, select_score_func='chi2', select_percentile=10):
        if select_score_func == 'chi2':
            score_func = chi2
        self.tfidf = TfidfTransformer(sublinear_tf=tfidf_sublinear_tf)
        self.select_words = SelectPercentile(score_func=score_func, percentile=select_percentile)
    
    def fit(self, X, y):
        self.tfidf.fit(X)
        slef.select_words.fit(X, y)

    def fit_transform(self, X, y):
        '''
            将特征、标签转化为向量，并训练字典
        '''
        X_new = self.tfidf.fit_transform(X)
        X_new = self.select_words.fit_transform(X_new, y)
        return X_new
 
    def get_support_features(self):
        return self.select_words.get_support(True)

    def transform(self, X):
        '''
            将特征转化为向量，并计算TFIDF值，卡方检验选择特征
        '''
        X_new = self.tfidf.transform(X)
        X_new = self.select_words.transform(X_new)
        return X_new


if __name__ == '__main__':
    wf = WordFeature({}) 

