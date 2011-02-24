# -*- coding: utf-8 -*-

from pylab import *

def lorenz(x):
    'returns a Lorenz curve for an array of random values x'
#    x = sorted(x,reverse=True)
    x = sorted(x,reverse=False)
    P = range(1,len(x)+1)
    P = array(P)/(1.0*len(x)+1)
    s = 0
    L = []
    for a in x:
        s += a
        L.append(s)
    L = array(L)/(1.0*sum(x))

    return (P,L)

def gini(x):
    'Returns Gini coeficient for array of rv x'
    x = sorted(x)
    n = len(x)
    i = arange(1,n+1)
    s1 = sum(i*x)
    s2 = sum(x)
    return 1.0 -(2.0/(n-1))*(n-s1/s2)

def gini2(x):
    mu = mean(x);
    s = 0
    N = len(x)
    for i in range(N):
        for j in range(N):
            s += abs(1.0*x[i]-1.0*x[j])
    return 0.5*s/mu/N**2

