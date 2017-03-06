#!/usr/bin/python 
# -*- coding: UTF-8 -*- #

import json
import sys, os

cur_dir = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
par_dir = os.path.abspath( cur_dir + "/../" )
sys.path.append(cur_dir+'/gen-py')
sys.path.append(par_dir+'/classifier')
sys.path.append(par_dir+'/thrift_service')

from classification_service import ClassificationService
from core_process import Core_Process

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.server import TProcessPoolServer

from set_logger import set_logger
import logging

import config


class ClfServiceHandler(object):
    def __init__(self):
        #self.model_obj = Core_Process()
        pass

    def data_process(self, json_text):
        #print '>>>input json_text: ', json_text, '\n'

        try:
            d_content = json.loads(json_text)
            if d_content.get('ID', None):
                data_id = d_content['ID']
            else:
                data_id = ''

            if d_content.get('description', None):
                data_desc = d_content['description']
            else:
                data_desc = ''

            if d_content.get('model_name', None):
                data_model = d_content['model_name']
            else:
                data_model = 'root'


            if data_desc:
                self.model_obj = Core_Process(model_name=data_model, opt='predict')
                result = self.model_obj.predict_one(data_desc)

            ### OUT Ex: {"ID":"工单ID", "label":"L1", "code":1, "message":"接口调用成功"}
            d_res = {}
            d_res['ID'] = str(data_id)
            d_res['label'] = str(result)
            d_res['code'] = 1
            d_res['message'] = str('Success !')

            #print '>>>>d_res: ', d_res
            return json.dumps(d_res, ensure_ascii=False)

        except KeyError:
            logging.info('%s ERROR', json_text)
            return json.dumps([])



def usage():
    print "Usage:"
    print "python server.py  processNum."

if( len(sys.argv) != 2 ):
    usage()
else:
    set_logger(cur_dir + '/../logs/clf_server.log')
    handler = ClfServiceHandler()
    processor = ClassificationService.Processor(handler)
    transport = TSocket.TServerSocket(config.IP,int(config.PORT))
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = TProcessPoolServer.TProcessPoolServer(processor, transport, tfactory, pfactory)
    server.setNumWorkers(int(sys.argv[1]))

    print "Starting classification server..."
    server.serve()
    print "Classification server started!"

