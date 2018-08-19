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

int main(int argc, char *argv[])
{
    int fd;/*File Descriptor*/
    
    printf("\n +----------------------------------+");
    printf("\n |        Serial Port Read          |");
    printf("\n +----------------------------------+");

    /*------------------------------- Opening the Serial Port -------------------------------*/

    /* Change /dev/ttyUSB0 to the one corresponding to your system */

    fd = open(argv[1], O_RDWR | O_NOCTTY);	/* ttyUSB0 is the FT232 based USB2SERIAL Converter   */
                        /* O_RDWR   - Read/Write access to serial port       */
                        /* O_NOCTTY - No terminal will control the process   */
                        /* Open in blocking mode,read will wait              */
                            
                                                                    
                            
    if(fd == -1)						/* Error Checking */
            printf("\n  Error! in Opening serial port file  ");
    else
            printf("\n  Serial port file opened Successfully ");


    /*---------- Setting the Attributes of the serial port using termios structure --------- */
    
    struct termios SerialPortSettings;	/* Create the structure                          */
    memset(&SerialPortSettings, 0, sizeof(SerialPortSettings));

    tcgetattr(fd, &SerialPortSettings);	/* Get the current attributes of the Serial port */

    /* Setting the Baud rate */
    cfsetispeed(&SerialPortSettings,B115200); /* Set Read  Speed as 115200                       */
    cfsetospeed(&SerialPortSettings,B115200); /* Set Write Speed as 115200                       */

    /* 8N1 Mode */
//    SerialPortSettings.c_cflag &= ~PARENB;   /* Disables the Parity Enable bit(PARENB),So No Parity   */
//    SerialPortSettings.c_cflag &= ~CSTOPB;   /* CSTOPB = 2 Stop bits,here it is cleared so 1 Stop bit */
//    SerialPortSettings.c_cflag &= ~CSIZE;	 /* Clears the mask for setting the data size             */
//    SerialPortSettings.c_cflag |=  CS8;      /* Set the data bits = 8                                 */
    
//    SerialPortSettings.c_cflag &= ~CRTSCTS;       /* No Hardware flow Control                         */
//    SerialPortSettings.c_cflag |= CREAD | CLOCAL; /* Enable receiver,Ignore Modem Control lines       */ 
    
    
//    SerialPortSettings.c_iflag &= ~(IXON | IXOFF | IXANY);          /* Disable XON/XOFF flow control both i/p and o/p */
//    SerialPortSettings.c_iflag &= ~(ICANON | ECHO | ECHOE | ISIG);  /* Non Cannonical mode                            */
//    SerialPortSettings.c_iflag &= ~IGNBRK;
//    SerialPortSettings.c_lflag = 0;

    SerialPortSettings.c_cflag = CS8 | CLOCAL | CREAD;
    SerialPortSettings.c_iflag = IGNPAR | IGNBRK;


    SerialPortSettings.c_oflag &= ~OPOST;/*No Output Processing*/
    
    /* Setting Time outs */
    SerialPortSettings.c_cc[VMIN] = 5; /* Read at least 10 characters */
    SerialPortSettings.c_cc[VTIME] = 0; /* Wait indefinetly   */

    if((tcsetattr(fd,TCSANOW,&SerialPortSettings)) != 0) /* Set the attributes to the termios structure*/
        printf("\n  ERROR ! in Setting attributes\n");
    else
                printf("\n  BaudRate = 115200 \n  StopBits = 1 \n  Parity   = none\n\n");
        
        /*------------------------------- Read data from serial port -----------------------------*/
    tcflush(fd, TCIFLUSH);   /* Discards old data in the rx buffer            */

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
    while (keep_running) {
        // reposition fd to last byte in file
        //fseek(fd, -1L, SEEK_END);
        //fs = ftell(fd);
        //printf("\nBefore reading\n");
        /*int init_byte = read(fd, &eid, 1);
        printf("eid: %u, read: %d\n", eid, init_byte);
        if (!first && eid != 0 && eid != 46)
            continue;
        else if (eid == 0)
            first = 1;
        if (eid >= 70)
            continue;*/
        memset(bytes, 0, 5);
        int bytes_read = read(fd,bytes,5);
//	serial_read()
        if (bytes_read != 5) {
            break;
        }
            
        eid = bytes[0];
        if (bytes_read > 0) {
            events[i].eid = eid;
            uint8_t b1 = bytes[1], b2 = bytes[2], b3 = bytes[3], b4 = bytes[4];
            //if (b1 == 255)
            //    b1 = pb1;
            //if (b2 == 255)
            //    b2 = pb2;
            //if (b3 == 255)
            //    b3 = pb3;
            //if (b4 == 255)
            //    b4 = pb4;
            events[i].cycles = b1 | (b2 << 8) | (b3 << 16) | (b4 << 24);
            //asm volatile("rdtsc" : "=a" (a), "=d" (d));
            //events[i].cycles = (a | (d << 32));
            //asm /*volatile*/("rdtsc" : "=a" (a), "=d" (d));
            //printf("%llu-%u\n", events[i].cycles, events[i].eid);
            printf("b1: %u, b2: %u, b3: %u, b4: %u, events[%d].eid: %d, events[%d].cycles: %llu\n", b1, b2, b3, b4, i, events[i].eid, i, events[i].cycles);
            pb1 = b1;
            pb2 = b2;
            pb3 = b3;
            pb4 = b4;
            ++i;
            //prev_filesize = cur_filesize;
        }
    }

    close(fd);
    write_events_to_file();
}
