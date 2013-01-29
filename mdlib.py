# -*- coding: utf-8 -*-

from pylab import *
import MySQLdb as mysql
import hashlib
import config
import time, os, decimal
from datetime import date

cachedir = 'cache'

moodles = {'stoa':'moodle',
           'redefor':'moodle_redefor',
           'liciencias':'moodle_lic_salas',
           'evs':'moodle_evs',
           'evc':'moodle_evc'}


# id dos curso dos modulos 1, 2, 3 e 4
courseids1 = [14,15,24,25,26,21,34,104]
courseids2 = []
courseids3 = []
courseids4 = []

# id da nota AVA dos curso dos modulos 1, 2, 3 e 4
idnotava1 = [84,215,1159,1602,[1905,1906],[1621,1622],[1603,1604],[3142,3147]]
idnotava2 = []
idnotava3 = []
idnotava4 = []

# id da nota da prova presencial dos curso dos modulos 1, 2, 3 e 4
idpp1 = [1560,1561,1564,1565,743,1571,1572,3144]
idpp2 = [1560,1561,1564,1565,743,1571,1572,3144]

# id da frequencia AVA dos curso dos modulos 1, 2, 3 e 4
idfreqava1 = [899,906,909,912,869,[917,922],[916,923],[916,916]]
idfreqava2 = []

day0 = time.mktime((2010,10,4,0,0,0,0,0,0))

prefix = "mdl_"

def loaddata(query,from_cache=False, moodle='moodle_lic2'):

    if from_cache:
        queryhash = hashlib.md5(query+moodle).hexdigest()
        try:
            fpath = os.path.join(cachedir,queryhash + ".npy")
            return np.load(fpath)
        except IOError as msg:
            print msg
    db = mysql.connect(host=config.host,user=config.user,passwd=config.passwd,db=moodle)
    c = db.cursor()
    c.execute(query)
    results = c.fetchall()
    if from_cache:
        fpath = os.path.join(cachedir,queryhash + ".npy")
        np.save(fpath,array(results))
    return array(results)


def pessoa(nusp):
    ''
    X = loaddata('select * from pessoa where codpes = %s' % nusp, moodle='usp')
    pinfo = {'nompes': X[0,2],
             'sexpes': X[0,4],
             'dtanas' : X[0,5]
             }
    return pinfo

def cpf2codpes(cpf):
    ''
    cpf = int(cpf)
    salt = config.cpfsalt
    cpfhash = hashlib.md5(salt+str(cpf)).hexdigest()
    X = loaddata('select codpes from pessoa where numcpf = "%s"' % cpfhash, moodle='usp')
    if X:
        return X[0,0]

def courseinfo(courseid):
    X = loaddata('select * from mdl_course where id = %s' % courseid)
    cinfo = {'fullname': l2u(X[0,4]),
             'shortname': l2u(X[0,5])}
    return cinfo

def course2context(courseid):
    query = "select id from mdl_context where contextlevel = 50 and instanceid = %s" % courseid
    X = loaddata(query)
    return X[0,0]

def courseusers(courseid):
    ''
    query = '''SELECT u.firstname, u.lastname, u.id, c.shortname, c.fullname, u.idnumber
    FROM mdl_course c
    INNER JOIN  mdl_context cx ON c.id = cx.instanceid
    AND cx.contextlevel = '50' and c.id=%s
    INNER JOIN mdl_role_assignments ra ON cx.id = ra.contextid
    INNER JOIN mdl_role r ON ra.roleid = r.id and r.id = 5
    INNER JOIN mdl_user u ON ra.userid = u.id
    ''' % (courseid,)

    X = loaddata(query, from_cache=False)
    if X.size:
        cinfo = {'firstname': [l2u(x) for x in X[:,0]],
             'lastname': [l2u(x) for x in X[:,1]],
             'userid': [int(x) for x in X[:,2]],
             'cshortname': X[:,3],
             'cfullname': X[:,4],
             'idnumber': [int(x) if x else '' for x in X[:,5]]}
        return cinfo
    else:
        return False
    
