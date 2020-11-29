from lexer import lexer, token_types
import re
import sys


class Node():
    def __init__(self, type):
        self.type = type

class WhileNode(Node):
    def __init__(self, expression, code):
        Node.__init__(self, "WHILE")
        self.expression = expression
        self.code = code


class IfNode(Node):
    def __init__(self, expression, code):
        Node.__init__(self, "IF")
        self.expression = expression
        self.code = code


class DefFunc(Node):
    def __init__(self, name, return_type, params, param_types, code):
        Node.__init__(self, "FUNC_DEF")
        self.name = name
        self.return_type = return_type
        self.params = params
        self.param_types = param_types
        self.code = code


class ExeFunc(Node):
    def __init__(self, name, param_names, storing_var):
        Node.__init__(self, "FUNC_EXE")
        self.name = name
        self.param_names = param_names
        self.storing_var = storing_var


class AssignVar(Node):
    def __init__(self, name, var_type):
        Node.__init__(self, "VAR")
        self.name = name
        self.var_type = var_type


class Comment(Node):
    def __init__(self, comment):
        Node.__init__(self, "COMMENT")
        self.comment = comment


def main():
    code = re.split("(\n)| |, ", open("custom_code.txt", "r").read())
    sys.setrecursionlimit(len(code) * 2)
    print(len(code))
    print(lexer(code, 0, token_types, []))


main()