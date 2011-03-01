# -*- coding: utf-8 -*-

from pylab import *
import MySQLdb as mysql
import hashlib
import config
import time, os

cachedir = 'cache'
courseids = [14,15,24,25,26,21,34]
day0 = time.mktime((2010,10,4,0,0,0,0,0,0))

prefix = "mdl_"

def loaddata(query,from_cache=True):
    if from_cache:
        queryhash = hashlib.md5(query).hexdigest()
        try:
            fpath = os.path.join(cachedir,queryhash + ".npy")
            return np.load(fpath)
        except IOError as msg:
            print msg
            
    db = mysql.connect(host=config.host,user=config.user,passwd=config.passwd,db=config.db)
    c = db.cursor()
    c.execute(query)
    results = c.fetchall()
    if from_cache:
        fpath = os.path.join(cachedir,queryhash + ".npy")
        np.save(fpath,array(results))
    return array(results)



def courseinfo(courseid):
    X = loaddata('select * from mdl_course where id = %s' % courseid)
    cinfo = {'fullname': X[0,4],
             'shortname': X[0,5]}
    return cinfo

def course2context(courseid):
    query = "select id from mdl_context where contextlevel = 50 and instanceid = %s" % courseid
    X = loaddata(query)
    return X[0,0]

def courseusers(courseid):
    ''
    query = '''SELECT u.firstname, u.lastname, u.id, la.timeaccess, c.shortname, c.fullname 
    FROM mdl_course c
    INNER JOIN mdl_context cx ON c.id = cx.instanceid
    AND cx.contextlevel = '50' and c.id=%s
    INNER JOIN mdl_role_assignments ra ON cx.id = ra.contextid
    INNER JOIN mdl_role r ON ra.roleid = r.id
    INNER JOIN mdl_user u ON ra.userid = u.id
    INNER JOIN mdl_user_lastaccess la ON la.userid = u.id and la.courseid = %s order by la.timeaccess desc''' % (courseid,courseid)

    X = loaddata(query)
    cinfo = {'firstname': X[:,0],
             'lastname': X[:,1],
             'userid': [int(x) for x in X[:,2]],
             'lastaccess': [float(x) for x in (X[:,3])],
             'cshortname': X[:,4],
             'cfullname': X[:,5]}
    return cinfo
    
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
	tempototal = 0L

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
	query = 'select finalgrade, userid from mdl_grade_grades where itemid = %s order by userid asc' % itemid
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

#	ids = courseusers(courseid)["userid"]
	grades, ids	= notas_curso(courseid)
	if ids:
		t = []
		tempos = []
		for u in ids:
			tempos.append(dedica(30, u, 1, 10, courseid))
	return tempos
