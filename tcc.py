#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pylab import *
from mdlib import *
import pandas as pd


courses = {'Ciencias':{'idambiente':108,'gradeitemtcc':7100,'idbanco':95,'nuspfield':''},
           'Biologia':{'idambiente':204,'gradeitemtcc':7098,'idbanco':98,'nuspfield': 'Número USP do cursista'},
           'Sociologia':{'idambiente':166,'gradeitemtcc':7097,'idbanco':99,'nuspfield': 'Número USP do cursista'},
           'Supervisores':{'idambiente':163,'gradeitemtcc':7096,'idbanco':91,'nuspfield': ''},
           'Coordenadores':{'idambiente':164,'gradeitemtcc':5160,'idbanco':93,'nuspfield': ''},
           'Diretores':{'idambiente':165,'gradeitemtcc':7093,'idbanco':96,'nuspfield': ''},
           }


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

def fichas (idbanco,nuspfield):
    'return dataframe indexed by nusp'
    r = loaddata("select r.id, r.userid, f.name,c.content from mdl_data_content c, mdl_data_fields f, mdl_data_records r where c.fieldid = f.id and r.id = c.recordid and r.dataid = %s" % idbanco, df=True)

    if nuspfield:
        df = r.pivot(index='id',columns='name',values='content')
        df = df.drop_duplicates(cols=nuspfield)
        df = df[df[nuspfield] != '']
        df = df.set_index(nuspfield,verify_integrity=True)
    else: #assumir que userid é de alunos
        df = r.pivot(index='userid',columns='name',values='content')
        df.index = df.index.map(idnumber)
        df = df[df.index != '']

    df.index = [int(i) if i else '' for i in df.index]
    return df


def frame(course):
    ''
    ambiente = course['idambiente']
    gradeitem = course['gradeitemtcc']
    users = courseusers(ambiente)
    userids = users['userid']
    frame = pd.DataFrame({'userid':userids})
    #    frame['Nome AVA'] = users['firstname']
    #frame['Sobrenome AVA'] = users['lastname']
    frame['Número USP'] = users['idnumber']
    frame['Nome Apolo'] = [pessoa(codpes)['nompes'] if codpes else '' for codpes in users['idnumber']]
    frame['Nota TCC'] = notas(userids,gradeitem)
    fichastcc = fichas(course['idbanco'],course['nuspfield'])
    fichastcc = fichastcc[['Título do Trabalho','Data da defesa']]
    converttodate = lambda x: datetime.datetime.fromtimestamp(int(x)).strftime('%Y-%m-%d')
    fichastcc['Data da defesa'] = fichastcc['Data da defesa'].apply(converttodate)
    frame = pd.merge(fichastcc,frame,left_index=True,right_on='Número USP', how="outer")
    # remover id do moodle antes de publicar
    del frame['userid']
    frame = frame[['Número USP','Nome Apolo','Título do Trabalho','Data da defesa','Nota TCC']]
    return frame

def moodle_date():
    return loaddata('select from_unixtime(timemodified) from mdl_grade_grades_history order by timemodified desc limit 1',from_cache=True,moodle='moodle_redefor')[0,0]

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
    moodledate = moodle_date()
    dstr =  '-' + moodledate.strftime('%Y-%m-%d')
    for coursename,course in courses.iteritems():
        print coursename
        df = frame(course)
        outfile = os.path.join(d+'/',coursename+'-tcc'+dstr)
        print "Writing to ", outfile
        df.to_csv(outfile + '.csv',index=False, sep='\t')
        try:
            # usar xlsx ao vez de xls aqui porque tem um problema com o xlwt e utf8...
            df.to_excel(outfile + '.xlsx', index = False)
        except ImportError:
            print "Faça um 'sudo pip install openpyxl' e tente novamente"

if __name__ == '__main__':
    import os
    d = os.path.expanduser('~/Dropbox/redefor-analises/dados/notas')
    if not os.path.exists(d):
        d = os.path.expanduser('~/redefor-analises/dados/notas')
    export_grades(courses,d)
