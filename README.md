This is a sub-system for work order automatic assignment. 


1. 启动/停止服务:
    启动： ./start_all.sh
    停止： ./stop_all.sh

2. 测试方法：
    (1) curl方式：
    curl -i -X POST -H "'Content-type':'application/x-www-form-urlencoded', 'charset':'utf-8', 'Accept': 'text/plain'" -d 'content={"ID":"工单ID", "description":"问题描述文本", "model_name":"ecc_model"}'  0.0.0.0:9898/para/

    (2) postman工具:
    POST: 172.18.1.146:9898/para/
    Body (x-www-from-urlencoded): 
        key   : content
        value : {"ID":"工单ID", "description":"问题描述文本", "model_name":"root"}
