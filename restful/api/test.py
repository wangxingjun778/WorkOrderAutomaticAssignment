import sys, os
import json
import traceback
reload(sys)
sys.setdefaultencoding( "utf-8")
cur_dir = os.path.dirname( os.path.abspath(__file__)) or os.getcwd()
par_dir = os.path.dirname(os.path.dirname(cur_dir))
sys.path.append(par_dir)

print cur_dir
print par_dir
