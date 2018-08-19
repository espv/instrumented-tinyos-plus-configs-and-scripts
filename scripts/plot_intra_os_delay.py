
import os
import re
import sys

import matplotlib.pyplot as plt

corrected = False
if len(sys.argv) > 1 and sys.argv[1] == "corrected":
	corrected = True

#ns3_points = {}
ns3_points = []
if len(sys.argv) > 2:
        ns3_point_file = open(sys.argv[2], "r")
        for l in ns3_point_file:
                plot_index = int(l.split()[0])
		ns3_points.append(int(l.split()[1]))
#                ps = int(l.split()[1])
#                pps = int(l.split()[2])
#                point = int(l.split()[3].split('.')[0])
#                ns3_points.setdefault(plot_index, {}).setdefault(ps, {})[pps] = point
		

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
        	if p[-1][0] not in [132, 134, 166]:
			i += 1
			if i != nth_oldest_packet:
				continue
#			try:
               		p.append((int(l.split()[1]), int(l.split()[0])))
#			except ValueError:
#				pass
			return p

def add_to_newest_packet(packets, l, required_number_of_traces=1, last_trace=None):
        for p in packets:
		if last_trace is not None:
			if p[-1][0] != last_trace:
				continue
                if len(p) == required_number_of_traces and p[-1][0] not in [132, 134, 166]:
                        p.append((int(l.split()[1]), int(l.split()[0])))
                        return p

def index_of_id(packet, trace_id):	
	for i, trace in enumerate(packet):
		#print packet
		if trace[0] == trace_id:
			return i
	return -1

def empty_radio_queue(packets):
#	packets.empty()  # TEMPORARY
	for packet in packets:
		print packet
		if 140 not in [p[0] for p in packet]:
			packets.remove(packet)

number0s = 0
number23s = 0
total_intra_os_delay = {}
import sys
fn = sys.argv[1]
#ps = re.split("ps\d+_full.txt", fn)[1]
ps = ""
f = open(fn, "r")
packets = []
intra_os_delay = []
number_0s = 0

next_line_seqno = False
for i, l in enumerate(f):
	if next_line_seqno:
		next_line_seqno = False
		print "Seqno:", l
		p = add_to_newest_packet(packets, l, required_number_of_traces=3)
		print p
#	elif " 150" in l:
#		continue
#		next_line_seqno = True
#	elif " 191" in l:
#		number0s += 1
#		#add_new_packet(packets, l)
	elif " 131" in l:
#		add_to_newest_packet(packets, l, required_number_of_traces=1)
		# We use 0 to calculate beginning of intra-OS delay
		number_0s += 1
		add_new_packet(packets, l)
	elif " 133" in l: 
		# We use 23 to calculate end of intra-OS delay
		p = add_to_oldest_packet(packets, l)
		if p is None:
			print "Skipping packet with 23"
                       	continue
		number23s += 1
		print "p:", p
                intra_os_delay.append(p[-1][1]-p[0][1])
#		intra_os_delay.append((p[3], p[-1][1]-p[0][1]))
		packets.remove(p)
#	elif " 134" in l:
		# nth_oldest_packet=4 because the IP layer queue has 3 entries. The trace
		# means that the packet could not fit in the queue, and therefore there must be 4
		# packets that are not sent yet.
#		p = add_to_oldest_packet(packets, l, nth_oldest_packet=4)
#		if p is None:
#			print "14 packet does not exist"
#			continue
#		intra_os_delay.append(p[-1][1]-p[0][1])
#		packets.remove(p)
#	elif " 132" in l:
#		p = add_to_newest_packet(packets, l, required_number_of_traces=2)
#		if p is None:
#			print "12 packet does not exist"
#			continue
#		packets.remove(p)
#		intra_os_delay.append(p[-1][1]-p[0][1])
#	elif " 135" in l:
#		empty_radio_queue(packets)
	#	print "135"
	#	packets = []
#		pass
#	elif " 166" in l:
		# Look for the first packet that has not been sent
#		p = add_to_oldest_packet(packets, l)
		#p = packets[0]
		# We subtract the first 23 trace with the second trace (0).
		# We don't count subsequent 23 traces. They occur because the channel is not clear.
#		if p is None:
#			print "66 packet does not exist"
#			continue
#		print "p:", p
#		print "packets:", packets
#		intra_os_delay.append((p[0], p[index_of_id(p, 133)][1]-p[0][1]))
#		packets.remove(p)
#	elif " 140" in l:
#		add_to_newest_packet(packets, l, required_number_of_traces=2)
#	else:
#		add_to_newest_packet(packets, l, required_number_of_traces=1)
		
print intra_os_delay
#intra_os_delay = sorted([x for x in intra_os_delay])
plt.title("Intra-os delay with varying packet size")
#for plot_index, ps_points in ns3_points.iteritems():
#for i, ps_points in enumerate(ns3_points):
#       	points = ps_points.get(int(ps))
#       	coords = [(a, b) for a, b in points.iteritems() if a > 35]
#       	coords = sorted(coords, key=lambda x: float(x[0]))
#       	plt.plot([a for a, b in coords], [b for a, b in coords], label="Device model")

plt.plot(xrange(len(ns3_points)), [i/1000.0 for i in ns3_points], label="Device model", marker='x', markersize=10, linewidth=0.7)
print "ns3_points:", ns3_points, len(ns3_points)

plt.xlabel('Sequence number')
plt.ylabel('Intra-OS delay (ms)')
#print "Seqnos:", [i[0] for i in intra_os_delay]
#plt.plot([i[0][0] for i in intra_os_delay], [i[1] for i in intra_os_delay], label="Real mote", marker='o')
plt.plot(xrange(len(intra_os_delay)), [i/1000.0 for i in intra_os_delay], label="Real mote", marker='o', linewidth=0.5)
plt.legend()

plt.show()


