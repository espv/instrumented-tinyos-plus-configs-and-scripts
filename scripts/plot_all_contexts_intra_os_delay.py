
import os
import re
import sys

import matplotlib.pyplot as plt

corrected = False
if len(sys.argv) > 1 and sys.argv[1] == "corrected":
	corrected = True

dir_name = "all_contexts"
if corrected:
	dir_name = "corrected_all_contexts"

all_context_files = os.listdir(dir_name)
print "all_context_files:", all_context_files

ns3_points = {}
if len(sys.argv) > 2:
        ns3_point_file = open(sys.argv[2], "r")
        for l in ns3_point_file:
                plot_index = int(l.split()[0])
                ps = int(l.split()[1])
                pps = int(l.split()[2])
                point = int(l.split()[3].split('.')[0])
                ns3_points.setdefault(plot_index, {}).setdefault(ps, {})[pps] = point

def add_new_packet(packets, l):
#        try:
    packets.append([(int(l.split()[1]), int(l.split()[0]))])
#        except ValueError:
#            print "ValueError"
#            return

def add_to_oldest_packet(packets, l, nth_oldest_packet=1, log=False):
	i = 0
	for p in packets:
		#print "p:", p
		if log is True:
			print l
        	if p[-1][0] not in [12, 14, 66]:
			i += 1
			if i != nth_oldest_packet:
				continue
#			try:
               		p.append((int(l.split()[1]), int(l.split()[0])))
#			except ValueError:
#				pass
			return p

def add_to_newest_packet(packets, l, required_number_of_traces=1):
        for p in reversed(packets):
                if len(p) == required_number_of_traces and p[-1][0] not in [12, 14, 66]:
                        p.append((int(l.split()[1]), int(l.split()[0])))
                        return p

def index_of_id(packet, trace_id):	
	for i, trace in enumerate(packet):
		if trace[0] == trace_id:
			return i
	return -1

number0s = 0
number23s = 0
total_intra_os_delay = {}
for fn in all_context_files:
	# file = "pps<x>ps<y>_exploratory.txt, and we want <y>
	ps = re.split("pps\d+psize|_exploratory", fn)[1]
	# file = "pps<x>ps<y>_exploratory.txt, and we want <x>
	pps = re.split("pps|psize", fn)[1]
	f = open(dir_name+"/"+fn, "r")
	#output = open("real_plots/"+fn+"_plot.png")
	packets = []
	intra_os_delay = []
	if fn == "pps129psize44_exploratory.txt":
		print f

	cnt = 0
	for l in f:
#		print f, l
#		if len(l.split()) < 2 or l.split()[1] == '':
#			continue
		if " 91" in l or " 0" in l or " 1\n" in l:
			number0s += 1
			add_new_packet(packets, l)
		elif " 0" in l:
			# We use 0 to calculate beginning of intra-OS delay
			add_to_newest_packet(packets, l, required_number_of_traces=1)
		elif " 23" in l: 
			# We use 23 to calculate end of intra-OS delay
			p = add_to_oldest_packet(packets, l)
			if p is None:
#				print "Skipping packet with 23"
                        	continue
			number23s += 1
#                        intra_os_delay.append(p[-1][1]-p[0][1])
		elif " 14" in l:
			# nth_oldest_packet=4 because the IP layer queue has 3 entries. The trace
			# means that the packet could not fit in the queue, and therefore there must be 4
			# packets that are not sent yet.
			if fn == "pps129psize44_exploratory.txt":
				p = add_to_oldest_packet(packets, l, nth_oldest_packet=4, log=True)
			else:
				p = add_to_oldest_packet(packets, l, nth_oldest_packet=4)
			if p is None:
				print "14 packet does not exist"
				continue
			if fn == "pps129psize44_exploratory.txt":
				print p
#			intra_os_delay.append(p[-1][1]-p[0][1])
		elif " 12" in l:
			p = add_to_newest_packet(packets, l, required_number_of_traces=1)
			if p is None:
				print "12 packet does not exist"
				continue
