#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <inttypes.h>
#include <stdio.h>
#include <fcntl.h>   /* File Control Definitions           */
#include <termios.h> /* POSIX Terminal Control Definitions */
#include <unistd.h>  /* UNIX Standard Definitions 	   */ 
#include <errno.h>   /* ERROR Number Definitions           */
#include "../tinyos-main/tools/tinyos/c/sf/serialsource.h"


static volatile int keep_running = 1;

void int_handler(int dummy) {
    keep_running = 0;
}

typedef struct static_event {
    uint8_t eid;
    long long cycles;
} static_event;

int i = 0;
FILE * fd, * fd_out;
static_event events[100000000];


void write_events_to_file() {
    int j = 0;

    fd_out = fopen( "static-traces.txt" , "w" );

    while (j < i) {
//        printf("j: %d, i: %d\n", j, i);
        static_event *event = &events[j++];
        char line[100];
        memset(line, 0, 100);
        sprintf(line, "%llu %u\n", event->cycles, event->eid);
        fwrite(line , 1 , strlen(line) , fd_out );
//        printf("events[%d].eid: %d, events[%d].cycles: %llu\n", j, events[j].eid, j, events[j].cycles);
//        printf("Wrote line '%s'\n", line);
//        printf("cycles: %llu, eid: %d\n", event->cycles, event->eid);
    }

    fclose(fd_out);
}

static char *msgs[] = { 
  "unknown_packet_type",
  "ack_timeout" ,
  "sync"        ,
  "too_long"    ,   
  "too_short"   ,   
  "bad_sync"    ,   
  "bad_crc"     ,   
  "closed"      ,   
  "no_memory"   ,   
  "unix_error"
};

void stderr_msg(serial_source_msg problem)
{
  fprintf(stderr, "Note: %s\n", msgs[problem]);
}

int main(int argc, char *argv[])
{
    printf("\n +----------------------------------+");
    printf("\n |        Serial Port Read          |");
    printf("\n +----------------------------------+\n");

    /*------------------------------- Opening the Serial Port -------------------------------*/

    /* Change /dev/ttyUSB0 to the one corresponding to your system */

    int bytes_read = 0;
    uint8_t bytes[5];
    unsigned long long a, d;
    unsigned long long cycles = 0;
    int prev_filesize = 0;
    int cur_filesize = 0;
    int fs = 0;
    uint8_t eid;
    int first = 0;
    signal(SIGINT, int_handler);
    setbuf(stdout, NULL);
    uint8_t pb1, pb2, pb3, pb4;
    if (argc != 3)
      {   
        fprintf(stderr, "Usage: %s <device> <rate> - dump packets from a serial port\n", argv[0]);
        exit(2);
      }

    serial_source src = open_serial_source(argv[1], platform_baud_rate(argv[2]), 1, stderr_msg);
    if (!src)
      {   
        fprintf(stderr, "Couldn't open serial port at %s:%s\n",
                argv[1], argv[2]);
        exit(1);
      }
    while (keep_running) {
        memset(bytes, 0, 5);
	int remaining = 5;

	while (remaining > 0 && keep_running) {
            int read = serial_read(src, 1, &bytes[5-remaining], remaining); 
            if (read > 0)
                remaining -= read;
        }
        eid = bytes[0];
        events[i].eid = eid;
        uint8_t b1 = bytes[1], b2 = bytes[2], b3 = bytes[3], b4 = bytes[4];
        events[i].cycles = b1 | (b2 << 8) | (b3 << 16) | (b4 << 24);
        printf("b1: %u, b2: %u, b3: %u, b4: %u, events[%d].eid: %d, events[%d].cycles: %llu\n", b1, b2, b3, b4, i, events[i].eid, i, events[i].cycles);
        ++i;
    }

    close(fd);
    write_events_to_file();
}
