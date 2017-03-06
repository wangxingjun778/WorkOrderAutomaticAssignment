ps aux | grep "clf_server.py" | grep -v grep | awk '{print $2}'| xargs kill -9
ps aux | grep "9898" | grep -v grep | awk '{print $2}'| xargs kill -9

ps aux | grep "auto_update_model" | grep -v grep | awk '{print $2}'| xargs kill -9
