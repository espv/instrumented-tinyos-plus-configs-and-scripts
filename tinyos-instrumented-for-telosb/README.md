# TinyOS instrumented to capture temporal behavior of CSW

How to create the device file for TelosB with Cooja and run an NS3 simulation:
1: Run Cooja with the modified UDPEcho program.
2: Start serial server on mote 2.
3: Run the read\_last\_byte\_socket.c program in scripts/, and use the port number from step 2.
4: Run the simulation in Cooja now. The program from step 3 will receive all the traces
   from the Cooja simulation. Whenever you want to stop the simulation, click ctrl-c in the
   program from step 3.
5: Run 'go run merge-traces.go' in scripts/ to produce a trace file that can be processed by
   analyse.go
6: Run 'go run analysis.go <TRACEFILE>' to produce signatures.
7: Copy the signatures you want in your device file to it as you feel fit.
8: Run './run\_gdb\_experiment.sh telosb' or './run\_valgrind\_experiment.sh telosb' to run the
   simulation with the execution environment.

PS: The above steps are very similar to how tracing a real device would be. The differences lie
    only in the four first steps, and they are as follows:
1: Connect a USB cable between TelosB and PC.
2: Run the read\_last\_byte.c program with the correct filename. The file the program listens to
   is the file that the TelosB mote writes its traces to.
3: Perform the real experiment, and stop whenever you feel like.
And that's it. From here on, you continue from step 5 above.

