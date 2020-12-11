empty_types = {
    "INT": "0",
    "FLOAT": "0.0",
    "STRING": ""
}

class Node():
    def __init__(self):
        pass


class WhileNode(Node):
    def __init__(self, expression, code):
        Node.__init__(self)
        self.expression = expression
        self.code = code

    def __repr__(self):
        expr = ""
        for entry in self.expression:
            expr += entry + " "
        code = ""
        for segment in self.code:
            code += "\t" + segment.__repr__() + "\n"
        return "while " + expr + ":\n" + code + "END_WHILE"


class IfNode(Node):
    def __init__(self, expression, code):
        Node.__init__(self)
        self.expression = expression
        self.code = code
    
    def __repr__(self):
        expr = ""
        for entry in self.expression:
            expr += entry + " "
        code = ""
        for segment in self.code:
            code += "\t" + segment.__repr__() + "\n"
        return "if " + expr + ":\n" + code + "END_IF"


class DefFunc(Node):
    def __init__(self, name, return_type, params, code):
        Node.__init__(self)
        self.name = name
        self.return_type = return_type
        self.params = params
        self.code = code

    def __repr__(self):
        full_str = self.return_type + " " + self.name + "("
        
        for param in self.params:
            full_str += param.__repr__() + ", "

        full_str += "):"
        for segment in self.code:
            full_str += "\n\t" + segment.__repr__()
        return full_str + "\nEND_FUNC"


class ExeFunc(Node):
    def __init__(self, name, param_names, storing_var):
        Node.__init__(self)
        self.name = name
        self.param_names = param_names
        self.storing_var = storing_var

    def __repr__(self):
        params = ""
        for param in self.param_names:
            params += param + ", "
        if self.storing_var:
            return self.name + "(" + params + ") -> " + self.storing_var
        else:
            return self.name + "(" + params + ")"


class Return(ExeFunc):
    def __init__(self, param_name):
        ExeFunc.__init__(self, "return", [param_name], None)


class Operation(Node):
    def __init__(self, rhs, operator, lhs):
        Node.__init__(self)
        self.rhs = rhs
        self.operator = operator
        self.lhs = lhs
    
    def __repr__(self):
        return self.rhs + " " + self.operator + " " + self.rhs


class AssignVar(Node):
    def __init__(self, name, var_type, value):
        Node.__init__(self)
        self.name = name
        self.var_type = var_type
        self.value = value
        self.check_if_empty_value()

    def check_if_empty_value(self):
        if self.value == "pustka":
            self.value = empty_types[self.var_type]

    def __repr__(self):
        return self.var_type + " " + self.name + " = " + self.value


class AssignList(AssignVar):
    def __init__(self, name, list_type, values):
        AssignVar.__init__(self, name, list_type, values)
    
    def __repr__(self):
        vals = ""
        for value in self.value:
            vals += value + ", "
        return self.var_type[0] + ";" + self.var_type[1] + " " + self.name + " = (" + vals + ")"


class ChangeVar(Node):
    def __init__(self, name, value):
        Node.__init__(self)
        self.name = name
        self.value = value
    
    def __repr__(self):
        val = ""
        for value in self.value:
            val += value + " "
        return "CHANGE " + self.name + " = " + val


class AST():
    def __init__(self, segments):
        self.segments = segments
    
    def __repr__(self):
        output = ""
        for segment in self.segments:
            output += segment.__repr__() + "\n"
        return output