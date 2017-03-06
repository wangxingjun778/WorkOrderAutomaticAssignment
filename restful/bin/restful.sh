#!/bin/bash

HOME=`dirname $(cd "$(dirname "$0")"; pwd)`
cd $HOME

while getopts "h" Option
do
case $Option in
h) echo "version: 'cat $HOME/VERSION'"
   echo "Usage: $0 <start|reload|stop>"
   exit
   ;;
esac
done
shift $(($OPTIND -1))

case $1 in
start)		/opt/Python-2.7.8/bin/uwsgi --python-path $HOME --pidfile $HOME/etc/uwsgi.pid -x $HOME/etc/restful.xml;;
reload)		/opt/Python-2.7.8/bin/uwsgi --reload $HOME/etc/uwsgi.pid;;
stop)		/opt/Python-2.7.8/bin/uwsgi --stop $HOME/etc/uwsgi.pid; rm -f $HOME/etc/uwsgi.pid;;
esac