def lastaccess(courseid=None):
    'usuários com lastaccess < t vs t'


    if courseid:
        res = courseusers(courseid)
        la = np.array(res['lastaccess'])
        since = la[0]
        la = (since - la)/(3600.0*24)
    else:
        query = 'select timeaccess, userid from mdl_user_lastaccess where timeaccess >  0 group by userid order by timeaccess desc'
        X = loaddata(query)
        la = X[:,0]
        since = la[0]
        la = (since - la)/(3600.0*24) # dias desde o mais recente

    return la, arange(1,len(la)+1), since


def week_where(startweek = 1, endweek = 10,timeexpr = 'timemodified'):
    
    start = day0 + (startweek-1)*3600*24*7
    end = start + (endweek)*3600*24*7
    return '%s between %s and %s' % (timeexpr,start,end)


def dedica(inativ = 30, userid = 2, startweek = 1, endweek = 10, courseid = 14):

    inativsec = inativ*60

    query = 'select time from mdl_log where '
    query += week_where(startweek, endweek, 'time')
    query += 'and course = %s ' % courseid 
    query += 'and userid = %s order by time asc' % userid
    X = list(loaddata(query))

    t = []
    for z in X:
        t.append(z[0])

    s = []
    if len(t) > 0:
        s.append(t[0])
    tempototal = 0.0

    for i, y in enumerate(t[0:-1]):
        if  (t[i+1]-y) > inativsec:
            temposecao = s[-1] - s[0]
            tempototal += temposecao
            s = [t[i+1]]
        else:
            s.append(y)
    return tempototal/3600 #retorna o tempo total em horas


def notas_curso(courseid):
    
    queryid = 'SELECT id FROM mdl_grade_items where itemtype = "course" and courseid = %s' % courseid
    id = loaddata(queryid)
    itemid = id[0,0]
    
#    query = 'select finalgrade, userid from mdl_grade_grades where itemid = %s order by userid asc' % itemid
    ''
    query = '''SELECT g.finalgrade, usr.id
    FROM mdl_course c
    INNER JOIN mdl_context cx ON c.id = cx.instanceid
    INNER JOIN mdl_role_assignments ra ON cx.id = ra.contextid
    INNER JOIN mdl_role r ON ra.roleid = r.id
    INNER JOIN mdl_user usr ON ra.userid = usr.id
    INNER JOIN mdl_grade_grades g ON usr.id = g.userid
    INNER JOIN mdl_grade_items gi ON g.itemid = gi.id
    WHERE r.id = 5 AND gi.id = %s AND c.id = %s AND cx.contextlevel = '50'
    ORDER BY usr.id asc''' % (itemid, courseid)
    X = loaddata(query)
    notas = X[:,0]
    userids = [int(x) for x in X[:,1]]
    grade = []
    for n in notas:
        if not n:
            grade.append(0)
        else:
            grade.append(float(n))
    return grade, userids


def notas_grupo(courseid):

    #encontrando o id do item da nota final do curso
    queryid = 'SELECT id FROM mdl_grade_items where itemtype = "course" and courseid = %s' % courseid
    id = loaddata(queryid)
    itemid = id[0,0] 

    q1 = 'SELECT id FROM mdl_groups WHERE courseid = %s order by id asc'% courseid
    groupids = loaddata(q1) #array com os ids de todos os grupos do

    medias = []            
    if groupids.any(): #verifica se ha grupos no curso
        for g in groupids[:,0]: # repete para cada grupo
            q2 = 'SELECT userid FROM mdl_groups_members where groupid=%s' % g
            userids = loaddata(q2) #tomando os ids de usuarios do grupo
            notas =[]
            if userids.any(): #verifica se ha membros no grupo
                for u in userids[:,0]: #repete para cada usuario
                    q3 = 'SELECT finalgrade FROM mdl_grade_grades WHERE userid=%s and itemid=%s' % (u, itemid)
                    nota = loaddata(q3) #busca a nota final do usuario
                    if nota.any(): #verifica se ha notas para o usuario
                        if nota[0,0] is False: #verifica se a nota eh falsa
                            notas.append(0) #atribui zero caso seja falsa
                        else:
                            notas.append(float(nota[0,0])) #senao adiciona a nota aa lista de notas do grupo
                    else:
                        notas.append(0) # se o usuario nao tem nenhuma nota atribuida adiciona zero na lista de notas do grupo
                medias.append(mean(notas)) 
            else:
                medias.append(0)
                
    return medias #retorna uma lista com as medias de notas finais dos grupos ordenado pelo id do grupo
        
        
