#!/usr/bin/env python
#coding:utf-8



import sys, os
import json
import traceback
reload(sys)
sys.setdefaultencoding( "utf-8")
cur_dir = os.path.dirname( os.path.abspath(__file__)) or os.getcwd()
par_dir = os.path.dirname(os.path.dirname(cur_dir))
sys.path.append(par_dir)
sys.path.append(par_dir + '/thrift_service' + '/gen-py')
sys.path.append(par_dir + '/thrift_service')

from django.http import HttpResponse        
from django.views.decorators.csrf import csrf_exempt

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

    def data_predict(self, json_text):
        json_res = self.client.data_process(json_text)
        return json_res

    def __del__(self):
        self.transport.close()




@csrf_exempt   
def para(request):

    try:
        clf_obj = ClfClient()
         
        if request.method == 'POST':
            json_content = request.POST.get('content')
            d_content = json.loads(json_content)
            out_data = clf_obj.data_predict(json.dumps(d_content))

        return HttpResponse(out_data, content_type="json")

    except Exception as e:
        print "error",e
        traceback.print_exc()
        state_code = 0
        out_data = {
                'state':'Error !',
                'state_code':state_code,
                'debug_info':str(e)
        }
        return HttpResponse(json.dumps(out_data), content_type="json")



