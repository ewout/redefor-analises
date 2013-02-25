#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pylab import *
from mdlib import *
import pandas

#xls = pandas.ExcelFile('/home/ewout/Dropbox/ATP/Administrativo/Redefor-2011-SEE.xls')
#see = xls.parse('USP_2011_FINAL',index_col = None)
#see['numero-cpf-int'] = see['numero-cpf'].apply(int)

# (ambiente,grade_item)
ciencias1 = [(14,1582),(15,1587),(51,1607),(61,1606),(61,1562),(64,2231),(69,2229),(78,2315),(80,2318),(80,2342),(80,3154),(86,2224)]
biologia1 = [(24,1158),(25,1164),(60,1624),(54,1627),(54,1567),(63,2273),(68,2234),(83,2330),(84,2328),(84,2334),(84,3155),(76,1771)]
supervisores1 = [(26,1898),(26,1901),(58,1921),(58,1922),(58,1569),(67,2845),(67,2846),(82,2833),(82,2834),(82,2713),(82,3167),(75,1769)]
coordenadores1 = [(21,691),(21,692),(52,1002),(52,1003),(52,1573),(66,1400),(66,1401),(77,1776),(77,1783),(77,2962),(77,3168),(85,2221)]
diretores1 = [(34,697),(34,698),(53,1004),(53,1005),(53,1610),(65,1402),(65,1403),(79,1830),(79,1835),(79,2691),(79,3169),(73,1764)]
ciencias2 = [(97,2532),(97,2529),(99,2611),(131,3337),(129,3226),(155,4497),(155,4495),(156,4562),(167,5273),(168,5340),(140,3843),(108,2879)]
biologia2 = [(102,2725),(102,2722),(121,2973),(137,3635),(138,3704),(151,4326),(151,4323),(157,4717),(178,6052),(177,5981),(142,3851),(204,7044)]
sociologia2 = [(104,3144),(104,3142),(104,3147),(134,3486),(134,3494),(149,4295),(149,5167),(149,5169),(175,5807),(175,5817),(141,3847),(166,5182)]
supervisores2 = [(94,2453),(94,3408),(94,3410),(136,3752),(136,3563),(159,4867),(159,4949),(159,4951),(176,5952),(176,5954),(143,3855),(163,5158)]
coordenadores2 = [(92,3433),(92,2374),(92,6995),(92,6996),(133,4111),(133,6997),(133,6998),(161,6156),(161,5212),(161,7000),(161,7000),(170,7004),(170,7062),(170,7061),(144,5177),(164,5160)]
diretores2 = [(93,6164),(93,2421),(93,2400),(135,3516),(135,3530),(153,4424),(153,4398),(153,4412),(174,5753),(174,5766),(145,3863),(165,5163)]

courses = {'Ciencias-ano1':ciencias1,
           'Biologia-ano1':biologia1,
           'Supervisores-ano1':supervisores1,
           'Coordenadores-ano1':coordenadores1,
           'Diretores-ano1':diretores1,
           'Ciencias-ano2':ciencias2,
           'Biologia-ano2':biologia2,
           'Sociologia-ano2':sociologia2,
           'Supervisores-ano2':supervisores2,
           'Coordenadores-ano2':coordenadores2,
           'Diretores-ano2':diretores2}


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
            return float(result[0,0])

    grades = [nota(userid,gradeitem) for userid in userids]
    grades = [round(nota,1) if nota else None for nota in grades]
    scale = scalenota(gradeitem)
    if scale:
        # Usar float(scale) assume que os strings da escala são 1 e 0
        # Isto só é válido para as presenças na escola!
        return [float(scale(int(nota))) if nota else None for nota in grades]
    else:
        return grades

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
                frame['Email'] = users['email']
                frame['Tel1'] = users['phone1']
                frame['Tel2'] = users['phone2']
                frame[gradename] = grades
                first = False
                continue
            thisframe[gradename] = grades
            # usamos um pandas.DataFrame para poder alinhar (join) as notas pelo userid facilmente
            frame = pandas.merge(frame,thisframe, on = 'userid', how='outer')

#    # agora as colunas "atividade" dos ambientes
#    ambientes = [ambiente for (ambiente, gradeitem) in course]
#    #unique and sorted
#    ambientes = sorted(list(set(ambientes)))
#    for ambiente in ambientes:
#        users = courseusers(ambiente)
#        coursename = courseinfo(ambiente)['shortname']
#        if users:
#            userids = users['userid']
#            thisframe = pandas.DataFrame({'userid':userids})
#            thisframe['Atividade '+coursename] = [ativuser(userid,ambiente) for userid in userids]
#            frame = pandas.merge(frame,thisframe, on = 'userid', how='outer')


    # remover id do moodle antes de publicar
    del frame['userid']
    return frame

def moodle_date():
    return loaddata('select from_unixtime(timemodified) from mdl_grade_grades_history order by timemodified desc limit 1',from_cache=False,moodle='moodle_redefor')[0,0]

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
        outfile = os.path.join(d+'/',coursename+dstr)
        print "Writing to ", outfile
        df.to_csv(outfile + '.csv',index=False, sep='\t')
        try:
            # usar xlsx ao vez de xls aqui porque tem um problema com o xlwt e utf8...
            df.to_excel(outfile + '.xlsx', index = False)
        except ImportError:
            print "Faça um 'sudo pip install openpyxl' e tente novamente"
    if sync:
        rstr = "rsync -av "+d+" atp.usp.br:/var/www/dados/redefor/"
        print rstr
        subprocess.call(rstr,shell=True)

if __name__ == '__main__':
    import os
    d = os.path.expanduser('~/Dropbox/redefor-analises/dados/notas')
    if not os.path.exists(d):
        d = os.path.expanduser('~/redefor-analises/dados/notas')
    export_grades(courses,d, sync=False)
    print "Agora, faça um rsync -av "+d+" atp.usp.br:/var/www/dados/redefor/"
    print "(Use rsync -av --delete se quiser remover arquivos inexistentes no diretório local do servidor remoto atp.usp.br)"
