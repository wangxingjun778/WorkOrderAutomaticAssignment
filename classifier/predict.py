#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys, logging, json, os, traceback

try:
    import cPickle as pickle
except:
    import pickle

cur_dir = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
sys.path.append(cur_dir)

class Predict(object):
    """
    预测类
    """
    def __init__(self):
        pass

    def load_model(self, model_file):
        """
        load model from disk
        """
        fp = open(model_file, "r")
        (self.pipeline, self.label_encoder) = pickle.load(fp)
        logger = logging.getLogger("lda")
        logger.setLevel(logging.ERROR)
        fp.close()
        self.init_test()
        #print '>'*10, self.label_encoder
        #print '='*10, 'Done init_test !'

    def init_test(self):
        """
        Initialize model to predict
        """
        self.vectorizer =  self.pipeline.named_steps['vec']
        self.feature_select = self.pipeline.named_steps['feat']
        self.clf = self.pipeline.named_steps['clf']
        self.cates = self.label_encoder.classes_
        self.features_support = self.feature_select.get_support_features()
        self.features_support_dict = {}
        for i in range(len(self.features_support)):
            self.features_support_dict[self.features_support[i]] = i
        self.word_dict = {str(value): key for key, value in self.vectorizer.vocabulary_.items()}
        

    def predict(self, features):
        '''
        input(dict type): features    Ex: {xx:1, xxx:2, ...}
        output(string type): predict-label  Ex: L1, ...
        '''
        result = ''
        try:
            target = self.pipeline.predict(features)
            #self.print_distance(features)
            #self.print_prob(features)
            #self.print_features_distance(features)
            result = self.label_encoder.classes_[target[0]]
            #print "reuslt:%s"%result
        except Exception, e:
            traceback.print_exc()
            logging.error("Error: %s" %json.dumps(features, ensure_ascii=False).encode('u8') )
            logging.error(e)
        return unicode(result)

    def print_distance(self, features):
        """
        print distances from given features to support vector
        """
        try:
            distances = self.pipeline.decision_function(features)
            for i in range(len(distances[0])):
                print >> sys.stderr, '%s %s' %(self.label_encoder.classes_[i], distances[0][i])
        except Exception as e:
            traceback.print_exc()

    def print_prob(self, features):
        """
        Brief: print the probability of prediction.
        """
        try:
            prob = self.pipeline.predict_proba(features)
            for i in range(len(prob[0])):
                print >> sys.stderr, '%s\t%s' %(self.label_encoder.classes_[i], prob[0][i])
        except Exception as e:
            traceback.print_exc()

    def print_features_distance(self, features):
        try:
            # get distances from given point to each support vector
            distances = self.pipeline.decision_function(features)
        except Exception as e:
            traceback.print_exc()
        feature_coef = {}
        for i in range(len(self.cates)):
            if not feature_coef.has_key(self.cates[i]):
                feature_coef[self.cates[i]] = {}
            for v in features:
                try:
                    feature_coef[self.cates[i]][v] = self.clf.coef_[i][self.features_support_dict[self.vectorizer.vocabulary_[v]]]
                except Exception as e:
                    pass
                    #traceback.print_exc()
        print "------------------------------------------"
        for i in range(len(feature_coef.keys())):
            c = feature_coef.keys()[i]
            print '%s\t%s'%(c,distances[0][i])
            _list = [f+'  '+str(v) for f,v in feature_coef[c].items()]
            print '\t%s'%(','.join(_list))
        print "------------------------------------------"
        

    def predict_prob_one(self, features):
        decision = self.pipeline.decision_function(features)
        if decision.ndim == 1:
            df = [0, decision.item()]
            args = [0, 1] if df[1] > 0 else [1, 0]
        else:
            df = decision.tolist()[0]
            args = decision.argsort().tolist()[0]
        args.reverse()




if __name__ == '__main__':
    test_predict = Predict()

    model_dir = cur_dir + '/model_result/model/root.model' 
    test_predict.load_model(model_dir)

    #features = {u'respond': 1, u'MySpace': 1, u'help': 4, u'just': 1, u'feel': 1, u'0bitchbd': 1, u'img': 1, u'it': 1, u'chear': 1, u'quotes': 1, u'say': 1, u'href': 2, u'thanks': 1, u'blank': 2, u'Comments': 1, u'sounds': 1, u'border': 1, u'out': 1, u'iam': 3, u'Girly': 1, u'figure': 1, u'would': 1, u'gif': 1, u'Quote': 1, u'self': 1, u'lke': 1, u'had': 1, u'how': 1, u'blingcheese': 2, u'way': 1, u'silly': 1, u'sme': 1, u'today': 1, u'happy': 1, u'me': 1, u'towards': 1, u'i153': 1, u'src': 1, u'similar': 1, u'but': 1, u'know': 1, u'br': 1, u'graphics': 1, u'albums': 1, u'why': 1, u'photobucket': 1, u'extreamly': 1, u'advance': 1, u'target': 2, u's235': 1, u'thou': 1, u'maybe': 1, u'could': 1, u'title': 1, u'eve': 1, u'honest': 1, u'so': 1, u'revmyspace2': 1, u'situation': 1, u'feeling': 2, u'my': 2, u'think': 1, u'mad': 1}

    #features = {u'it': 1, u'heard': 1, u'Abu': 1, u'sell': 1, u'fee': 1, u'NHA': 1, u'there': 2, u'charge': 1, u'Hamour': 1, u'station': 1, u'health': 1, u'take': 1, u'only': 1, u'get': 1, u'petrol': 1, u'but': 1, u'child': 1, u'properties': 1, u'card': 4, u'qr': 1, u'vaccinating': 1, u'taking': 1, u'near': 1, u'green': 3, u'my': 1}
 
    features = {u'customer': 1, u'good': 1, u'service': 1, u'very': 1, u'excellent': 1, u'IBQ': 1}

    predict_result = test_predict.predict(features)
    print type(predict_result), predict_result


