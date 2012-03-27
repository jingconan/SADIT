/*
 * tree.c
 *
 *  Created on: Jun 13, 2010
 *      Author: johnraffensperger
 */
/* modified by JS */

#include <stdlib.h>
#include <strings.h>
#include <time.h>
#include <math.h>
#include "addrgen_trie.h"

#ifndef MAX
#define MAX(a,b) (a > b ? a : b)
#endif

#ifndef MIN
#define MIN(a,b) (a < b ? a : b)
#endif


static inline double unifrand()
{
    return drand48();
}

static double genbeta(double);

static inline struct node *new_node()
{
    struct node *n = (struct node*)malloc(sizeof(struct node));
    if (!n)
        return NULL;
    memset(n, 0, sizeof(struct node));
    return n;
}

static void reseed()
{
    srand48(time(NULL));
}

struct gentrie *initialize_trie(uint32_t netaddr, uint8_t prefixlen, double beta)
{
    static int randinit = 0;
    if (0 == randinit)
    {
        randinit = 1;
        reseed();
        genbeta(beta); // throw away the first value
    }


    if (prefixlen > 31)
        return NULL;
    if (beta < 0.0)
        return NULL;
    struct gentrie *trie = (struct gentrie*)malloc(sizeof(struct gentrie));
    if (!trie)
        return NULL;
    memset(trie, 0, sizeof(struct gentrie));
    trie->netaddr = netaddr;
    trie->prefixlen = prefixlen;
    trie->beta = beta;
    trie->root = new_node();
    trie->root->p = genbeta(beta);
    return trie;
}

static void release_helper(struct node *n)
{
   if (n == NULL)
       return;
   release_helper(n->children[0]);
   release_helper(n->children[1]);
   free(n);
   return;
}

void release_trie(struct gentrie *t)
{
    release_helper(t->root);
    free(t);
}

uint32_t generate_addressv4(struct gentrie *trie)
{
    /* assume that if there's a non-NULL trie passed that
       it has been properly initialized with initialize_trie */
    if (!trie)
        return 0;

    struct node *currnode = trie->root;
    int remaining_bits = 32 - trie->prefixlen;
    uint32_t xaddr = 0;
    while (remaining_bits > 0)
    {
        xaddr <<= 1;
        double pprime = unifrand();
        int leftright = pprime >= currnode->p; // 0 if left, 1 if right
        xaddr |= leftright;

        /* don't bother to create a node for the last bit */
        /* if we're not there yet, create a new node based on
           p vs. pprime */
        if (remaining_bits > 1 && !currnode->children[leftright])
        {
            struct node *xnode = new_node();
            xnode->p = genbeta(trie->beta);
            currnode->children[leftright] = xnode;
            currnode = xnode;
        }
        remaining_bits--;
    }
    return (trie->netaddr | xaddr);
}

static inline uint64_t count_helper(struct node *curr)
{
    if (curr == NULL)
        return 0ULL;
    return 1ULL + count_helper(curr->children[0]) + 
                  count_helper(curr->children[1]);
}

uint64_t count_nodes(struct gentrie *trie)
{
    struct node *rnode = trie->root;    
    return count_helper(rnode);  
}


static double genbeta(double aa)
/*
**********************************************************************
     float genbet(float aa,float bb)
               GENerate BETa random deviate
                              Function
     Returns a single random deviate from the beta distribution with
     parameters A and B.  The density of the beta is
               x^(a-1) * (1-x)^(b-1) / B(a,b) for 0 < x < 1
                              Arguments
     aa --> First parameter of the beta distribution

     bb --> Second parameter of the beta distribution

                              Method
     R. C. H. Cheng
     Generating Beta Variatew with Nonintegral Shape Parameters
     Communications of the ACM, 21:317-322  (1978)
     (Algorithms BB and BC)
**********************************************************************
*/
{
   double bb = aa;

#define expmax 89.0
#define infnty 1.0E38
static double olda = -1.0;
static double oldb = -1.0;
static double genbet,a,alpha,b,beta,delta,gamma,k1,k2,r,s,t,u1,u2,v,w,y,z;
static long qsame;

    qsame = olda == aa && oldb == bb;
    if(qsame) goto S20;
    if(!(aa <= 0.0 || bb <= 0.0)) goto S10;
S10:
    olda = aa;
    oldb = bb;
S20:
    if(!(MIN(aa,bb) > 1.0)) goto S100;
/*
     Alborithm BB
     Initialize
*/
    if(qsame) goto S30;
    a = MIN(aa,bb);
    b = MAX(aa,bb);
    alpha = a+b;
    beta = sqrt((alpha-2.0)/(2.0*a*b-alpha));
    gamma = a+1.0/beta;
S30:
S40:
    u1 = unifrand();
/*
     Step 1
*/
    u2 = unifrand();
    v = beta*log(u1/(1.0-u1));
    if(!(v > expmax)) goto S50;
    w = infnty;
    goto S60;
S50:
    w = a*exp(v);
S60:
    z = pow(u1,2.0)*u2;
    r = gamma*v-1.3862944;
    s = a+r-w;
/*
     Step 2
*/
    if(s+2.609438 >= 5.0*z) goto S70;
/*
     Step 3
*/
    t = log(z);
    if(s > t) goto S70;
/*
     Step 4
*/
    if(r+alpha*log(alpha/(b+w)) < t) goto S40;
S70:
/*
     Step 5
*/
    if(!(aa == a)) goto S80;
    genbet = w/(b+w);
    goto S90;
S80:
    genbet = b/(b+w);
S90:
    goto S230;
S100:
/*
     Algorithm BC
     Initialize
*/
    if(qsame) goto S110;
    a = MAX(aa,bb);
    b = MIN(aa,bb);
    alpha = a+b;
    beta = 1.0/b;
    delta = 1.0+a-b;
    k1 = delta*(1.38889E-2+4.16667E-2*b)/(a*beta-0.777778);
    k2 = 0.25+(0.5+0.25/delta)*b;
S110:
S120:
    u1 = unifrand();
/*
     Step 1
*/
    u2 = unifrand();
    if(u1 >= 0.5) goto S130;
/*
     Step 2
*/
    y = u1*u2;
    z = u1*y;
    if(0.25*u2+z-y >= k1) goto S120;
    goto S170;
S130:
/*
     Step 3
*/
    z = pow(u1,2.0)*u2;
    if(!(z <= 0.25)) goto S160;
    v = beta*log(u1/(1.0-u1));
    if(!(v > expmax)) goto S140;
    w = infnty;
    goto S150;
S140:
    w = a*exp(v);
S150:
    goto S200;
S160:
    if(z >= k2) goto S120;
S170:
/*
     Step 4
     Step 5
*/
    v = beta*log(u1/(1.0-u1));
    if(!(v > expmax)) goto S180;
    w = infnty;
    goto S190;
S180:
    w = a*exp(v);
S190:
    if(alpha*(log(alpha/(b+w))+v)-1.3862944 < log(z)) goto S120;
S200:
/*
     Step 6
*/
    if(!(a == aa)) goto S210;
    genbet = w/(b+w);
    goto S220;
S210:
    genbet = b/(b+w);
S230:
S220:
    return genbet;
#undef expmax
#undef infnty
}

#ifdef DEBUG
int main(int argc, char **argv)
{
    float b = 0.001;
    int nvals = 100;
    int i = 0;
    reseed();
    for ( ; i < nvals; i++)
        printf("%f\n", genbeta(b,b));

    return 0;
}
#endif