#			intra_os_delay.append(p[-1][1]-p[0][1])
		elif " 66" in l:
			# Look for the first packet that has not been sent
			p = add_to_oldest_packet(packets, l)
			# We subtract the first 23 trace with the second trace (0).
			# We don't count subsequent 23 traces. They occur because the channel is not clear.
			if p is None:
				print "66 packet does not exist"
				continue
			if fn == "pps129psize44_exploratory.txt":
				cnt += 1
				print cnt, p
#			if abs(p[index_of_id(p, 23)][1]-p[0][1]) > 90000*4200:
#				continue
			intra_os_delay.append(p[index_of_id(p, 23)][1]-p[0][1])
#			intra_os_delay.append(p[-2][1]-p[0][1])
		
	intra_os_delay = sorted([x for x in intra_os_delay])
	if fn == "pps129psize44_exploratory.txt":
		print "pps129psize44_exploratory.txt:", intra_os_delay
	if len(intra_os_delay) == 0:
		continue
#	print f, "Intra os delay:", intra_os_delay
	intra_os_delay = {"min": intra_os_delay[0], "median": intra_os_delay[len(intra_os_delay)/2], "max": intra_os_delay[-1], "avg": sum(intra_os_delay)/float(len(intra_os_delay))}

	total_intra_os_delay.setdefault(ps, {})[pps] = intra_os_delay

print total_intra_os_delay

for ps, v in total_intra_os_delay.iteritems():
#	v = sorted(v, key=lambda x: float(x[0]))
	v_max = [(int(a), int(b["max"])) for a, b in v.iteritems()]
	v_max = sorted(v_max, key=lambda x: x[0])
	v_median = [(int(a), int(b["median"])) for a, b in v.iteritems()]
	v_median = sorted(v_median, key=lambda x: x[0])
	v_avg = [(int(a), int(b["avg"])) for a, b in v.iteritems()]
	v_avg = sorted(v_avg, key=lambda x: x[0])
	v_min = [(int(a), int(b["min"])) for a, b in v.iteritems()]
	v_min = sorted(v_min, key=lambda x: x[0])
#	v_sfds = sorted(v, key=lambda x: float(x[0]))
	plt.title("Intra os delay with packet size: " + ps)
#	if corrected:
	arg1 = [a for (a, b) in v_median if a > 30 and a < 150]
#	else:
#		print "v_median:", v_median
#		print "ps:", ps
#		arg1 = [1/(float(a)/4200000000.0) for (a, b) in v_median]
	for plot_index, ps_points in ns3_points.iteritems():
                if plot_index != 1:  # Plot index 1 is line for % successfully forwarded
                        continue
                if ps_points.get(int(ps)):
                        points = ps_points.get(int(ps))
                        coords = [(a, b) for a, b in points.iteritems() if a > 35]
                        coords = sorted(coords, key=lambda x: float(x[0]))
#			print "Coords:", coords
                        plt.plot([a for a, b in coords], [b for a, b in coords], label="Device model")

	args = []
	max_intra_os_delay_arg = [b for (a, b) in v_max if a > 30 and a < 150]
	median_intra_os_delay_arg = [b for (a, b) in v_median  if a > 30 and a < 150]
	avg_intra_os_delay_arg = [b for (a, b) in v_avg  if a > 30 and a < 150]
	min_intra_os_delay_arg = [b for (a, b) in v_min  if a > 30 and a < 150]

#	plt.plot(arg1, max_intra_os_delay_arg, label="Max intra os delay")
#	plt.plot(arg1, median_intra_os_delay_arg, label="Median intra os delay")
	#plt.plot(arg1, avg_intra_os_delay_arg, label="Average intra os delay")
	plt.xlabel('pps')
	plt.ylabel('Intra-OS delay')
	print "avg:", avg_intra_os_delay_arg
	plt.plot(arg1, avg_intra_os_delay_arg, label="Real mote")
#	plt.plot(arg1, min_intra_os_delay_arg, label="Min intra os delay")
#	plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
	plt.legend()

	plt.show()


