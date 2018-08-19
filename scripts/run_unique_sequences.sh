#!/bin/bash
full_log=""
for i in $( ls ); do
	if [ ${i: -4} == ".txt" ]; then
		log=""
		python ~/Master-thesis/scripts/unique_sequences.py $i 
#		echo "python $1 $i > $log"
		full_log+=$log
	fi
done
echo $full_log
