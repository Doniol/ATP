empty_types = {
    "INT": "0",
    "FLOAT": "0.0",
    "STRING": ""
}

def get_entry_by_name(entries, name, index):
    if entries[index][0] == name:
        return entries[index], index
    else:
        return get_entry_by_name(entries, name, index + 1)


#TODO: CLASSES NEED TO BE FUNCTIONAL, DONT USE FORLOOPS
#TODO: Change functions so they have default values in parameters, dont want to give 0 or [] for each result(s)
class Node():
    def __init__(self):
        pass

    def visit(self):
        pass


class WhileNode(Node):
    def __init__(self, expression, code):
        Node.__init__(self)
        self.lhs, comparator, self.rhs = expression
        self.expression = Expression(comparator)
        self.code = code

    def __repr__(self):
        expr = self.lhs + " " + self.expression.__repr__() + " " + self.rhs
        code = ""
        for segment in self.code:
            code += "\t" + segment.__repr__() + "\n"
        return "while " + expr + ":\n" + code + "END_WHILE"


class IfNode(Node):
    def __init__(self, expression, code):
        Node.__init__(self)
        self.lhs, comparator, self.rhs = expression
        self.expression = Expression(comparator)
        self.code = code
    
    def __repr__(self):
        expr = self.lhs + " " + self.expression.__repr__() + " " + self.rhs
        code = ""
        for segment in self.code:
            code += "\t" + segment.__repr__() + "\n"
        return "if " + expr + ":\n" + code + "END_IF"


class Expression():
    def __init__(self, comparator):
        self.comparator = comparator

    def evaluate_statement(self, lhs, rhs):
        if self.comparator == "wiecej":
            return lhs > rhs
        elif self.comparator == "mniej":
            return lhs < rhs
        elif self.comparator == "nie":
            return lhs != rhs
        elif self.comparator == "jest":
            return lhs == rhs
        else:
            # ERROR
            return
    
    def __repr__(self):
        return self.comparator


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

    def get_new_vars(self, index, vars, new_names, result):
        if index == len(self.param_names):
            return results
        else:
            new_var = new_names[index] + get_entry_by_name(vars, self.param_names[index], 0)[0][1:]
            return self.get_new_vars(index + 1, vars, result + new_var)

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
    
    def apply_change(self, index, VARS, result=None):
        if result == None:
            if self.value[index + 1] == "i":
                var_1 = self.value[index] if self.value[index] not in VARS else get_entry_by_name(VARS, self.value[index], 0)
                var_2 = self.value[index + 2] if self.value[index + 2] not in VARS else get_entry_by_name(VARS, self.value[index + 2], 0)
                return self.apply_change(index + 2, VARS, result + var_1 + var_2)
            else:
                return entries[0]
        else:
            if self.value[index + 1] == "i":
                var = self.value[index] if self.value[index] not in VARS else get_entry_by_name(VARS, self.value[index], 0)
                return self.apply_change(index + 2, VARS, result + var)
            else:
                return result
    
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