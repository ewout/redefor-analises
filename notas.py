#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pylab import *
from mdlib import *	
import pandas

#xls = pandas.ExcelFile('/home/ewout/Dropbox/ATP/Administrativo/Redefor-2011-SEE.xls')
#see = xls.parse('USP_2011_FINAL',index_col = None)
#see['numero-cpf-int'] = see['numero-cpf'].apply(int)

# (ambiente,grade_item)
ciencias1 = [(14,1582),(15,1587),(51,1607),(61,1606),(61,1562),(64,2231),(69,2229),(78,2315),(80,2318),(80,2342),(86,2224)]
biologia1 = [(24,1158),(25,1164),(60,1624),(54,1627),(54,1567),(63,2273),(68,2234),(83,2330),(84,2328),(84,2334),(76,1771)]
supervisores1 = [(26,1898),(26,1901),(58,1921),(58,1922),(58,1569),(67,2845),(67,2846),(82,2833),(82,2834),(82,2713),(82,3167),(75,1769)]
coordenadores1 = [(21,691),(21,692),(52,1002),(52,1003),(52,1573),(66,1400),(66,1401),(77,1776),(77,1783),(77,2962),(77,3168),(85,2221)]
diretores1 = [(34,697),(34,698),(53,1004),(53,1005),(53,1610),(65,1402),(65,1403),(79,1830),(79,1835),(79,2691),(79,3169),(73,1764)]
ciencias2 = [(97,2532),(97,2529),(97,2534),(99,2611),(99,3747),(131,3337),(131,3762),(129,3226),(129,3785),(155,4497),(155,4495),(155,4765),(156,4562),(156,4683),(167,5273),(167,5859),(168,5340),(168,5342),(140,3844),(140,3846),(140,3845),(140,3910),(140,3911),(140,3916),(140,3912),(140,3913),(140,3914),(140,3915),(140,3917),(140,3918),(140,7025),(140,7026),(140,3843),(108,2879)]
biologia2 = [(102,2725),(102,2722),(102,6117),(121,2973),(121,6118),(137,3635),(137,6119),(138,3704),(138,6120),(151,4326),(151,4323),(151,6212),(157,4717),(157,6213),(178,6052),(178,6214),(177,5981),(177,6215),(142,3852),(142,3854),(142,3853),(142,3919),(142,3920),(142,3925),(142,3921),(142,3922),(142,3923),(142,3924),(142,3926),(142,3927),(142,7029),(142,7030),(142,3851),(204,7044)]
sociologia2 = [(104,3144),(104,3142),(104,3147),(104,5268),(104,5269),(134,3486),(134,3494),(134,5270),(134,5271),(149,4295),(149,5167),(149,6218),(149,5169),(149,6219),(175,5807),(175,6221),(175,5817),(175,6222),(141,3870),(141,3871),(141,3872),(141,3892),(141,3893),(141,3898),(141,3894),(141,3895),(141,3896),(141,3897),(141,3899),(141,3900),(141,7027),(141,7028),(141,3847),(166,5188)]
supervisores2 = [(94,2453),(94,3408),(94,6121),(94,3410),(94,6123),(136,3752),(136,6124),(136,3563),(136,6122),(159,4867),(159,4949),(159,6223),(159,4951),(159,6224),(176,5952),(176,6225),(176,5954),(176,6226),(143,3856),(143,3858),(143,3857),(143,3882),(143,3883),(143,3888),(143,3884),(143,3885),(143,3886),(143,3887),(143,3889),(143,3890),(143,7021),(143,7022),(143,3855),(163,5188)]
coordenadores2 = [(92,3433),(92,2374),(92,6995),(92,6125),(92,6996),(92,6126),(133,4111),(133,6997),(133,6127),(133,6998),(133,6128),(161,6156),(161,5212),(161,6999),(161,6227),(161,7000),(161,6228),(170,7004),(170,6229),(170,6230),(170,7062),(170,7061),(144,3860),(144,3862),(144,3861),(144,5175),(144,5176),(144,5236),(144,5242),(144,6141),(144,3932),(144,3933),(144,5237),(144,3936),(144,7031),(144,7032),(144,5177),(164,5160)]
diretores2 = [(93,6164),(93,2421),(93,6129),(93,2400),(93,6130),(135,3516),(135,6131),(135,3530),(135,6132),(153,4424),(153,4398),(153,6233),(153,4412),(153,6234),(174,5753),(174,6231),(174,5766),(174,6232),(145,3864),(145,3866),(145,3865),(145,3910),(145,3902),(145,3907),(145,3903),(145,3904),(145,3905),(145,3906),(145,3908),(145,3909),(145,7023),(145,7024),(145,3863),(165,5163)]

courses = {'Ciencias-ano1':ciencias1,
           'Biologia-ano1':biologia1,
           'Supervisores-ano1':supervisores1,
           'Coordenadores-ano1':coordenadores1,
           'Diretores-ano1':diretores1,
           'Ciencias-ano1':ciencias2,
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
    d = os.path.expanduser('~/redefor-analises/dados/notas')
    export_grades(courses,d, sync=False)
    print "Agora, faça um rsync -av "+d+" atp.usp.br:/var/www/dados/redefor/"
    print "(Use rsync -av --delete se quiser remover arquivos inexistentes no diretório local do servidor remoto atp.usp.br)"