def dedica_grupo(courseid):

    q1 = 'SELECT id FROM mdl_groups WHERE courseid = %s order by id asc'% courseid
    groupids = loaddata(q1) #array com os ids de todos os grupos do
    
    if groupids.any():
        t = []
        for g in groupids[:,0]:
        
            q2 = 'SELECT userid FROM mdl_groups_members where groupid=%s' % g
            userids = loaddata(q2) #tomando os ids de usuarios do grupo
            tempos = []
            if userids.any():
                for u in userids[:,0]:
                    tempos.append(dedica(30, u, 1, 10, courseid))
                tmedio = mean(tempos)
            t.append(tmedio)
    return t
    
    
def dedica_curso(courseid):

#    ids = courseusers(courseid)["userid"]
    ids    = notas_curso(courseid)[1]
    if ids:
        t = []
        tempos = []
        for u in ids:
            tempos.append(dedica(30, u, 1, 10, courseid))
    return tempos
    
def usersbyrole(courseid, roleid=5):
    ''
    query = '''SELECT u.firstname, u.lastname, u.id, c.shortname, c.fullname 
    FROM mdl_course c
    INNER JOIN mdl_context cx ON c.id = cx.instanceid
    AND cx.contextlevel = '50' and c.id=%s
    INNER JOIN mdl_role_assignments ra ON cx.id = ra.contextid
    INNER JOIN mdl_role r ON ra.roleid = r.id and r.id = %s
    INNER JOIN mdl_user u ON ra.userid = u.id
    ''' % (courseid,roleid)

    X = loaddata(query)
    cinfo = {'firstname': X[:,0],
             'lastname': X[:,1],
             'userid': [int(x) for x in X[:,2]],
             'lastaccess': [float(x) for x in (X[:,3])],
             'cshortname': X[:,4],
             'cfullname': X[:,5]}
    return cinfo
    
def usersbygroup(groupid, roleid=5):

    query = '''select gm.userid from mdl_groups_members gm where groupid = %s and gm.userid in (select ra.userid from mdl_role_assignments ra where roleid = %s)''' % (groupid, roleid)
        
    X = loaddata(query)
    if X.any():
        notas = X[:,0]
        userids = [int(x) for x in X[:,0]]
    else:
        userids = []
            
    return userids
    
    
def ativuser(userid, courseid):
    
    query = '''select count(*) from mdl_log where userid = %s and course = %s''' % (userid, courseid)
    a = loaddata(query)[0,0]
    
    return a

    
