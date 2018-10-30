#Cloudboobk
import ply.lex as lex
from ply.lex import TOKEN
import re
import parser
import token
import math


#file = "agent.py"
#file = "cloudbook_maker.py"
file = "pruebas.py"

tokens = ['FUN_DEF','COMMENT','LOOP_FOR','LOOP_WHILE','IF','TRY','PRINTV2', 'PRINTV3','FUN_INVOCATION','PYTHON_INVOCATION','INVOCATION','ANY_LINE']

#fundefintion =r'[\s]*[d][e][f][\s]*'+r'[a-zA-Z_][a-zA-Z_0-9]*'+r'[\s]*[(][\d\D\s\S\w\W]*[)][\s]*[:][\n]*'
fundefintion =r'[d][e][f][\s]*'+r'[a-zA-Z_][a-zA-Z_0-9]*'+r'[\s]*[(][\d\D\s\S\w\W]*[)][\s]*[:][\n]*'
t_ignore = " \n"

#functions = []
#fun_invocations = []
#token_list = []



def t_COMMENT(t):
	r'\#.*'
	pass

def t_PRINTV3(t):#TODO Probarlo mas.
	r'[p][r][i][n][t][ ]*[(][\d\D\s\S\w\W]*'
	t.type = 'PRINTV3'
	return t

def t_PRINTV2(t):#TODO Probarlo mas.
	r'[p][r][i][n][t][ ][\d\D\s\S\w\W]*'
	t.type = 'PRINTV2'
	return t

@TOKEN(fundefintion)
def t_FUN_DEF(t):#decorators not observed
    #r'[d][e][f][\s]+[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = 'FUN_DEF'
    t.value = t.value.split(" ")[1]
    #t.value = t.value.replace('\t','')
    t.value = re.sub(r'\s*',"",t.value)
    #t.value = t.value.split("(")[0]
    return t

def t_LOOP_FOR(t):#very simple for, not evaluated targetlist
	#r'[\s]*[f][o][r][\s]+[\d\D\s\S\w\W][\s]+[i][n][\s]+[\d\D\s\S\w\W]+'
	r'[f][o][r][\s]+[\d\D\s\S\w\W][\s]+[i][n][\s]+[\d\D\s\S\w\W]+'
	t.type = 'LOOP_FOR'
	t.value = t.value.split(" ")[3]
	t.value = t.value[:len(t.value)-2]
	#value = len(eval(loop_st[left:right]))
	try:
		t.value = len(eval(t.value))#only this kind of iterator?
	except:
		t.value = 100
	return t

def t_LOOP_WHILE(t):
	r'[w][h][i][l][e][\s]+[\d\D\s\S\w\W]*'
	t.type = 'LOOP_WHILE'
	t.value = 100
	return t

def t_IF(t):
	r'[i][f][\s]+[\d\D\s\S\w\W]+[:][\s]*[\n]'
	t.type = 'IF'
	t.value = 1
	return t

def t_TRY(t):
	r'[t][r][y][\s]*[:][\s]*[\n]'
	t.type = 'TRY'
	t.value = 1
	return t

#def t_FUN_INVOCATION(t):
def t_INVOCATION(t):
	#r'[\s]*[a-zA-Z_][a-zA-Z_0-9]*[(][\d\D\s\S\w\W]*[)][\s]*[\n]*'
	r'[a-zA-Z_][a-zA-Z_0-9]*[.]*[a-zA-Z_][a-zA-Z_0-9]*[(][\d\D\s\S\w\W]*[)][\s]*[\n]*'#initial part, complete invocation
	#print('Trad invocation:',t.value)
	#t.value = t.value[:len(t.value)-1]
	if (t.value.find("\n")!=-1):
		t.value = t.value.replace("\n","") 
	else:
		t.value = t.value
	#print('Trad invocation:',t.value)
	t.value = re.sub(r'[(][\d\D\s\S\w\W]*[)][\s]*',"",t.value)
	#print('Trad invocation:',t.value)
	t.value = re.sub(r'\s*',"",t.value)
	t.type = 'INVOCATION'
	return t

