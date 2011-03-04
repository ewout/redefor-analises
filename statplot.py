#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pylab import *
from mdlib import loaddata, courseinfo,courseusers,lastaccess, week_where, dedica, courseids, dedica_curso, notas_curso
from matplotlib.ticker import MultipleLocator
from matplotlib import cm
from statlib import lorenz, gini
import time

def dedicacao(courseid):
    userids = courseusers(courseid)['userid']
    # choose 20 at random
    indices = random_integers(0,len(userids),20)
    userids = userids[indices] 
    for userid in userids:
        inativ = arange(0.1,10,0.1) # vary inativ from 0.1 to 10 hours
        t = []
        for tinativ in inativ:
            t.append(dedica(tinativ*60, userid, startweek = 1, endweek = 10))
        
        plot(inativ,t,'o-')

def tarefas():
    X = loaddata("SELECT from_unixtime(timemodified), timemodified, timemarked FROM mdl_assignment_submissions m where timemodified > %s and timemarked > 0 order by timemodified asc" % day0)
    submitted = X[:,0]
    delay = (X[:,2] - X[:,1])/(3600.0*24) #days
    #delay = np.sort(delay)
    #plot(range(len(delay)),delay,'o')
    plot(submitted,delay)

def acoes_cdf():
    'Distribuição do número de ações por usuário'
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
    'Número total de ações por dia'
    X = loaddata("select dayofyear(from_unixtime(time)) d, count(*) from mdl_log m group by d order by d asc")
    dayofyear = X[:,0]
    actions = X[:,1]
    fig = figure()
    ax = fig.add_subplot(111)
    ax.plot(dayofyear,actions,'o-')
    ax.set_xlim(250,350)
    ax.set_xlabel(u"dia do ano")
    ax.set_ylabel(u"# de ações / dia")


def acoes_distribucao(user=None,start=1, end=10):
    ''

    query = 'select userid, time FROM mdl_log m  '    

    query += 'where '
    query += week_where(start, end, 'time')
    if user:
        query += ' and userid = %s' % user
    query += ' order by time'
    print query
    X = loaddata(query)
    print X[0:10,1]
    d = diff(X[:,1])
    fig = figure()
    ax = fig.add_subplot(111)
    ax.hist(d,unique(d),histtype='step')
    ax.set_ylim(0,100)
    ax.set_xlabel(u"segundos entre ações")
    ax.set_ylabel(u"# de ações")


def acoes_visu(users,start=1, end=10):
    ''

    def query(user):
        q = 'select userid, time FROM mdl_log m  '    
        q += 'where '
        q += week_where(start, end, 'time')
        q += ' and userid = %s' % user
        q += ' order by time asc'
        return q

    fig = figure()
    
    for i,user in enumerate(users):
        X = loaddata(query(user))
        if X.any():
            clicks = X[:,1] - X[0,1]
        print i, user, len(clicks)
        ax = fig.add_subplot(len(users),1,i+1)
        axis("off")
        ax.plot(clicks, zeros(len(clicks)),'|')
    
def acoes_visu2(courseid,start=1, end=10):
    ''

    def query1(users):
        q = 'select userid, time FROM mdl_log m  '    
        q += 'where '
        q += week_where(start, end, 'time')
        q += " and userid in (" + ",".join([str(u) for u in users]) + ")"
        q += ' order by time asc'
        return q

    def query2(users):
        q = 'select userid, count(*) FROM mdl_log m  '    
        q += 'where '
        q += week_where(start, end, 'time')
        q += " and userid in (" + ",".join([str(u) for u in users]) + ")"
        q += ' group by userid order by count(*) desc'
        return q

    users = courseusers(courseid)['userid']
    course_shortname = courseinfo(courseid)['shortname']

    fig = figure()
    
    X = loaddata(query1(users))
    if X.any():
        clicks = X[:,1] - X[0,1]
        userids = X[:,0]
        # ordenar por userid com maior acoes
        Y = loaddata(query2(userids))
        userids_by_clicks = list(Y[:,0])
        # mapear userids para 0..nusers 
        y = [userids_by_clicks.index(u) for u in userids]
        cmap = cm.autumn
        ax = fig.add_subplot(111) 
        ax.plot(clicks/(3600.0), y ,'|')
        ax.set_xlabel(u'um | por ação ('+str(end-start+1)+' semanas)')
        ax.set_yticklabels([])
        figtext(0.8,0.8,course_shortname)
        #ax.hexbin(clicks, y, cmap=cmap, bins = 'log')
    


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
    fig = figure(figsize=(8,6))

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

def notas_vs_dedica():

	for n, cid in enumerate(courseids):
	
		x = n+1
		par = '42%s' % x
		subplot(par)
		plot(dedica_curso(cid),notas_curso(cid)[0],'ro')
		title(courseinfo(cid)['shortname'])
		plt.axis([0,150,0,10])
	subplot(428)
	for cid in courseids:
		plot(dedica_curso(cid),notas_curso(cid)[0],'ro')
		title('Todos')
		plt.axis([0,100,0,10])
	show()


def main():


#    from matplotlib.backends.backend_pdf import PdfPages
#    pp = PdfPages('redefor-figs.pdf')

#    cadastros()
#    savefig('cadastros.png')
#    acoes_cdf()
#    savefig('acoes_cdf.png')
#    acoes_tempo()
#    savefig('acoes_tempo.png')
#    lafigs()
#    savefig('last_access.png',dpi=300)
#    tarefas()
#    acoes_distribucao(start = 1, end = 10)
#    savefig('acoes_dist_tempos.png')
#    dedicacao(26)
#    savefig('dedica.png')
	notas_vs_dedica()

#    pp.savefig()
#    pp.close()
#	hist(notas_curso(24)[0],bins=20)

#    for cid in courseids:
        acoes_visu2(cid,start=1,end=5)
        savefig('acoes-visu-'+str(cid)+'.png')
#   show()

if __name__ == "__main__":
    main()
