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
        //event->cycles /= 1050;
        sprintf(line, "%llu %u\n", event->cycles, event->eid);
        fwrite(line , 1 , strlen(line) , fd_out );
        //printf("events[%d].eid: %d, events[%d].cycles: %llu\n", j, events[j].eid, j, events[j].cycles);
        //printf("Wrote line '%s'\n", line);
        //printf("cycles: %llu, eid: %d\n", event->cycles, event->eid);
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

    tcgetattr(fd, &SerialPortSettings);	/* Get the current attributes of the Serial port */

    /* Setting the Baud rate */
    cfsetispeed(&SerialPortSettings,B115200); /* Set Read  Speed as 115200                       */
    cfsetospeed(&SerialPortSettings,B115200); /* Set Write Speed as 115200                       */

    /* 8N1 Mode */
    SerialPortSettings.c_cflag &= ~PARENB;   /* Disables the Parity Enable bit(PARENB),So No Parity   */
    SerialPortSettings.c_cflag &= ~CSTOPB;   /* CSTOPB = 2 Stop bits,here it is cleared so 1 Stop bit */
    SerialPortSettings.c_cflag &= ~CSIZE;	 /* Clears the mask for setting the data size             */
    SerialPortSettings.c_cflag |=  CS8;      /* Set the data bits = 8                                 */
    
    SerialPortSettings.c_cflag &= ~CRTSCTS;       /* No Hardware flow Control                         */
    SerialPortSettings.c_cflag |= CREAD | CLOCAL; /* Enable receiver,Ignore Modem Control lines       */ 
    
    
    SerialPortSettings.c_iflag &= ~(IXON | IXOFF | IXANY);          /* Disable XON/XOFF flow control both i/p and o/p */
    SerialPortSettings.c_iflag &= ~(ICANON | ECHO | ECHOE | ISIG);  /* Non Cannonical mode                            */

    SerialPortSettings.c_oflag &= ~OPOST;/*No Output Processing*/
    
    /* Setting Time outs */
    SerialPortSettings.c_cc[VMIN] = 1; /* Read at least 10 characters */
    SerialPortSettings.c_cc[VTIME] = 0; /* Wait indefinetly   */

    if((tcsetattr(fd,TCSANOW,&SerialPortSettings)) != 0) /* Set the attributes to the termios structure*/
        printf("\n  ERROR ! in Setting attributes");
    else
                printf("\n  BaudRate = 115200 \n  StopBits = 1 \n  Parity   = none");
        
        /*------------------------------- Read data from serial port -----------------------------*/
    tcflush(fd, TCIFLUSH);   /* Discards old data in the rx buffer            */

    char byte;
    unsigned long long a, d;
    unsigned long long cycles = 0;
    int prev_filesize = 0;
    int cur_filesize = 0;
    int fs = 0;
    signal(SIGINT, int_handler);

    while (keep_running) {
        // reposition fd to last byte in file
        //fseek(fd, -1L, SEEK_END);
        //fs = ftell(fd);
        //printf("\nBefore reading\n");
        int byte_read = read(fd,&byte,1);
        //if (byte_read < 0)
        //    printf("errno: %d\n", errno);
        //printf("byte_read: %d\n", byte_read);
        if (byte_read > 0) {
            events[i].eid = byte;
            asm volatile("rdtsc" : "=a" (a), "=d" (d));
            events[i].cycles = (a | (d << 32));
            //asm /*volatile*/("rdtsc" : "=a" (a), "=d" (d));
            //printf("%llu-%u\n", events[i].cycles, events[i].eid);
	    ++i;
	    printf("%d, %llu, eid: %d\n", i, (a | (d << 32)), byte);
            //printf("Time to read: %llu, events[%d].eid: %d, events[%d].cycles: %llu\n", (a | (d << 32)) - events[i].cycles, i, events[i].eid, i, events[i].cycles);
            //prev_filesize = cur_filesize;
        }
    }

    close(fd);
    write_events_to_file();
}
