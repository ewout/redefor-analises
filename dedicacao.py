

import MySQLdb as mysql


#config

inativmin = 30 #escolha do tempo maximo de inatividade em minutos
userid = 2 #id do usuario



db = mysql.connect(host="localhost", user="root", db="moodle_redefor") #conecta com a base
c = db.cursor()
c.execute("""select time from mdl_log where userid = %s order by time asc""", (userid,)) #carrega uma lista com as entradas no moodle log para um usuario
temp = c.fetchall() 


tempo = list(temp)
t =[]
#print tempo

for x in tempo:
	t.append(x[0])
#print t

n = 0
s = [t[0]]
inativsec = inativmin*60
tempototal = 0L

for i, y in enumerate(t[0:-1]):
#	print (t[i+1]-y)
	if  (t[i+1]-y) > inativsec:
		temposecao = s[-1] - s[0]
		tempototal += temposecao
#		print s
		s = [t[i+1]]
#		print temposecao, tempototal	

	else:
		s.append(y)
print tempototal/3600
