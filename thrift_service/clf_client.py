#!/usr/bin/python 
# -*- coding: UTF-8 -*- #

import json
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')
cur_dir = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
sys.path.append(cur_dir + '/gen-py')

from classification_service import ClassificationService

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

import config

class ClfClient():
    def __init__(self):
        transport = TSocket.TSocket(config.IP, config.PORT)
        self.transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = ClassificationService.Client(protocol)
        self.transport.open()

    def test_client(self, json_text):
        json_res = self.client.data_process(json_text)

        return json_res

    def __del__(self):
        self.transport.close()

if __name__=='__main__':
    clf_client = ClfClient()

    json_text = json.dumps({'ID':'工单ID', 'description':'问题描述文本'})
    res = clf_client.test_client(json_text)
    print '\n', res, '\n'

    