def infoaluno(courseid, saida=recarray):
     
    nusp = []    
    grupo = []
    ativ = []
    desist = []
    tutor = []
    notava1 = []
    notava2 = []
    notapp = []
    freqava1 = []
    freqava2 = []
    i = courseids1.index(courseid)
    c = courseid
    
    q1 = '''select id from mdl_groups where courseid = %s;''' % c
    grupos = list(loaddata(q1)[:,0])
    if grupos <> []:
        for g in grupos:
            users = usersbygroup(g)
            users += usersbygroup(g,4)
            if users <> []:
                for u in users:
                    #Numero USP
                    n = loaddata('''select idnumber from mdl_user where id = %s''' % u)
                    if n:
                        nusp.append(n[0,0])
                    else:
                        nusp.append(0)
                    
                    #Grupo
                    grupo.append(loaddata('''select name from mdl_groups where id = %s''' % g)[0,0])
                    
                    #Atividade (num. de itens no mdl_log)
                    ativ.append(ativuser(u, c))
                    
                    #Desistente
                    la = loaddata('''select from_unixtime(lastaccess) from mdl_user where id = %s''' % u)[0,0]
                    delta = date.today() - la.date()
                    if  delta.days > 30:
                        desist.append(1)
                    else:
                        desist.append(0)
                    t = loaddata('''select id from mdl_role_assignments where userid = %s and roleid = 4''' % u)
                    if t.any():
                        tutor.append(1)
                    else:
                        tutor.append(0)
                    
                    #Nota AVA
                    
                    if type(idnotava1[i]) == list:
                        n1 = loaddata('''select finalgrade from mdl_grade_grades where itemid = %s and userid = %s''' % (idnotava1[i][0],u))
                        if n1.any():    
                            notava1.append(n1[0,0])
                        else:
                            notava1.append('')

                        n2 = loaddata('''select finalgrade from mdl_grade_grades where itemid = %s and userid = %s''' % (idnotava1[i][1],u))
                        if n2.any():
                            notava2.append(n2[0,0])
                        else:
                            notava2.append('')

                    else:
                        n1 = loaddata('''select finalgrade from mdl_grade_grades where itemid = %s and userid = %s''' % (idnotava1[i],u))
                        if n1.any():
                            notava1.append(n1[0,0])
                        else:
                            notava1.append('')
                        notava2.append('')
                    
                    #Nota da prova presencial
                    q = loaddata('''select finalgrade from mdl_grade_grades where itemid = %s and userid = %s''' % (idpp1[i],u))
                    if q.any():
                        notapp.append(q[0,0])
                    else:
                        notapp.append('')
                        
                    #Frequencia
                    try:
                        if type(idfreqava1[i]) == list:
                        
                            f1 = loaddata('''select finalgrade from mdl_grade_grades where itemid = %s and userid = %s''' % (idfreqava1[i][0],u))
                            if f1.any():    
                                freqava1.append(f1[0,0])
                            else:
                                freqava1.append('')
                                
                                f2 = loaddata('''select finalgrade from mdl_grade_grades where itemid = %s and userid = %s''' % (idfreqava1[i][1],u))
                                if f2.any():
                                    freqava2.append(f2[0,0])
                                else:
                                    freqava2.append('')
                                    
                        else:
                            f1 = loaddata('''select finalgrade from mdl_grade_grades where itemid = %s and userid = %s''' % (idfreqava1[i],u))
                            if f1.any():
                                freqava1.append(f1[0,0])
                            else:
                                freqava1.append('')
                            freqava2.append('')
                    except:
                        pass
                    
    nusp = array(nusp)
    grupo = array(grupo)
    ativ = array(ativ)
    desist = array(desist)
    tutor = array(tutor)
    notava1 = array(notava1)
    notava2 = array(notava2)
    notapp = array(notapp)
    freqava1 = array(freqava1)
    freqava2 = array(freqava2)
    
    reg = rec.fromarrays([nusp,grupo,ativ,desist,tutor,notava1,notava2,notapp,freqava1,freqava2], names = 'NumUSP, Grupo, Atividade, Desistente, Tutor, NotaAVA1, NotaAVA2, Prova Presencial,Frequencia AVA 1,Frequencia AVA 2')
    outfile = 'csv/InfoAluno-'+courseinfo(c)['shortname']+'.csv'
    if saida == recarray:
        return reg
    else:        
        rec2csv(reg, outfile)
        
