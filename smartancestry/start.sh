#!/bin/sh
#
# description: node servers
#
bar_pidfile=./bar.pid
tree_pidfile=./tree.pid
python_pidfile=./python.pid

if [ -f $bar_pidfile ]
then
	bar_pid=`cat $bar_pidfile`
fi

if [ -f $tree_pidfile ]
then
	tree_pid=`cat $tree_pidfile`
fi

if [ -f $python_pidfile ]
then
	python_pid=`cat $python_pidfile`
fi

# Start the service node
start() {
		echo "Starting node/python servers: "
		if [ -f $bar_pidfile ] ; then
				if test `ps -e | grep -c $bar_pid` = 2; then
						echo "Not starting bar - instance already running with PID: $bar_pid"
				else
						echo "Starting bar"
						cd data/static/data/js/
						node ./bar.js &> ./../../../../bar.log &
						cd ../../../..
						echo $! > $bar_pidfile
				fi
		else
				echo "Starting bar"
				cd data/static/data/js/
				node ./bar.js &> ./../../../../bar.log &
				cd ../../../..
				echo $! > $bar_pidfile
		fi
		
		if [ -f $tree_pidfile ] ; then
				if test `ps -e | grep -c $tree_pid` = 2; then
						echo "Not starting tree - instance already running with PID: $tree_pid"
				else
						echo "Starting tree"
						cd data/static/data/js/
						node ./tree.js &> ./../../../../tree.log &
						cd ../../../..
						echo $! > $tree_pidfile
				fi
		else
				echo "Starting tree"
				cd data/static/data/js/
				node ./tree.js &> ./../../../../tree.log &
				cd ../../../..
				echo $! > $tree_pidfile
		fi
		
		if [ -f $python_pidfile ] ; then
				if test `ps -e | grep -c $python_pid` = 2; then
						echo "Not starting python - instance already running with PID: $python_pid"
				else
						echo "Starting python"
						python manage.py runserver &> ./python.log &
						echo $! > $python_pidfile
						sleep 5
				fi
		else
				echo "Starting python"
				python manage.py runserver &> ./python.log &
				echo $! > $python_pidfile
				sleep 5
		fi
		
        echo "node/python servers startup"
        echo
}
# Restart the service node
stop() {
        echo "Stopping node/python servers: "
        if [ -f $bar_pidfile ] ; then
				echo "stopping bar"
				kill -9 $bar_pid
		else
				echo "Cannot stop bar - no Pidfile found!"
		fi
		
		if [ -f $tree_pidfile ] ; then
				echo "stopping tree"
				kill -9 $tree_pid
		else
				echo "Cannot stop tree - no Pidfile found!"
		fi
		
		if [ -f $python_pidfile ] ; then
				echo "stopping python"
				kill -9 $python_pid
				
				killall Python
		else
				echo "Cannot stop python - no Pidfile found!"
		fi
		
		echo "node/python servers stopped"
        echo
}
status() {
		if [ -f $bar_pidfile ] ; then
				if test `ps -e | grep -c $bar_pid` = 1; then
						echo "bar not running"
				else
						echo "bar running with PID: [$bar_pid]"
				fi
		else
				echo "$bar_pidfile does not exist! Cannot process bar status!"
		fi
		
		if [ -f $tree_pidfile ] ; then
				if test `ps -e | grep -c $tree_pid` = 1; then
						echo "tree not running"
				else
						echo "tree running with PID: [$tree_pid]"
				fi
		else
				echo "$tree_pidfile does not exist! Cannot process tree status!"
		fi
		
		if [ -f $python_pidfile ] ; then
				if test `ps -e | grep -c $python_pid` = 1; then
						echo "python not running"
				else
						echo "python running with PID: [$python_pid]"
				fi
		else
				echo "$python_pidfile does not exist! Cannot process python status!"
		fi
}

### main logic ###
case "$1" in
  start)
        start
        ;;
  stop)
        stop
        ;;
  status)
        status
        ;;
  restart|reload|condrestart)
        stop
        sleep 5
        start
        ;;
  *)
        echo $"Usage: $0 {start|stop|restart|reload|status}"
        exit 1
esac
exit 0