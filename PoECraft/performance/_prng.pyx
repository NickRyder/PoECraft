

# http://prng.di.unimi.it/xoshiro128starstar.c
cdef inline unsigned int rotl(unsigned int x, int k):
    return (x << k) | (x >> (32 - k))

cdef unsigned int s[4]
s[:] = [7,92929898,10100292,9999932]

cdef unsigned int rng():
    
    cdef unsigned int result = rotl(5*s[1],7)*9
    cdef unsigned int t = s[1] << 9

    s[2] ^= s[0]
    s[3] ^= s[1]
    s[1] ^= s[2]
    s[0] ^= s[3]

    s[2] ^= t

    s[3] = rotl(s[3], 11)
    return result


#http://www.pcg-random.org/posts/bounded-rands.html
cdef unsigned int _bounded_rand(unsigned int rand_range):
    cdef unsigned int x = rng()
    cdef unsigned long m = <unsigned long>x * <unsigned long>rand_range
    cdef unsigned int l = <unsigned long>m
    cdef unsigned int t = -rand_range
    if (l < rand_range):
        if (t >= rand_range):
            t -= rand_range
            if (t >= rand_range):
                t %= rand_range
        while (l < t):
            x = rng()
            m = <unsigned long>x * <unsigned long>rand_range
            l = <unsigned int>m
    return m >> 32

def bounded_rand(int rand_range):
    return _bounded_rand(rand_range)