#def t_ANY_LINE(t):
#	r'[\d\D\s\S\w\W]+'
#	t.type = 'ANY_LINE'
#	return t

def t_error(t):
    #print("Illegal characters!")
    t.lexer.skip(1)

def tokenize():
	token_list = []
	lexer = lex.lex()

	with open(file,'r') as fi:
	    
	    for i,line in enumerate(fi,start=1):
	        lexer.input(line)
	        #indent level: only if tabs before text, not counted else
	        indent_level = line.count('\t')

	        cont = True
	        while cont:
	            tok = lexer.token()
	            if not tok:
	                #cont = False
	                break
	            tok.lineno = i
	            #print(tok)
	            token_list.append(tok)

	return token_list


def function_scanner():
	token_list = tokenize()
	function_names = []
	for i in token_list:
		if i.type == 'FUN_DEF':
			function_names.append(i.value.split("(")[0])#cutre
	return function_names

def function_parser():
	print("entro en el parser")
	token_list = tokenize()
	print(token_list)
	function_names = function_scanner()
	matrix = create_matrix(function_names)
	#print_matrix(matrix)
	invocator = ""
	level = 0
	n = 0
	level_loop = 0
	last_value = n
	levels = []
	values = []
	loop_levels = []
	#levels.append(0)
	for tok in token_list:
		if tok.type == 'FUN_DEF':#not for classes only procedimental programs
			level = tok.lexpos
			if tok.value.find("(")!=-1:
				invocator = tok.value.split("(")[0]
			else:
				invocator = tok.value
			n = 1
			last_value = 1
			#level = 1
			levels = []
			values = []
			#levels.append(level)
			#values.append(n)
			levels.append(1)
			values.append(1)
			print(tok.value + " levels: "+str(levels) +" values: "+ str(values))
			continue
		#if tok.lexpos > levels[-1]:#ignore indent 0
		if tok.lexpos > 0:#ignore indent 0
			if tok.type == 'INVOCATION' and tok.value in function_names:
				index_invocator = function_names.index(invocator)+1
				index_invoked = function_names.index(tok.value)+1
				#before assign value to matrix compare value and indentation
				#if tok.lexpos-levels[-1] == 1:
				#	print("Llamada de valor 1",tok.lexpos," y ", levels[-1])
				#	n = int(1)
				#else:#more indent than one
				#	n = values[tok.lexpos-1]
				n = values[tok.lexpos-1]
				matrix[index_invoked][index_invocator] += int(n)
				print("La funcion: "+invocator+" invoca a "+ tok.value + " " + str(n) + " veces")
				#last_value = n
			if tok.type == 'LOOP_FOR':
				#level = tok.lexpos
				n = n*tok.value
				last_value = tok.value
				level_loop +=1
				values.append(n)
				loop_levels.append(tok.lexpos)
				levels.append(tok.lexpos+1)
				print("Bucle for, niveles: "+str(levels)+ "valores: "+ str(values))
			if tok.type == 'LOOP_WHILE':
				n = n * tok.value
				values.append(n)
				levels.append(tok.lexpos+1)
				print("Bucle while, niveles: "+str(levels)+ "valores: "+ str(values))
		if tok.lexpos == 0:#ignore indent 0
			n=0
			level = 0
			levels.append(level)
	print_matrix(matrix)

def parser():
	pass

def create_matrix(function_list):
	num_cols = len(function_list)+1
	num_rows = num_cols
	matrix = [[None] * num_cols for i in range(num_rows)]
	matrix[0][0] = 'Matrix'
	for i in range(1,num_rows):
		matrix[0][i] = function_list[i-1]
	#print matrix[0]
	for i in range(1,num_rows):
		matrix[i][0] = function_list[i-1]
	for i in range(1,num_rows):
		for j in range(1,num_cols):
			matrix[i][j]=0
	return matrix

def print_matrix(matrix):
	num_cols=len(matrix[0])
	num_rows=len(matrix)
	for i in range(0,num_rows):
		print (matrix[i])


#function_names = function_scanner()
#print(function_names)
#function_parser()

toklist = tokenize()
for i in toklist:
	print(i)

