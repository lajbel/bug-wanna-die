#!/usr/bin/env python3

"""
IWANNADIE Language Interpreter
I already know this is by far the worst interpreter for a language in the world
																															 - Antikore, 2021
Update 1: In case isn't obvious, or is not the same as and
Created in 3 days
Usage: ./iwannadie.py <file>
Made using Python 3.9.5
"""

import sys, re, base64, random, math, os
file = None
vlist, markers, filename = {}, {}, sys.argv[1]

clear = lambda: os.system('clear')

try:
	file = open(filename)
except:
	sys.exit(0)

if file == None or not filename.endswith(".iwd"):
	sys.exit(0)

ln, current_line, excepted = 0, "", False
code = file.readlines()
file.close()
if (code[-1] != "die"): sys.exit(0)

# Execute all the code
def ExecuteCode():
	global ln, current_line, code
	PreInterpret()
	while ln < len(code):
		line = code[ln]
		formatted = FormatLine(line)
		if formatted.strip() != "" and not formatted.strip().startswith("@"):
			current_line = formatted.strip()
			ReadCommand(formatted)		
		ln += 1

# Find markers
def PreInterpret():
	global markers, ln, code
	while ln < len(code):
		line = code[ln]
		formatted = FormatLine(line)
		if formatted.strip() != "" and formatted.strip().startswith("@"):
			markers.update({formatted.strip()[1:]: ln})
		ln += 1
	ln = 0

# Format a line, to remove extra whiespaces or tabs, and comments
def FormatLine(line):
	xline = line.rstrip("\n ").strip()
	parsed = xline
	m = re.search(r"\"(.+?)\"", parsed)
	if m:
		parsed = parsed.replace(m.group(0), "")
	m = re.search(r"-- (.+?)+", parsed)
	if m:
		return xline.replace(m.group(0), "")
	return xline

# Read a command, checking the name and arguments
def ReadCommand(command):
	name = ""
	for c in command:
		if c != " ":
			name = name + c
		else:
			arguments = command.replace(name+" ", "",1)
			return InterpretCommand(name, arguments)
	return InterpretCommand(name, [])

# Interpret the comand to find subcommands and strings
def InterpretCommand(name, arguments):
	args, current, counter = [], "", ""
	for c in arguments:
		if c != "," or counter != "":
			if (c == "["):
				if ((len(counter) > 0 and counter[-1] != "\"") or len(counter) == 0):
					counter = counter + c
			elif (c == "]"):
				if (len(counter) > 0 and counter[-1] == "["):
					counter = counter[:-1]
			elif (c == "\""):
				if (len(counter) > 0 and counter[-1] == "\""):
					counter = counter[:-1]
				else:
					counter = counter + c
			current = current + c
		else:
			value = InterpretExpression(current)
			args.append(value)
			current = ""
	if (current != ""):
		value = InterpretExpression(current)
		args.append(value)
		current = ""
	if (counter != ""):
		CatchError(4)
	return ExecuteCommand(name, args)
	
# Execute the command (Yeah, ifelseifelseifelseifelse)
def ExecuteCommand(name, args):
	global vlist, markers, ln
	if (name == "print"):
		print(args[0])
		return None
	if (name == "set"):
		if isinstance(args[0], str):
			vlist.update({args[0]: args[1]})
		else:
			CatchError(5)
	try:
		if (name == "add"):
			if args[1] == 0:
				if isinstance(args[0], str):
					return vlist.get(args[0])
				else:
					return args[1]
			else:
				if isinstance(args[0], str):
					current = vlist.get(args[0])
					vlist.update({args[0]: current + args[1]})
					return current + args[1]
				else:
					return args[0] + args[1]
		if (name == "mul"):
			if isinstance(args[0], str):
				current = vlist.get(args[0])
				vlist.update({args[0]: current * args[1]})
				return current * args[1]
			else:
				return args[0] * args[1]
		if (name == "div"):
			if isinstance(args[0], str):
				current = vlist.get(args[0])
				vlist.update({args[0]: current / args[1]})
				return current / args[1]
			else:
				return args[0] / args[1]
		if (name == "mod"):
			if isinstance(args[0], str):
				current = vlist.get(args[0])
				vlist.update({args[0]: current % args[1]})
				return current % args[1]
			else:
				return args[0] % args[1]
	except KeyError:
		CatchError(3)
	except TypeError:
		CatchError(1)
	if (name == "goto"):
		destination = markers.get(args[0])
		if destination == None: CatchError(6) 
		ln = destination
	if (name == "goif"): 
		if args[1]: ln = markers.get(args[0])
	if (name == "doif"): 
		if not args[0]: 
			ln += 1
	if (name == "comp" or name == "compare"): 
		return args[0] > args[1]
	if (name == "check"):	
		return args[0] == args[1]
	if (name == "die"):		
		Exit()
	if (name == "input"):	
		return input(args[0])
	if (name == "and"):		
		return args[0] and args[1]
	if (name == "or"):		 
		return args[0] or args[1]
	if (name == "not"):		
		return not args[0]

  # a tomar por culo sex
	if (name == "type"):
		return str(type(args[0])).replace("<class '", "").replace("'>", "")
	if (name == "len"):
		return len(args[0])
	if (name == "random"): 
		return random.uniform(args[0], args[1])
	if (name == "floor"):	
		return math.floor(args[0])
	if (name == "round"):	
		return round(args[0])
	if (name == "char"):	 
		return args[0][args[1]]
	if (name == "clear"):
		clear()
		return None
	if (name == "int"): 
		try: return int(args[0]) 
		except: return None
	if (name == "text"):
		try: return str(args[0]) + str(args[1])
		except: CatchError(1)
	return None

# Interpet an expression, if its a variable, a subcommand, or an important value
def InterpretExpression(exp):
	exp = exp.strip()
	if (exp.startswith("#")):
		encoding = base64.b64encode(exp[1:].encode("utf-8"))
		return str(encoding, "utf-8")
	elif (exp.startswith("[") and exp.endswith("]")):
		return ReadCommand(exp[1:-1])
	elif (exp.startswith("\"") and exp.endswith("\"")):
		return exp[1:-1]
	elif (exp == "null"):
		return None
	elif (exp == "true"):
		return True
	elif (exp == "false"):
		return False
	else:
		try:
			return float(exp)
		except:
			CatchError(2)
		
# Return an error if something failed
def CatchError(error):
	global ln, current_line, excepted
	if (not excepted) and error != 0:
		print("")
		sentence = "Unexpected Error"
		if (error == 1):	 sentence = "Illegal operation"
		elif (error == 2): sentence = "Unknown expression"
		elif (error == 3): sentence = "I'm a teapot"
		elif (error == 4): sentence = "He's guilty"
		elif (error == 5): sentence = "Welcome to the dungeon"
		elif (error == 6): sentence = "Illegal movement"
		print("Error "+str(error)+": "+sentence)
		print("At line "+str(ln + 1)+": '"+current_line+"'")
	excepted = True
	sys.exit(0)

# Exit the program
def Exit():
	CatchError(0)

try:
	ExecuteCode()
except:
	CatchError(-1)