#coding:utf-8

import sys, os
import time
import json
from datetime import datetime

cur_dir = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
par_dir = os.path.abspath( cur_dir + "/../" )
sys.path.append(par_dir+'/classifier')
sys.path.append(par_dir+'/classifier/data_base')
from aquire_training_data import update_train_data_online
from core_process import Core_Process

reload(sys)
sys.setdefaultencoding('utf-8')

UPDATE_PERIOD = 30 * 24 * 60 * 60       # unit: (s) 默认更新周期为1个月
#UPDATE_PERIOD = 60                     # for test
MODEL_PATH = par_dir+'/classifier/model_result/' 
TRAIN_DATA_PATH = par_dir+'/classifier/data_base/' 


def read_local_train_data(file_path):
    """
    Input:
        file_path <string>: local train data path. 
    """
    l_res = []
    with open(file_path, 'r') as fp:
        for line in fp.readlines():
            line = json.loads(line)
            l_res.append(line)
    
    return l_res

def write_local_train_data(l_data, file_path):
    with open(file_path, 'w') as fp:
        for d_term in l_data:
            fp.write(json.dumps(d_term, ensure_ascii=False) + '\n')
    print "\n****Write the training data: ", file_path, "\n"
            
def get_train_data_all(process_obj):
    """
    Output: 
        d_res_all <dict>:  Ex: {model_name:[{},{},...], ...}
    """
    
    d_res_all = {}
    for model_name,pc_types in process_obj.d_model_map.items():
        #model_path = MODEL_PATH + 'model/' + model_name + '.model' 
        train_data_path = TRAIN_DATA_PATH + model_name + '.json' 
        pc_type_names, date_interval = pc_types.strip().split('|')
        l_pc_types = [i.strip() for i in pc_type_names.strip().split(',') if i.strip()]
        start_date, end_date = date_interval.strip().split(',')

        l_res_increment = []
        l_res_increment_str = []
        for pc_type in l_pc_types:
            l_res_increment += update_train_data_online(start_date, end_date, pc_type=pc_type)
        for d_data in l_res_increment:
            d_temp = {}
            d_temp['id'] = str(d_data['id']) 
            d_temp['description'] = str(d_data['description']) 
            d_temp['label'] = str(d_data['label'])   
            l_res_increment_str.append(d_temp)

        """
        try:
            l_res_local = read_local_train_data(train_data_path)
        except:
            l_res_local = []
        ## 本地数据与数据库取得的数据合并，去重 
        l_train_data_all = l_res_increment_str + l_res_local
        d_train_data_all = {}
        for d_data in l_train_data_all:
            d_train_data_all[d_data['id']] = d_data
        l_res_temp = [v for k,v in d_train_data_all.items()]
        d_res_all[model_name] = l_res_temp
        """

        d_res_all[model_name] = l_res_increment_str

    return d_res_all
    


def update_model(sleep_period):
    """
    Input:
        sleep_period  <int>: 更新模型的时间周期；单位：秒
    """
    CP_obj = Core_Process()
    d_train_data_all = get_train_data_all(CP_obj)

    ## 训练数据回写到本地，更新模型
    print "\nModel training ..."
    for model_name,l_train_data in d_train_data_all.items():
        if model_name == 'root':
            continue
        if not l_train_data:
            continue
        train_data_path = TRAIN_DATA_PATH + model_name + '.json' 
        write_local_train_data(l_train_data, train_data_path)
        CP_obj.train_all(train_data_path, model_name)


    ## 重载服务
    print "***Reload the service.\n"
    #CP_obj.__init__()
    

    ## 设置更新周期
    print "\nUpdate_model service is sleeping ...\n"
    time.sleep(sleep_period)
    


if __name__ == '__main__':
    
    #file_path = par_dir+'/classifier/data_base/train_data.json'
    #print read_local_train_data(file_path)    

    #update_model(sleep_period=UPDATE_PERIOD)
    while True:
        update_model(sleep_period=UPDATE_PERIOD)
    print "***The update_model service is stopped.\n"


