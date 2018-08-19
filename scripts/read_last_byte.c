#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <inttypes.h>

static volatile int keep_running = 1;

void int_handler(int dummy) {
    keep_running = 0;
}

typedef struct static_event {
    uint8_t eid;
    uint64_t cycles;
} static_event;

int main()
{
    FILE * fd, * fd_out;
    char byte;
    unsigned long long a, d;
    unsigned long long cycles = 0;
    int prev_filesize = 0;
    int cur_filesize = 0;
    int fs = 0;
    int i = 0;

    static_event events[100000];

    signal(SIGINT, int_handler);
    printf("Opening file\n");
    fd = fopen("usb-raw-traces.txt", "r");
    if (fd == NULL) {
        printf("Error opening file\n");
        return -1;
    }

    while (keep_running) {
        // reposition fd to last byte in file
        fseek(fd, -1L, SEEK_END);
        fs = ftell(fd);
        if (fs != -1)
            cur_filesize = fs;
        if (cur_filesize != prev_filesize) {
            asm /*volatile*/("rdtsc" : "=a" (a), "=d" (d));
            events[i].eid = fgetc(fd);
            events[i].cycles = (a | (d << 32));
            asm /*volatile*/("rdtsc" : "=a" (a), "=d" (d));
            printf("Time to read: %llu, events[%d].eid: %d, events[%d].cycles: %lu\n", (a | (d << 32)) - events[i].cycles, i, events[i].eid, i, events[i].cycles);
            ++i;
            prev_filesize = cur_filesize;
        }
    }

    fclose(fd);
}