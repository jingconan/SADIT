/*
 * main:
 *  - tree height (prefix length)
 *  - number of addresses
 *  - beta
 */
#include <stdio.h>
#include <stdint.h>
#include <sys/time.h>
#include "addrgen_trie.h"

int main(int argc, char **argv)
{
    struct gentrie *t = initialize_trie(0x7f000000, 8, 0.61);
    int i = 0;
    struct timeval begin, end, diff;
    gettimeofday(&begin, NULL);
    for ( ; i < 10000; i++)
    {
        uint32_t a = generate_addressv4(t);
        printf("0x%08x\n", a);
    }    
    gettimeofday(&end, NULL);
    timersub(&end, &begin, &diff);
    int c = (int)count_nodes(t);
    release_trie(t);
    printf("%d nodes %d bytes\n", c, (int)(c * sizeof(struct node)));
    printf("%d.%06d elapsed\n", (int)diff.tv_sec, (int)diff.tv_usec);
    return 0;
}
