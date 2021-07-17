#! /usr/bin/env python3
import re, sys
variables = {}
global line; line = -1
exprs = {
    "pn_expr" : r"(\+|\-|\*|\/) ([0-9]+|(\w+)) ([0-9]+|(\w+))", # num expression
    "bool_expr" : r"(\=\=|\!\=|\>|\<|\<=|\>=) ([0-9]+|(\w+)) ([0-9]+|(\w+))" # bool expression
}
statements = {
    "var_exp"   : r"(\w+) \= %s" % (exprs["pn_expr"]), # var = num expression
    "var_bex"   : r"(\w+) \= %s" % (exprs["bool_expr"]), # var = bool expression
    "var_cst"   : r"(\w+) \= ([0-9]+|(\w+))", # var = literal
    "a_cond_go" : r"\b(goto) [0-9]+ (\w+)", # goes to line x if variable is true
    "a_print_v" : r"\b(print) (\w+)", # print value of variable
    "a_input_v" : r"\b(input) (\w+)", # get numeric input into variable
}
all_matches = {
    "var_exp"  : statements["var_exp"],
    "var_bex"  : statements["var_bex"],
    "var_cst"  : statements["var_cst"],
    "pn_expr"  : exprs["pn_expr"],
    "bool_expr": exprs["bool_expr"],
    "a_cond_go": statements["a_cond_go"],
    "a_print_v": statements["a_print_v"],
    "a_input_v": statements["a_input_v"],
}
def lex(code):
    for m in all_matches:
        match = re.search(all_matches[m], code)
        if match:
            return (m, code.split(' '))
    raise SyntaxError("invalid expression %s" % code)
class BinOp:
    def __init__(self, operator, p1, p2):
        self.operator = operator
        self.p1 = p1
        self.p2 = p2
    def resolve(self):
        if not self.p1.isdigit(): self.p1 = variables[self.p1]
        if not self.p2.isdigit(): self.p2 = variables[self.p2]
        return eval("%s %s %s" % (self.p1, self.operator, self.p2))
class VarDec:
    def __init__(self, name, value):
        self.name = name
        self.value = value
    def resolve(self):
        if type(self.value) is BinOp: self.value = self.value.resolve()
        elif not self.value.isdigit() : self.value = variables[self.value]
        variables[self.name] = self.value
        return variables
class Action:
    def __init__(self, action, params):
        self.action = action
        self.params = params
    def resolve(self):
        if self.action == "goto": 
            global line
            if variables[self.params[1]]: line = int(self.params[0]) - 2
        elif self.action == "print": print(variables[self.params[0]])
        elif self.action == "input":
            got_in = input()
            if not got_in.isdigit(): raise SyntaxError("only numeric values are supported.")
            variables[self.params[0]] = int(got_in)
def parse(type, tokens):
    if "var" in type:
        if type == "var_cst": return VarDec(tokens[0], tokens[2])
        else: return VarDec(tokens[0], BinOp(tokens[2], tokens[3], tokens[4]))
    elif "expr" in type: return BinOp(tokens[0], tokens[1], tokens[2])
    elif "a_" in type: return Action(tokens[0], tokens[1:])
    else: raise Exception("something has gone terribly wrong.")
def interpret(node):
    return node.resolve()
if __name__ == "__main__":
    if len(sys.argv) == 1:
        while True:
            try:
                get_in = input('> ')
                print(interpret(parse(*lex(get_in))))
            except EOFError: # the user pressed ^D
                print('')
                break
            except KeyboardInterrupt: # the user pressed ^C
                print('')
                break
            except Exception as err:
                print(err)
    else:
        program = open(sys.argv[1]).read().split('\n')
        while line < len(program) - 1:
            line += 1
            if program[line].isspace() or program[line] == "" or program[line][0] == ';': 
                continue
            else:
                interpret(parse(*lex(program[line])))
