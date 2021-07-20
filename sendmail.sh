#!/bin/bash
max=$1
subj=$2
file=$3
today=$(date)
for i in {1..$max}
do
   echo -e "Subject:$subj $today" | /usr/sbin/sendmail -vt < $file
done
echo "Subject:$subj $today"