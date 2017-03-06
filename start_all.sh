nohup python thrift_service/clf_server.py 2 &
nohup python restful/manage.py runserver 0.0.0.0:9898 &

nohup python -u thrift_service/auto_update_model.py &
