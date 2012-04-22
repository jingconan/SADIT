=============================================
Log file for SADIT
=============================================

[2012-04-21 22:49:38]
=============================================
generator

what's the difference with generator of Multi-Server case and normal case?


multi-server case, generators have different types.

for each source and sever pair. we have a random variable to indicating the type
of the flow. 
for user i and server j, the random variable is so called. :math:`X_i^j`

we store the joint distribution as a matrix. 
for each user i, we have a set of random variable X^j. 
X^j, j = 1,...,n. there are m severs. 

joint_dist = zeros([ n digit tuple ])
join_dist[p1, p2, p3] is the probability distribution of 
type to sever 1 is p1, type of flow to server 2 is p2, type of flow to server 3
is p3.

the summation over all other flows is the marginal probability of a specific
random variable.

We get different types of generators

