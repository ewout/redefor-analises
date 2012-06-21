#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pylab import *
from mdlib import *	
import pandas

#xls = pandas.ExcelFile('/home/ewout/Dropbox/ATP/Administrativo/Redefor-2011-SEE.xls')
#see = xls.parse('USP_2011_FINAL',index_col = None)
#see['numero-cpf-int'] = see['numero-cpf'].apply(int)

# (ambiente,grade_item)
ciencias = [(97,2532),(97,2529),(97,2534),(99,2611),(99,3747),(131,3337),(131,3762),(129,3226),(129,3785),(155,4495),(156,4562),(140,3844),(140,3846),(140,3845),(140,3910),(140,3911),(140,3916),(140,3912)]
biologia = [(102,2725),(102,2722),(102,6117),(121,2973),(121,6118),(137,3635),(137,6119),(138,3704),(138,6120),(151,4323),(157,4717),(142,3852),(142,3854),(142,3853),(142,3919),(142,3920),(142,3925)]
sociologia = [(104,3144),(104,3142),(104,3147),(104,5268),(104,5269),(134,3486),(134,3494),(134,5270),(134,5271),(149,5167),(149,5169),(141,3870),(141,3871),(141,3872),(141,3892),(141,3893),(141,3898)]
supervisores = [(94,2453),(94,3408),(94,6121),(94,3410),(94,6123),(136,3752),(136,6124),(136,3563),(136,6122),(159,4949),(159,4951),(143,3856),(143,3858),(143,3857),(143,3882),(143,3883),(143,3888)]
coordenadores = [(92,2374),(92,2362),(92,6125),(92,2378),(92,6126),(133,3446),(133,6127),(133,3453),(133,6128),(161,5206),(161,5208),(144,3860),(144,3862),(144,3861),(144,5175),(144,5176),(144,5236)]
diretores = [(93,2420),(93,2421),(93,6129),(93,2400),(93,6130),(135,3516),(135,6131),(135,3530),(135,6132),(153,4398),(153,4412),(145,3864),(145,3866),(145,3865),(145,3910),(145,3902),(145,3907)]

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

    def scalenota(gradeitem):
        result = loaddata('select scaleid from mdl_grade_items where id = %s' % gradeitem, moodle='moodle_redefor')
        if result:
            scaleid = result[0,0]
            result = loaddata('select scale from mdl_scale where id = %s' % scaleid,moodle='moodle_redefor')
            if result:
                scale = result[0,0].split(',')
                return lambda x: scale[x-1]

        
    def nota (userid,gradeitem): 
        result = loaddata('select finalgrade from mdl_grade_grades where itemid = %s and userid = %s' % (gradeitem,userid),from_cache=False,moodle='moodle_redefor')
        if result:
            return result[0,0]

    notas = [nota(userid,gradeitem) for userid in userids]
    scale = scalenota(gradeitem)
    if scale:
        return [scale(int(nota)) if nota else None for nota in notas]
    else:
        return notas

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
                frame['Nome AVA'] = users['firstname']
                frame['Sobrenome AVA'] = users['lastname']
            
                frame['Número USP'] = users['idnumber']
                frame['Nome Apolo'] = [pessoa(codpes)['nompes'] if codpes else '' for codpes in users['idnumber']]
                frame[gradename] = grades
                first = False
                continue
            thisframe[gradename] = grades
            # usamos um pandas.DataFrame para poder alinhar (join) as notas pelo userid facilmente        
            frame = pandas.merge(frame,thisframe, on = 'userid', how='outer')

    # agora as colunas "atividade" dos ambientes
    ambientes = [ambiente for (ambiente, gradeitem) in course]
    #unique and sorted
    ambientes = sorted(list(set(ambientes)))
    for ambiente in ambientes:
        users = courseusers(ambiente)
        coursename = courseinfo(ambiente)['shortname']
        if users:
            userids = users['userid']
            thisframe = pandas.DataFrame({'userid':userids})
            thisframe['Atividade '+coursename] = [ativuser(userid,ambiente) for userid in userids]
            frame = pandas.merge(frame,thisframe, on = 'userid', how='outer')
            

    # remover id do moodle antes de publicar
    del frame['userid'] 
    return frame

def moodle_date():
    return loaddata('select from_unixtime(time) from mdl_log order by time desc limit 1',from_cache=False,moodle='moodle_redefor')[0,0]

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

def export_grades(courses,d='notas/', sync=False):
    ''
    import os, subprocess
    if not os.path.exists(d):
        makedir = query_yes_no("diretório "+d+" não existe. Criar?")
        if makedir == "sim":
            os.makedirs(d)
        else:
            return
    moodledate = moodle_date()
    dstr =  '-' + moodledate.strftime('%Y-%m-%d')
    for coursename,course in courses.iteritems():
        df = frame(course)
        df.to_csv(os.path.join(d+'/',coursename+dstr+'.csv'),index=False)
    if sync:
        rstr = "rsync -av "+d+" atp.usp.br:/var/www/dados/redefor/"
        print rstr
        subprocess.call(rstr,shell=True)

if __name__ == '__main__':
    export_grades(courses,'/home/ewout/redefor-analises/dados/notas', sync=True)
