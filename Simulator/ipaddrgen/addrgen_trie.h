/*
 * tree.h
 *
 *  Created on: Jun 13, 2010
 *      Author: johnraffensperger
 */

/* updated by JS */

#ifndef __TRIE_H__
#define __TRIE_H__

#include <netinet/in.h>
#include <stdint.h>

struct node 
{
    double p; // left is 0, right is 1
    struct node *children[2];
};

struct gentrie 
{
    uint32_t netaddr;
    struct node *root;
    double beta;
    int prefixlen;
};

struct gentrie *initialize_trie(uint32_t, uint8_t, double);
uint32_t generate_addressv4(struct gentrie *);
uint64_t count_nodes(struct gentrie *);
void release_trie(struct gentrie *);

#endif /* __TRIE_H__ */
