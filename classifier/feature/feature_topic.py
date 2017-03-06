#! -*- coding:utf-8 -*-

import sys, logging

from sklearn.feature_extraction import DictVectorizer
import numpy as np
from scipy import sparse

# 需要安装Python的lda包，地址:https://pypi.python.org/pypi/lda
import lda

class TopicFeature(object):
    '''
        将文本转化为主题空间中的向量
        parameters
        ------------
        n_topics: the number of topics
        n_iter: the number of iterations
        n_merge: the number of same label snippets merged into one doc 
        max_freq: the max frequency after merging
        shffle: wheather shffle the data before merging
    
    def __init__(self, n_topics=30, n_iter=200, random_state=1, n_merge=50, max_freq=100, shuffle=True):
        self.n_topics = n_topics
        self.n_iter = n_iter
        self.random_state = random_state
        self.model = lda.LDA(n_topics=self.n_topics, n_iter=self.n_iter, random_state=self.random_state)
        self.n_merge = n_merge    
        self.max_freq = max_freq
        self.shuffle = True
    '''
    def __init__(self, user_params={}):
        params = user_params
        self.n_topics = 30
        self.n_iter = 100
        self.random_state = 1
        self.n_merge = 50
        self.max_freq = 100
        self.shuffle = True
    
        param_lst = ['n_topics', 'n_iter', 'random_state', 'n_merge', 'max_freq', 'shuffle']
        for key,value in params.iteritems():
            if not key in param_lst:
                logging.warn('Invalid parameter %s ' 'for estimator %s' % (key, self.__class__.__name__))
                continue
            try:
                value = int(value)
            except:
                logging.warn('params %s is not integer' %value)
            setattr(self, key, value)        
    
        self.model = lda.LDA(n_topics=self.n_topics, n_iter=self.n_iter, random_state=self.random_state)

    def X_merge(self, X, y):
        '''
            相同标签的短文本合并成文档
        '''
        y_vals = np.unique(y)
        doc_feats = []
      
        # 短文本合并前将数据打散
        # np.random.seed(seed=1234)
        if self.shuffle:
            idx = np.random.permutation(X.shape[0])
            X = X[idx]
            y = y[idx]

        n_merge = self.n_merge
        #print '**', X.shape, y.shape
        for yi in y_vals:
            indx = np.nonzero(y == yi)[0]
            n_doc = np.ceil(indx.shape[0]*1.0 / n_merge).astype(int)
            for i in xrange(n_doc):
                X_indx = indx[n_merge*i:n_merge*(i+1)] 
                if X_indx.shape[0] < 1:
                    continue
                Xone = X[X_indx,:].sum(axis=0)
                Xone[np.nonzero(Xone>self.max_freq)[0]] = self.max_freq
                Xone = sparse.csr_matrix(Xone)
                doc_feats.append(Xone)
        Xt = sparse.vstack(doc_feats, format='csr')
        return Xt
       
    def fit(self, X, y):
        Xt = self.X_merge(X, y)
        self.model.fit(Xt)        

    def fit_transform(self, X, y, max_iter=20, tol=1e-6):
        self.fit(X, y)
        feats_lst = self.transform(X, max_iter, tol)
        return feats_lst

    def transform(self, X, max_iter=20, tol=1e-16):
        #b = X.toarray()
        #t_feats = self.model.transform(b.astype(np.int32), max_iter=max_iter, tol=tol)
        feats_lst = []
        for i in xrange(X.shape[0]):
            b = X[i].toarray().astype(np.int32)
            t_feats = self.model.transform(b, max_iter=max_iter, tol=tol)
            feats_lst.append(t_feats[0])
        feats_lst = np.array(feats_lst)
        #print feats_lst.shape
        return feats_lst

    def model_topic_word(self, dict_vectorizer, n_top_words=10):
        '''
            获取每个主题下的相关词
        '''
        topic_word = self.model.topic_word_
        feat_words = dict_vectorizer.get_feature_names()
        for i, topic_dist in enumerate(topic_word):
            topic_words = np.array(feat_words)[np.argsort(topic_dist)][:-n_top_words:-1]
            print('Topic {}: {}'.format(i, ' '.join(topic_words).encode('utf-8')))

    def model_doc_topic(self):
        '''
            获取文档主题矩阵
        '''
        doc_topic = self.model.doc_topic_
        return doc_topic

    def get_params(self, deep=True):
        params = {
            'n_iter'   : self.n_iter,
            'n_topics' : self.n_topics,
            'n_merge'  : self.n_merge,
            'max_freq' : self.max_freq,
            'shuffle': self.shuffle
        }
        return params

    def set_params(self, **params):
        if not params:
            return self
        valid_params = self.get_params()
        for key, value in params.iteritems():
            if not key in valid_params:
                raise ValueError('Invalid parameter %s ' 'for estimator %s'
                                 % (key, self.__class__.__name__))
            setattr(self, key, value)  

if __name__ == '__main__':
    pass 
