#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pylab import *
from mdlib import *	
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
    
def acoes_visu2(courseid,start=1, end=10, plottype='ticks'):
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
    clicks = X[:,1] - X[0,1]
    userids = X[:,0]
    # ordenar por userid com maior acoes
    Y = loaddata(query2(userids))
    userids_by_clicks = list(Y[:,0])
    # mapear userids para 0..nusers 
    y = [userids_by_clicks.index(u) for u in userids]
    ax = fig.add_subplot(111) 
    figtext(0.9,0.9,course_shortname)
    if plottype == 'ticks':
        ax.plot(clicks/(3600.0), y ,'|')
        ax.set_xlabel(u'um | por ação ('+str(end-start+1)+' semanas)')
        ax.set_yticklabels([])
    elif plottype == 'heatmap':
        xbins = (end-start+1)*7*24 # 1 hora / bin
        ybins = len(users)/5 # 5 usuários / bin
        heatmap, xedges, yedges = histogram2d(y,clicks,bins=(ybins,xbins))
        print heatmap
        print 'xbins', xbins, 'ybins ', ybins
        print 'max', heatmap.max()
        cmap = cm.hot
        #img = imshow(heatmap,cmap=cmap,origin='lower',aspect = xbins/ybins)
        img = imshow(heatmap,cmap=cmap,origin='lower')
        #clim = (0,heatmap.mean()*2)
        clim = (0,30)
        img.set_clim(clim)
        img.axes.set_yticklabels([])
        img.axes.set_xlabel(u'horas')
        cb = colorbar()
        cb.set_label('clicks por hora')
        

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

	fig = figure()
	fig.suptitle('Notas vs Atividade')

	for n, cid in enumerate(courseids):
	
		x = n+1
		par = '42%s' % x
		subplot(par)
		notas = notas_curso(cid)[0]
		tempos = dedica_curso(cid)
		plot(tempos,notas,'ro')
		title(courseinfo(cid)['shortname'])
		plt.axis([0,150,0,10])
		xlabel('Atividade')
		ylabel('Nota')
		subplot(428)
		plot(tempos,notas,'ro')
	title('Todos')
	xlabel('Atividade')
	ylabel('Nota')
	plt.axis([0,150,0,10])
	show()
	
def notas_vs_dedica_grupos():

	fig = figure()
	fig.suptitle('Notas vs Atividade (por grupo)')
	
	for n, cid in enumerate(courseids):
		x = n+1
		par = '42%s' % x
		subplot(par)
		notas = notas_grupo(cid)
		tempos = dedica_grupo(cid)
		plot(tempos,notas,'ro')
		title(courseinfo(cid)['shortname'])
		axis([0,100,0,10])
		xlabel('Atividade')
		ylabel('Nota')
		subplot(428)
		plot(tempos,notas,'ro')
	title('Todos')
	ylabel('Nota')
	subplot(428)
	axis([0,100,0,10])
	show()

def hist_notas():
	
	fig = figure()
	fig.suptitle('Histograma de notas por curso')
	todas = []
	for n, cid in enumerate(courseids):
		x = n+1
		par = '42%s' % x
		subplot(par)
		notas = notas_curso(cid)[0]
		hist(notas,20)
		title(courseinfo(cid)['shortname'])
		[todas.append(n) for n in notas]
	subplot(428)
	hist(todas,20)	
	title('Geral')
	show()
	
def hist_dedica():

	fig = figure()
	fig.suptitle('Histograma de atividade por curso')
	geral = []
	for n, cid in enumerate(courseids):
		x = n+1
		par = '42%s' % x
		subplot(par)
		tempo = dedica_curso(cid)
		hist(tempo,20,(0,160))
		title(courseinfo(cid)['shortname'])
		[geral.append(n) for n in tempo]
	subplot(428)
	hist(geral,20,(0,160))	
	title('Geral')
	show()

def notas_fuvest(fn, gtitle="Notas", notascol = 'pontos11', curcol='curusp'):
    from scipy.stats import gaussian_kde
    prova = csv2rec(fn)
    cursos = {
        480100007 : u'Ciências',
        410100001 : u'Biologia',
        480100015 : u'Diretores',
        810100001 : u'Supervisores',
        480100011 : u'Coordenadores'
        }

    fig = plt.figure()
    fig.text(0.5,0.975,gtitle,horizontalalignment='center',verticalalignment='top')
    p = arange(0,40,0.1)
    axt = fig.add_subplot(3,2,6)

    for i,curso in enumerate(cursos):
        curso
        notas = [x[notascol] for x in prova if x[curcol] == curso]
        kde = gaussian_kde(array(notas)*1.0)
        line = axt.plot(p,kde(p),'-')
        color = line[-1].get_color()
        ax = fig.add_subplot(3,2,i+1)
        ax.hist(notas,normed=True,rwidth=0.9,color=color)
        ax.set_xlim(0,40)
        ax.set_ylim(0,0.12)
        ax.text(0.05,0.82,cursos[curso]+u' N = '+unicode(len(notas)),transform=ax.transAxes)


def quiz_attempts_plot(quizids):
    for quizid in quizids:
        t = quiz_attempts(quizid,time='start')
        if quizid == 470:
            t = t[0:-1]
        plot(t,range(len(t)))
    fig = gcf()
    fig.autofmt_xdate()
    return fig
    
        
    

def main():

#    quiz_attempts_plot([470,478,501])

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
#    notas_vs_dedica()
#    notas_vs_dedica_grupos()
#    hist_notas()
#    pp.savefig()
#    pp.close()

#    acoes_visu2(14,start=1,end=2,plottype='heatmap')

#    for cid in courseids:
#        acoes_visu2(cid,start=1,end=5,plottype='heatmap')
#        savefig('acoes-visu-1-5'+str(cid)+'.png')
#        acoes_visu2(cid,start=5,end=10,plottype='heatmap')
#        savefig('acoes-visu-5-10'+str(cid)+'.png')
#    notas_fuvest('redefor2011a-1-fuvest8abr2011.csv',u'Redefor 2011-04-08, prova Módulo 1 e 2')
    notas_fuvest('redefor2011-prova2.csv',u'Redefor 2011-09-03, prova Módulo 3 e 4','pontos1','codcur')

    show()

if __name__ == "__main__":
    main()
