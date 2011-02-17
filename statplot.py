# -*- coding: utf-8 -*-

from pylab import *
from mdlib import loaddata, courseinfo,courseusers,lastaccess
from matplotlib.ticker import MultipleLocator
import time

courseids = [14,15,24,25,26,21,34]
day0 = time.mktime((2010,10,4,0,0,0,0,0,0))


def week_where(week = 1, timeexpr = 'timemodified'):

    start = day0 + (week-1)*3600*24*7
    end = start + (week)*3600*24*7
    return 'where %s between %s and %s' % (timeexpr,start,end)

def tarefas():
    X = loaddata("SELECT from_unixtime(timemodified), timemodified, timemarked FROM mdl_assignment_submissions m where timemodified > %s and timemarked > 0 order by timemodified asc" % day0)
    submitted = X[:,0]
    delay = (X[:,2] - X[:,1])/(3600.0*24) #days
    #delay = np.sort(delay)
    #plot(range(len(delay)),delay,'o')
    plot(submitted,delay)

def acoes_cdf():
    X = loaddata("SELECT userid, count(*) FROM mdl_log m group by userid order by count(*) desc;")
    actions = X[:,1]
    ccdf = arange(len(actions))/(1.0*len(actions))
    cdf = 1-ccdf
    fig = figure()
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212, sharex=ax1)
    ax1.loglog(actions,cdf,'o')
    ax1.set_ylabel(u'P(x < X)')
    ax2.loglog(actions,ccdf,'o')
    ax2.set_ylabel(u'P(x > X)')
    figtext(0.4, 0.02, u'X = número ações')



def acoes_tempo():
    X = loaddata("select dayofyear(from_unixtime(time)) d, count(*) from mdl_log m group by d order by d asc")
    dayofyear = X[:,0]
    actions = X[:,1]
    fig = figure()
    ax = fig.add_subplot(111)
    ax.plot(dayofyear,actions,'o-')
    ax.set_xlim(250,350)
    ax.set_xlabel(u"dia do ano")
    ax.set_ylabel(u"# de ações / dia")



def cadastros():
    # cadastros desde 02/10/2010
     X = loaddata("select from_unixtime(firstaccess) from mdl_user where firstaccess > 1285988400 and firstaccess < 1287712800 order by firstaccess asc;")
     cdate = X[:,0]
     cadastros = arange(len(cdate))
     fig = figure()
     ax = fig.add_subplot(111)
     ax.plot(cdate,cadastros,'-')
     fig.autofmt_xdate()
     figtext(0.3,0.92,'Cadastros no AVA do Redefor - outubro 2010')

def lafigs(tlimit=30):
    'usuários com lastaccess < t vs t'

    i = 0
    fig = figure()

    for courseid in courseids:
        i += 1
        la,cum_users,since = lastaccess(courseid)
        title = courseinfo(courseid)['shortname']
        ax = fig.add_subplot(4,2,i)
        ax.set_title(title)
        #ax.annotate("Total",
        #            xytext=(0.8*tlimit,0.95*len(la)), xycoords='data',
        #            xy = (tlimit,len(la)),textcoords='data',
        #            arrowprops = dict(arrowstyle="->",connectionstyle='arc3'))
        ax.plot(la,cum_users/(1.0*len(la)))
        ax.set_xlim(0,tlimit)
        #ax.set_ylim(0,len(la)*1.1)
        ax.set_ylim(0,1)

    la,cum_users,since = lastaccess()
    ax = fig.add_subplot(4,2,i+1)
    ax.set_title('Todas')
    ax.annotate("Total",
                xytext=(0.8*tlimit,0.95*len(la)), xycoords='data',
                xy = (tlimit,len(la)),textcoords='data',
                arrowprops = dict(arrowstyle="->",connectionstyle='arc3'))
    ax.plot(la,cum_users)
    ax.set_xlim(0,tlimit)
    ax.set_ylim(0,len(la)*1.1)

    t0 = time.strftime("%d/%m/%Y",time.gmtime(since))
    figtext(0.2,0.95,u'Participantes (fração do total) nos últimos N dias (antes de %s )' % t0)
    fig.subplots_adjust(hspace=0.4)

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


def main():

#    cadastros()
#    acoes_cdf()
#    acoes_tempo()
    lafigs()
#    tarefas()
    show()

if __name__ == "__main__":
    main()
