#!/bin/sh
PID=$(ps aux | grep "server.py" | head -n 1 | awk '{print $2}')
echo $PID
for id in $PID
do
  kill -9 $id
  echo "process $id killed"
done
WENKU8_LOCAL=True python server.py &
