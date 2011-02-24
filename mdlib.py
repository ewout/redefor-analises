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
        np.save(queryhash,array(results))
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
             'userid': X[:,2],
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
