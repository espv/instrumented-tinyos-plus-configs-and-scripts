
import os
import re
import sys

import matplotlib.pyplot as plt

corrected = False
if len(sys.argv) > 1 and sys.argv[1] == "corrected":
	corrected = True

ns3_points = {}
if len(sys.argv) > 2:
	ns3_point_file = open(sys.argv[2], "r")
	for l in ns3_point_file:
		plot_index = int(l.split()[0])
		ps = int(l.split()[1])
		pps = int(l.split()[2])
		point = int(l.split()[3].split('.')[0])
		ns3_points.setdefault(plot_index, {}).setdefault(ps, {})[pps] = point

dir_name = "all_contexts"
if corrected:
	dir_name = "corrected_all_contexts"


all_context_files = os.listdir(dir_name)
all_23s = {}
all_sfds = {}
for fn in all_context_files:
	# file = "pps<x>ps<y>_exploratory.txt, and we want <y>
	ps = re.split("pps\d+psize|_exploratory", fn)[1]
	# file = "pps<x>ps<y>_exploratory.txt, and we want <x>
	pps = re.split("pps|psize", fn)[1]
	f = open(dir_name+"/"+fn, "r")
	#output = open("real_plots/"+fn+"_plot.png")
	number_23s = 0
	number_sfds = 0
	number_ip_layer_drops = 0
	number_ip_layer_packets = 0
	number_bad_crc_drops = 0
	number_sent = 0
	number_rxfifo_flushes = 0
	for l in f:
		if " 23" in l:
			number_23s += 1
		if " 91" in l:
			number_sfds += 1
		if " 14" in l:
			number_ip_layer_drops += 1
		if " 40" in l:
			number_ip_layer_packets += 1
		if " 12" in l:
			number_bad_crc_drops += 1
		if " 66" in l:
			number_sent += 1
		if " 15" in l:
			number_rxfifo_flushes += 1
	all_23s.setdefault(ps, {})[pps] = {"number_23s": number_23s, "number_sfds": number_sfds, "number_ip_layer_drops": number_ip_layer_drops, "number_ip_layer_packets": number_ip_layer_packets, "number_bad_crc_drops": number_bad_crc_drops, "number_sent": number_sent}

res = {}
for ps, v in all_23s.iteritems():
	for k2, v2 in v.iteritems():
		res.setdefault(ps, []).append((k2, v2))

for r, v in res.iteritems():
	v = sorted(v, key=lambda x: float(x[0]))
	v_sfds = sorted(v, key=lambda x: float(x[0]))
	plt.title("Percentage forwarded packets - UDP payload size: " + r)
	arg1 = [int(a) for (a, b) in v if int(a) > 35]

	args = []
	number_23s_arg = [(b["number_23s"]/256.0)*100 for (a, b) in v if int(a) > 35]
	number_sfds_arg = [(b["number_sfds"]/256.0)*100 for (a, b) in v if int(a) > 35]
	number_ip_layer_drops_arg = [(b["number_ip_layer_drops"]/256.0)*100 for (a, b) in v if int(a) > 35]
	number_bad_crc_drops_arg = [(b["number_bad_crc_drops"]/256.0)*100 for (a, b) in v if int(a) > 35]
	number_sent_arg = [(b["number_sent"]/256.0)*100 for (a, b) in v if int(a) > 35]

	for plot_index, ps_points in ns3_points.iteritems():
		print "NS3 point file:", plot_index
		if plot_index != 1:  # Plot index 1 is line for % successfully forwarded
			continue
		if ps_points.get(int(r)):
			points = ps_points.get(int(r))
			coords = [(a, b) for a, b in points.iteritems()]
                        coords = sorted(coords, key=lambda x: float(x[0]))
			print coords
                        plt.plot([a for a, b in coords], [b for a, b in coords], label="Device model")

#	if ns3_points.get(int(r)):
#		for pps_points in ns3_points.get(int(r)):
			
		#pps_points = ns3_points.get(int(r))
#			coords = [(a, b) for a, b in pps_points.iteritems() if a > 35 and (r != "88" or int(a) < 95)]
#			coords = sorted(coords, key=lambda x: x[0])
#			plt.plot([a for a, b in coords], [b for a, b in coords], label="Device model")
#	plt.plot(arg1, number_23s_arg, label="Real mote")
#	plt.plot(arg1, number_sfds_arg, label="Number SFD received")
	#plt.plot(arg1, number_ip_layer_drops_arg, label="% dropped at IP layer")
#	plt.plot(arg1, number_bad_crc_drops_arg, label="Number bad CRC packets dropped")
	plt.plot(arg1, number_sent_arg, label="Real mote")
	plt.legend()

	plt.show()

