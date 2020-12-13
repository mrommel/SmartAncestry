#!/bin/sh
#
# description: node servers
#
bar_pidfile=./bar.pid
ancestry_pidfile=./ancestry.pid
python_pidfile=./python.pid

if [ -f $bar_pidfile ]
then
	bar_pid=`cat $bar_pidfile`
fi

if [ -f $ancestry_pidfile ]
then
	ancestry_pid=`cat $ancestry_pidfile`
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

		if [ -f $ancestry_pidfile ] ; then
				if test `ps -e | grep -c $ancestry_pid` = 2; then
						echo "Not starting ancestry - instance already running with PID: $ancestry_pid"
				else
						echo "Starting ancestry"
						cd data/static/data/js/
						node ./ancestry.js &> ./../../../../ancestry.log &
						cd ../../../..
						echo $! > $ancestry_pidfile
				fi
		else
				echo "Starting ancestry"
				cd data/static/data/js/
				node ./ancestry.js &> ./../../../../ancestry.log &
				cd ../../../..
				echo $! > $ancestry_pidfile
		fi
		
		if [ -f $python_pidfile ] ; then
				if test `ps -e | grep -c $python_pid` = 2; then
						echo "Not starting python - instance already running with PID: $python_pid"
				else
						echo "Starting python"
						#deactivate
						#workon venv
						python3 manage.py runserver 127.0.0.1:7000 &> ./python.log &
						echo $! > $python_pidfile
						sleep 5
				fi
		else
				echo "Starting python"
				python3 manage.py runserver 127.0.0.1:7000 &> ./python.log &
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
		
		if [ -f $ancestry_pidfile ] ; then
				echo "stopping ancestry"
				kill -9 $ancestry_pid
		else
				echo "Cannot stop ancestry - no Pidfile found!"
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
		
		if [ -f $ancestry_pidfile ] ; then
				if test `ps -e | grep -c $ancestry_pid` = 1; then
						echo "ancestry not running"
				else
						echo "ancestry running with PID: [$ancestry_pid]"
				fi
		else
				echo "$ancestry_pidfile does not exist! Cannot process ancestry status!"
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