def infogrupo(courseid,saida=recarray):
    
   
    nomegrupo = []
    ativtutor = []
    ativalunos = []
    fracdesist = []
    c = courseid
    i = courseids1.index(courseid)

    q1 = '''select id from mdl_groups where courseid = %s;''' % c
    grupos = list(loaddata(q1)[:,0])
    if grupos:
        for g in grupos:

            #Nome do grupo
            nome = loaddata('''select name from mdl_groups where id = %s''' % g)[0,0]
            nomegrupo.append(nome)

            #Atividade do tutor
            at = []
            tutores = usersbygroup(g,4)
            if tutores:
                for t in tutores:
                    at.append(ativuser(t, c))
                ativtutor.append(sum(at))
            else:
                ativtutor.append('')
            
            #Atividade dos alunos
            alunos = usersbygroup(g)
            if alunos:
                aa = []
                for a in alunos:
                    aa.append(ativuser(a, c))
                ativalunos.append(mean(aa))
            else:
                ativalunos.append('')
            
            #Fracao desistente
            if alunos:
                desist = []
                for a in alunos:
                    la = loaddata('''select from_unixtime(lastaccess) from mdl_user where id = %s''' % a)[0,0]
                    delta = date.today() - la.date()
                    if  delta.days > 30:
                        desist.append(1)
                    else:
                        desist.append(0)
                fracdesist.append(mean(desist))
            else:
                fracdesist.append('')
                    
    nomegrupo = array(nomegrupo)
    ativtutor = array(ativtutor)
    ativalunos = array(ativalunos)
    fracdesist = array(fracdesist)
    
    reg = rec.fromarrays([nomegrupo, ativtutor, ativalunos, fracdesist], names = 'Grupo, Atividade do tutor, Atividade media dos alunos, Fracao desistente')
    outfile = 'csv/InfoGrupo-'+courseinfo(c)['shortname']+'.csv'
    if saida == recarray:
        return reg
    else:
        rec2csv(reg, outfile)
        
        
def username(userid):

    query = 'select firstname, lastname from mdl_user where id = %s' % userid
    X = loaddata(query)
    return X[0,0]+' '+X[0,1]
        
        
def l2u(s):
    'converte string latin1 em utf8'
    return s.decode('latin1').encode('utf8')
     
def ativtutores(courseid):

    ids = usersbyrole(courseid, 4)['userid']
    outfile = 'csv/AtivTutor-'+courseinfo(courseid)['shortname']+'.csv'
    print outfile
    fp = open(outfile,'w')
    fp.write('nome\tatividade_total\tativ_forum\tativ_dialogo\tadd_entry\n')
    for i in ids:
        fp.write(str(l2u(username(i)))+'\t'+str(logcount(i, courseid))+'\t'+str(logcount(i, courseid,'forum'))+'\t'+str(logcount(i,courseid,'dialogue'))+'\t'+str(logcount(i,courseid,'dialogue','add entry'))+'\n')
    fp.close()
    
def logcount(userid=None, courseid=None, mod=None, act=None,from_cache=True,moodle='moodle_lic2'):
    if userid is None:
        if courseid is None:
            if mod is None:
                if act is None:
                    w = ''
                else:
                    w = '''where action="%s"''' %act
            else:
                if act is None:
                    w = '''where module = "%s"''' %mod
                else:
                    w = '''where module = "%s" and action="%s"''' %(mod, act)
        else:
            if mod is None:
                if act is None:
                    w = '''where course = %s''' %courseid
                else:
                    w = '''where course = %s and action="%s"''' %(courseid, act)
            else:
                if act is None:
                    w = '''where course = %s and module = "%s"''' %(courseid, mod)
                else:
                    w = '''where course = %s and module = "%s" and action="%s"''' %(courseid, mod, act)
    else:        
        if courseid is None:
            if mod is None:
                if act is None:
                    w = '''where userid = %s''' %userid
                else:
                    w = '''where userid = %s and action="%s"''' %(userid, act)
            else:
                if act is None:
                    w = '''where userid = %s and module = "%s"'''%(userid, mod)
                else:
                    w = '''where userid = %s and module = "%s" and action="%s"''' %(userid, mod, act)
        else:
            if mod is None:
                if act is None:
                    w = '''where userid = %s and course = %s''' %(userid, courseid)
                else:
                    w = '''where userid = %s and course = %s and action="%s"''' %(userid, courseid, act)
            else:
                if act is None:
                    w = '''where userid = %s and course = %s and module = "%s"''' %(userid, courseid, mod)
                else:
                    w = '''where userid = %s and course = %s and module = "%s" and action="%s"''' %(userid, courseid, mod, act)
    query = "select count(*) from mdl_log "+w
    return loaddata(query,from_cache=from_cache,moodle=moodle)[0,0]


