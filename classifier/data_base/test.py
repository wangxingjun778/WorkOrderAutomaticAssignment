#coding:utf-8

import os, sys, json

reload(sys)
sys.setdefaultencoding('utf-8')

cur_dir = os.path.dirname( os.path.abspath(__file__)) or os.getcwd()


def write_file(l_data, file_path):
    with open(file_path, 'w') as fp:
        for d_data in l_data:
            fp.write(json.dumps(d_data,ensure_ascii=False) + '\n')
        print "\n***Output Done: ", cur_dir + '/' + file_path

def process_file(in_file_path, out_file_path):
    l_res_all = []
    with open(in_file_path, 'r') as fp:
        data_id = 1
        for line in fp.readlines():
            d_res = {}
            d_line = json.loads(line)
            des   = d_line['description']
            label = d_line['label']

            if label == 'AO':
                label = 'OLS'

            d_res['id'] = str(data_id)
            d_res['description'] = des
            d_res['label'] = label

            data_id += 1

            l_res_all.append(d_res)
        l_res_all.append({'id':'0', 'description':'for training set', 'label':'other'})
        
    write_file(l_res_all, out_file_path)


if __name__ == '__main__':

    in_file_path  = sys.argv[1]
    out_file_path = sys.argv[2]
    process_file(in_file_path, out_file_path)




