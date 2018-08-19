
f = open("static-traces.txt", "r")

last_time = 0
i = 0
start_packet_size = 88
microseconds_start = 24000
microseconds_stop = 5000
microsecond_interval = 250
microseconds_between_intervals = 6000000000
microseconds_between_ps = 42000000000
#microseconds_between_intervals = 2000000
#microseconds_between_ps = 50000000

packets_per_interval = 256
packet_size = 88
packet_size_interval = 8
min_packet_size = 0
packet_per_microseconds = 24250
cur_index = 0
number_files = 0
write_to = None
do_skip_leftover = False
skip_leftover_traces = 0
for i, l in enumerate(f):
	cur_time = int(l.split()[0])
	#if cur_time > (last_time + microseconds_between_ps):
	#	print i, "ps decrease because time diff of", cur_time-last_time
	if cur_time > (last_time + microseconds_between_intervals): 
		number_files += 1
		if do_skip_leftover:
			skip_leftover_traces += 1
			if skip_leftover_traces == 2:
				skip_leftover_traces = 0
#		print "New file, number_files:", number_files, "cur_time:", cur_time, "diff:", cur_time - (last_time + microseconds_between_intervals)
#		print "i:", i, "cur time:", cur_time, "last_time:", last_time
		# New pps. If i == 255, new packet size as well
		packet_per_microseconds -= microsecond_interval
		if packet_per_microseconds < microseconds_stop:
			packet_per_microseconds = microseconds_start
			packet_size -= packet_size_interval
			if packet_size < min_packet_size:
				# End
				pass
	
		pps = int(1/(packet_per_microseconds/1000000.0))
		if write_to is not None:
			write_to.close()
		if skip_leftover_traces != 1:
			write_to = open("all_contexts/pps"+str(pps)+"psize"+str(packet_size)+"_exploratory.txt", "w")
		print "write to new file: all_contexts/pps"+str(pps)+"psize"+str(packet_size)+"_exploratory.txt"
	if skip_leftover_traces != 1:
		write_to.write(l)
	last_time = cur_time