def active_courses(n_actions, start = None, stop=None, moodle='moodle_lic2'):
    '''Returns array of course ids with at least n_actions between start and stop.
    Start and stop are tuples of the form (year, month), for example (2010,1) for Jan. 2010'''

    if not start:
        starts = 0
    else:
        starts = time.mktime((start[0],start[1],0,0,0,0,0,0,0))
    if not stop:
        stops = time.localtime()
    else:
        stops = time.mktime((stop[0],stop[1],0,0,0,0,0,0,0))

    query = 'SELECT course, count(*) n FROM mdl_log m where time between %s and %s and course <> 0 and course <> 1  group by course having count(*) > %s order by count(*) desc' % (starts,stops,n_actions)
    X = loaddata(query,from_cache=False,moodle=moodle)
    if X.any():
        return X[:,0]
    else:
        return array([])
    

def course_frame(start, stop):
    '''Generates dataframe of course indicators from mdl_log 

    Start and stop are tuples of the form (year, month), for example (2010,1) for Jan. 2010'''
    
    # courses with at least 10 actions in the time period
    ids = active_courses(10, start, stop)

    df = []

    for id in ids:
        forum_adds = logcount(courseid=id, mod='forum', act='add')
        forum_views = logcount(courseid=id, mod='forum', act='view forum')
        forum_posts = logcount(courseid=id, mod='forum', act='add post')

        assignment_views = logcount(courseid=id, mod='assignment', act='view')
        assignment_uploads = logcount(courseid=id, mod='assignment', act='upload')
        assignment_adds = logcount(courseid=id, mod='assignment', act='add')

        course_views = logcount(courseid=id, mod='course', act='view')

        quiz_adds = logcount(courseid=id, mod='quiz', act='add')
        quiz_views = logcount(courseid=id, mod='quiz', act='view')
        quiz_attempts = logcount(courseid=id, mod='quiz', act='attempt')


        resource_views = logcount(courseid=id, mod='resource', act='view')
        resource_updates = logcount(courseid=id, mod='resource', act='update')
        resource_adds = logcount(courseid=id, mod='resource', act='add')
        
        df.append((id,forum_adds,forum_views,forum_posts,assignment_views,assignment_uploads,assignment_adds,course_views,quiz_views,quiz_adds,quiz_attempts,resource_views,resource_updates,resource_adds))
        
    df = rec.fromrecords(df,names=('courseid','forum_adds','forum_views','forum_posts','assignment_views','assignment_uploads','assignment_adds','course_views','quiz_views','quiz_adds','quiz_attempts','resource_views','resource_updates','resource_adds'))

    return df

def quiz_attempts(quizid,time='start'):
    'Returns list of datetime times in ascending order. time ={start,finish,modified}'
    
    query = 'select from_unixtime(time%s) from mdl_quiz_attempts where quiz = %i order by time%s asc' % (time,quizid,time)
    X = loaddata(query)
    return X[:,0]

def logs_per_day(moodle='moodle'):
    'return (date,actions)'
    query = 'SELECT from_unixtime(time) date, year(from_unixtime(time)) year, dayofyear(from_unixtime(time)) day, count(*) actions FROM mdl_log m group by year, day'
    X = loaddata(query,True,moodle)
    return X[:,0],X[:,3]

def quiz_attempts_hour_before_deadline():
    '-- Number of quiz submissions by hour before deadline'
    query = """
SELECT 
    (quiz.timeclose - qa.timefinish) / 3600 AS hoursbefore,
    COUNT(1)

FROM mdl_quiz_attempts as qa
JOIN mdl_quiz as quiz ON quiz.id = qa.quiz

WHERE
    qa.preview = 0 AND
    quiz.timeclose <> 0 AND
    qa.timefinish <> 0

AND
    (quiz.timeclose - qa.timefinish) / 3600 < 24 * 7

GROUP BY
    (quiz.timeclose - qa.timefinish) / 3600

ORDER BY
    hoursbefore"""
    X = loaddata(query)
    return X

def quiz_attempts_hourofday():
    'Number of quiz submissions by hour of day'
    query = """SELECT 
    hour(from_unixtime(timefinish)) hour,
    COUNT(1)

FROM mdl_quiz_attempts qa

WHERE
    qa.preview = 0 AND
    qa.timefinish <> 0

GROUP BY
    hour

ORDER BY
    hour
"""
    X = loaddata(query)
    return X
