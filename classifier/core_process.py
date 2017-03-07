#!/usr/bin/env python
# -*- coding:utf-8 -*- 

import sys, os, json, logging, time, traceback
from preprocess.preprocess import Preprocess
from train import Train
from predict import Predict
cur_dir = os.path.dirname( os.path.abspath(__file__)) or os.getcwd()
CONFIG_FILE = cur_dir + '/classifier.cfg'
TRAIN_FILE_PATH = cur_dir + '/data_base/'
MODEL_PATH = cur_dir + '/model_result/' 


class Core_Process(object):
    """
    Func: training and predict process.
    """
    def __init__(self, model_name='root', opt='train'):
        
        self.model_name = model_name
        self.preprocess = Preprocess(CONFIG_FILE)
        self.d_model_map = self.preprocess.d_models

        if opt == 'predict':
            self.predict_obj = Predict()
            if self.d_model_map.get(self.model_name, None):
                self.predict_obj.load_model(MODEL_PATH + 'model/' + self.model_name + '.model')
            else:
                self.predict_obj.load_model(MODEL_PATH + 'model/' + 'root.model')
                print "\nNote: using the default model--root.model to predict.\n"
                


        self.train_features = []
        self.train_labels = []   

        self.predict_features = []
        self.predict_labels = []
  
        self.predict_data_id = []
        self.predict_result = []
            
    def load_data_path(self, data_path):
        """
        Input: 
            data_path <string>: the input file path.
        Output:
            None
        """
        print data_path
        fp = open(data_path, 'r')
        for json_line in fp.readlines():
            d_line = json.loads(json_line)
           
            data_id = d_line['id']
            desc_text = ' '.join(d_line['description'].replace('.', ' ').split())
            labels    = d_line['label']
            features = self.preprocess.process(title='', content=desc_text, model_name=self.model_name)
           
            self.train_features.append(features)
            self.train_labels.append(labels)

            self.predict_data_id.append(data_id)

        fp.close()    

        if len(self.train_features) == len(self.train_labels):
            pass
            #print '=========', len(self.train_features), len(self.train_labels)
        else:
            print 'ERROR: len(train_features) != len(train_labels)'

        
         
    def train_all(self, train_data_dir, model_name='root'):
        """
        train model with all training dataset, use model 'root' by default
        """
        self.load_data_path(train_data_dir)

        print >> sys.stderr, "train the model", train_data_dir
     
        space = 'word'
        #space = 'topic'    # There are some problems ? 
        _train = Train(space, {})
        _train.train(self.train_features, self.train_labels)

        if not os.path.exists(os.path.join(MODEL_PATH, 'model')):
            os.makedirs(os.path.join(MODEL_PATH, 'model'))
        if not os.path.exists(os.path.join(MODEL_PATH, 'report')):
            os.makedirs(os.path.join(MODEL_PATH, 'report'))
        if not os.path.exists(os.path.join(MODEL_PATH, 'feature')):
            os.makedirs(os.path.join(MODEL_PATH, 'feature'))        

        model_path = MODEL_PATH + 'model/' + model_name + ".model"
        print >> sys.stderr, "dump the model", model_path
        _train.dump_model(model_path)
        
      
        feature_file = os.path.join(MODEL_PATH, 'feature/'+model_name+".feature")

        #输出选择的特征及系数
        ffile = open(feature_file, 'w')
        feature_coef =  _train.get_feature_coef()
        print "----------len featrue coef:",len(feature_coef)
        feature_len = 0
        for cate in feature_coef:
            print "-------------",cate
            print >> ffile, "%s" %(cate.encode('u8'))
            features = sorted(feature_coef[cate].items(), key=lambda x:x[1], reverse=True)
            feature_len = len(features)
            for f_item in features:
                print >> ffile, "\t%s\t%f" %(f_item[0].encode('u8'), f_item[1])
        ffile.close()
        print >> sys.stderr, "%d features has been selected!" %feature_len
    
    def evaluation(self,  predict_file):
        """
        Func: evaluation of batch data.
        Input:
            predict_file <string>: input file path.
        Output:
            precision <float>: the precision of the prediction .
        """
        d_eval = {'corr':0}
        all_cnt = 0
        precision = 0.0

        self.load_data_path(predict_file)
        self.predict_features = self.train_features
        self.predict_labels = self.train_labels
        all_cnt = len(self.predict_labels)

        for features,label in zip(self.predict_features, self.predict_labels):
            result = self.predict_obj.predict(features)
            if result == label:
                d_eval['corr'] += 1
            self.predict_result.append(result) 
        if all_cnt == 0:
            print 'ERROR: all_cnt of predict_file: 0 !' 
        else:
            precision = d_eval['corr']*1.0/all_cnt 
        

        print '========== all_cnt: ', all_cnt
        print '========== precision: ', precision

        return precision
              
    def run(self, opt, file_path):      
        """
        opt: to determine train or predict
        file_path: traning data.
        """
        if opt == 'train':
            for mod_name,values in self.d_model_map.items():
                self.train_all(file_path, mod_name)

        elif opt == 'predict':
            predict_file = file_path
            result = self.evaluation(predict_file)
            
            report_file = os.path.join(MODEL_PATH, 'report/'+self.model_name+".report")
            rfile = open(report_file, 'a')
            rfile.write(str(file_path + '  precision: ') + str(result) + '\n')
            rfile.close()
            with open(report_file + '.rep', 'w') as rf:
                for tid, res in zip(self.predict_data_id,self.predict_result):
                    rf.write(tid + '\t' + res + '\n')

        else:
            print 'Nothing to do, please input train or predict.'

    def predict_one(self, desc_text):
        """
        Func: predict single data.
        Input:
            desc_text <string>: description text of the single data.
        Output:
            result <string>: the label of the input text.
        """
        features = self.preprocess.process(title='', content=desc_text, model_name=self.model_name)
        result = self.predict_obj.predict(features)

        return str(result)
        

            

if __name__ == '__main__':
    print >> sys.stderr, "Usage1: python %s train(or predict)  train_filepath(or predict_filepath)" %sys.argv[0]
    print >> sys.stderr, "Usage2: python %s predict_one input_text" %sys.argv[0], "\n"

    if sys.argv[1] == 'train':
        opt = sys.argv[1]
        file_path = sys.argv[2]
        EN = Core_Process(opt='train')
        EN.run(opt, file_path)

    if sys.argv[1] == "predict":
	opt = sys.argv[1]
	file_path = sys.argv[2]
        model_name = sys.argv[3]    # see the classifier.cfg
	EN = Core_Process(model_name=model_name, opt=opt)
	EN.run(opt,file_path)	


    if sys.argv[1] == 'predict_one':
        EN = Core_Process(model_name='root', opt='predict')
        desc_text = sys.argv[2]
        res = EN.predict_one(desc_text)
        print '\n>>>result: ', res, '\n'


    print '******** Done *******'

