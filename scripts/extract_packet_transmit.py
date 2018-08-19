
f = open("static-traces.txt", "r")

lines = []
cur_line = ""
next_trace_size = False
for i, l in enumerate(f):
	trace_id = int(l.split()[1])
	if trace_id == 131:
		cur_line += l.split()[0]# + "\n" + str(i)
#		lines.append(cur_line)
#		cur_line = ""
		next_trace_size = True
	elif trace_id < 129:#''' and next_trace_size is True'''
		cur_line += "\n" + str(trace_id)
		lines.append(cur_line)
		cur_line = ""
		next_trace_size = False
#	if trace_id == 130 or trace_id < 129:
#		lines.append(l.split()[0])

f.close()
output = open("packets-received.txt", "w+")

for l in lines:
	output.write(l+"\n")

