
import os
import re

all_context_files = os.listdir("all_contexts")

for fn in all_context_files:
        # file = "pps<x>ps<y>_exploratory.txt, and we want <y>
        ps = re.split("pps\d+ps|_exploratory", fn)[1]
        # file = "pps<x>ps<y>_exploratory.txt, and we want <x>
#        pps = 1/(int(re.split("pps|ps", fn)[1])/1000)
        pps = int(re.split("pps|ps", fn)[1])
        f = open("all_contexts/"+fn, "r")
	print "Reading", f
	first_time = 0
	last_time = 0
        for l in f:
                if first_time == 0:
			first_time = int(l.split()[0])
		if l.split()[1] == "91" or l.split()[1] == "0":
			last_time = int(l.split()[0])
	f.close()
	# Currently, 91 is the SFD trace, which means when we receive the first bytes of a packet
	print "last_time - first_time:", last_time-first_time
	try:
		corrected_pps = int(1/(((last_time-first_time)/256.0)/4200000000.0))
	except ZeroDivisionError:
		continue
	print "Corrected pps:", corrected_pps
	# We skip the file if the pps was decreased 
	if corrected_pps < int(pps)-10:
		continue
	
	print "corrected_pps", corrected_pps, "arg 2:", ((last_time-first_time)/256.0)/1000000.0
        output = open("corrected_all_contexts/"+re.sub("pps\d+ps", "pps"+str(corrected_pps)+"ps", fn), "w+")
	print "Wrote to file:", "corrected_all_contexts/"+re.sub("pps\d+ps", "pps"+str(corrected_pps)+"ps", fn)
	print "Original file:", fn
        number_23s = 0
	f = open("all_contexts/"+fn, "r")
        for l in f:
                output.write(l)

	output.close()
	f.close()

