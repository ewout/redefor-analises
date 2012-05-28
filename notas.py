#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pylab import *
from mdlib import *	
import pandas

#xls = pandas.ExcelFile('/home/ewout/Dropbox/ATP/Administrativo/Redefor-2011-SEE.xls')
#see = xls.parse('USP_2011_FINAL',index_col = None)
#see['numero-cpf-int'] = see['numero-cpf'].apply(int)

# (ambiente,grade_item)
ciencias = [(97,2529),(99,2611),(131,3337),(129,3226),(155,4495),(156,4562),(140,3844),(140,3846),(140,3845),(140,3910),(140,3911),(140,3916),(140,3912)]
biologia = [(102,2722),(121,2973),(137,3635),(138,3704),(151,4323),(157,4717),(142,3852),(142,3854),(142,3853),(142,3919),(142,3920),(142,3925)]
sociologia = [(104,3142),(104,3147),(134,3486),(134,3494),(149,5167),(149,5169),(141,3870),(141,3871),(141,3872),(141,3892),(141,3893),(141,3898)]
supervisores = [(94,3408),(94,3410),(136,3752),(136,3563),(159,4949),(159,4951),(143,3856),(143,3858),(143,3857),(143,3882),(143,3883),(143,3888)]
coordenadores = [(92,2362),(92,2378),(133,3446),(133,3453),(161,5206),(161,5208),(144,3860),(144,3862),(144,3861),(144,5175),(144,5176),(144,5236)]
diretores = [(93,2421),(93,2400),(135,3516),(135,3530),(153,4398),(153,4412),(145,3864),(145,3866),(145,3865),(145,3910),(145,3902),(145,3907)]

courses = {'Ciências':ciencias,
           'Biologia':biologia,
           'Sociologia':sociologia,
           'Supervisores':supervisores,
           'Coordenadores':coordenadores,
           'Diretores':diretores}


def itemname(gradeitem):
    ''
    result = loaddata('select courseid, itemname from mdl_grade_items where id = %s' % gradeitem,moodle='moodle_redefor')
    if result.size:
        course = courseinfo(result[0,0])['shortname']
        iname = l2u(result[0,1])
        return course + ': ' + str(iname)


def notas(userids,gradeitem):
    ''
    def nota (userid,gradeitem): 
        result = loaddata('select finalgrade from mdl_grade_grades where itemid = %s and userid = %s' % (gradeitem,userid),from_cache=False,moodle='moodle_redefor')
        if result:
            return result[0,0]

    return [nota(userid,gradeitem) for userid in userids]

def frame(course):
    ''
    first = True # hmm, não tem jeito melhor???
    for ambiente, gradeitem in course:
        #print gradeitem
        users = courseusers(ambiente)
        if users:
            userids = users['userid']
            gradename = itemname(gradeitem)
            grades = notas(userids,gradeitem)
            thisframe = pandas.DataFrame({'userid':userids})
            if first:
                frame = thisframe
                frame['firstname'] = users['firstname']
                frame['lastname'] = users['lastname']
                frame['idnumber'] = users['idnumber']
                frame[gradename] = grades
                first = False
                continue
            thisframe[gradename] = grades
            # usamos um pandas.DataFrame para poder alinhar (join) as notas pelo userid facilmente        
            frame = pandas.merge(frame,thisframe, on = 'userid', how='outer')
    
    return frame


def query_yes_no(question, default="sim"):
    valid = {"sim":"sim",   "s":"sim",
             "não":"não",     "n":"não"}
    if default == None:
        prompt = " [s/n] "
    elif default == "sim":
        prompt = " [S/n] "
    elif default == "não":
        prompt = " [s/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while 1:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return default
        elif choice in valid.keys():
            return valid[choice]
        else:
            sys.stdout.write("Responda com  'sim' ou 'não' "\
                             "(ou 's' or 'n').\n")

def export_grades(courses,d='notas/'):
    ''
    import os
    if not os.path.exists(d):
        makedir = query_yes_no("diretório "+d+" não existe. Criar?")
        if makedir == "sim":
            os.makedirs(d)
        else:
            return
    for coursename,course in courses.iteritems():
        df = frame(course)
        df.to_csv(os.path.join(d+'/',coursename+'.csv'),index=False)

if __name__ == '__main__':
    export_grades(courses)
