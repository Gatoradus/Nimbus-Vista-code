All from: http://www.linuxforums.org/forum/programming-scripting/195773-get-wireless-statistics-c.html


int main(int argc, char *argv[]){

    int sockfd;
    struct iw_statistics stats;
    struct iwreq req;

    if(argc != 2){
        fprintf(stderr, "Usage: %s iface\n", argv[0]);
        return -1;
    }

    memset(&stats, 0, sizeof(stats));
    memset(&req, 0, sizeof(req));
    sprintf(req.ifr_name, "wlan0"); // for debug, hardcode the iface
    req.u.data.pointer = &stats;
    req.u.data.length = sizeof(stats);
#ifdef CLEAR_UPDATED
    req.u.data.flags = 1;
#endif


    if((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) == -1) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    if(ioctl(sockfd, SIOCGIWSTATS, &req) == -1) {
        perror("ioctl SIOCGIWSTATS failed");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    close(sockfd);

// I have to substract 256 to get the values as they are shown in /proc/net/wireless, why iw_statistics parameters are unsigned? what I am doing wrong?

    printf("qual: %d level: %d noise: %d updated: %d\n",
        stats.qual.qual, stats.qual.level - 256, stats.qual.noise - 256, stats.qual.updated);

return 0;
}

using /proc/net/wireless

int main(void){

    int i;
    char buf[32];
    FILE *fproc;

    fproc = fopen("/proc/net/wireless", "r");

    if(fproc == NULL){
        perror("failed to open /proc/net/wireless");
        return -1; 
    }   
        
    for(i=0; i<31; i++){  // Level is in position 31
        fscanf(fproc, "%s", buf);
//      printf("i: %d : %s\n",i, buf);
    }   

    printf("Level: %d\n", atoi(buf));
    fclose(fproc);

    return 0;

}

Better way with casts


int main(int argc, char *argv[])
{

    int sockfd;
    struct iw_statistics stats;
    struct iwreq req;

    if(argc != 2)
    {
        fprintf(stderr, "Usage: %s iface\n", argv[0]);
        return -1;
    }

    memset(&stats, 0, sizeof(stats));
    memset(&req, 0, sizeof(req));
    sprintf(req.ifr_name, "wlan0"); // for debug, hardcode the iface
    req.u.data.pointer = &stats;
    req.u.data.length = sizeof(stats);
#ifdef CLEAR_UPDATED
    req.u.data.flags = 1;
#endif


    if((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) == -1)
    {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    if(ioctl(sockfd, SIOCGIWSTATS, &req) == -1)
    {
        perror("ioctl SIOCGIWSTATS failed");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    close(sockfd);

// I have to substract 256 to get the values as they are shown in /proc/net/wireless, why iw_statistics parameters are unsigned? what I am doing wrong?

    printf("qual: %d level: %d noise: %d updated: %d\n",
        (int)((char)stats.qual.qual), (int)((char)stats.qual.level), (int)((char)stats.qual.noise), (int)((char)stats.qual.updated));

return 0;
}


