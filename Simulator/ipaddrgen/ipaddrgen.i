/* Convert from Python --> C */
%typemap(in) uint32_t {
    $1 = PyInt_AsLong($input);
}

/* Convert from C --> Python */
%typemap(out) uint32_t {
    $result = PyInt_FromLong($1);
}

/* Convert from Python --> C */
%typemap(in) uint8_t {
    $1 = PyInt_AsLong($input);
}

/* Convert from C --> Python */
%typemap(out) uint8_t {
    $result = PyInt_FromLong($1);
}

/* Convert from Python --> C */
%typemap(in) uint64_t {
    $1 = PyInt_AsLong($input);
}

/* Convert from C --> Python */
%typemap(out) uint64_t {
    $result = PyInt_FromLong($1);
}


%module ipaddrgen
%{
struct gentrie *initialize_trie(uint32_t, uint8_t, double);
uint32_t generate_addressv4(struct gentrie *);
uint64_t count_nodes(struct gentrie *);
void release_trie(struct gentrie *);
%}

struct gentrie *initialize_trie(uint32_t, uint8_t, double);
uint32_t generate_addressv4(struct gentrie *);
uint64_t count_nodes(struct gentrie *);
void release_trie(struct gentrie *);
