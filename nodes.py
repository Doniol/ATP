from __future__ import annotations
from typing import List, Any, Tuple

empty_types = {
    "INT": 0,
    "FLOAT": 0.0,
    "STRING": ""
}

def get_entry_by_name(entries: List[Any], name: str, index: int, exception: bool=False) -> Tuple[Any]:
    ''' Searches a list for an entry that starts with the given name

    entries: A list of different entries, each at the very least containing the entries' name as its' first variable
    name: The name of the desired entry
    index: An index denoting how far through the list the function has already searchhed
    exception: An option to throw an exception when no matching entry is found
    return: Either None or a matching entry
    '''
    if index == len(entries):
        if exception:
            raise Exception("No entry with name \'" + name + "\' found")
        return None
    if entries[index][0] == name:
        return entries[index]
    else:
        return get_entry_by_name(entries, name, index + 1, exception)


def unfold_variables(VARS: List[Any], targets: List[str], index: int=0, result: List[Any]=[]) -> Tuple[Any]:
    ''' A function that returns all variables that correspond to the given variable names

    VARS: A list filled with all currently recorded variables
    targets: A list filled with names of variables
    index: An index denoting how far through the list the function has already searched
    result: The resulting variables
    return: The resulting variables
    '''
    # If all targets have been checked
    if index == len(targets):
        return result

    # If current target does not refer to another variable; if it doesn't refer
    #  to another variable, it's automatically not a list
    elif not get_entry_by_name(VARS, targets[index], 0):
        return unfold_variables(VARS, targets, index + 1, result + [targets[index]])
    
    # If current target does refer to another variable
    else:
        # If current target refers to a list
        if type(get_entry_by_name(VARS, targets[index], 0)[-1]) == list:
            var = unfold_variables(VARS, get_entry_by_name(VARS, targets[index], 0)[-1])
        # If current target refers to a single variable
        else:
            var = unfold_variables(VARS, [get_entry_by_name(VARS, targets[index], 0)[-1]])
        return unfold_variables(VARS, targets, index + 1, result + var)


class Node():
    ''' Base class for all nodes
    '''
    def __init__(self) -> None:
        ''' Inits the node class
        '''
        pass
    
    def __repr__(self) -> str:
        ''' Function for returning a printable version of the class

        return: A str representation of the class
        '''
        return "node"


class WhileNode(Node):
    ''' A node for defining while-loops
    '''
    def __init__(self, condition: List[str], code: List[Node]) -> None:
        ''' Inits the class

        condition: A list containing the condition that needs to be true in order to contain looping
        code: A list of nodes that are to be executed if the condition is true
        '''
        Node.__init__(self)
        self.lhs, operator, self.rhs = condition
        self.condition = Condition(operator)
        self.code = code

    def __repr__(self) -> str:
        ''' Function for returning a printable version of the class

        return: A str representation of the class
        '''
        expr = self.lhs + " " + self.condition.__repr__() + " " + self.rhs
        code = "\n\t".join(list(map(lambda x: x.__repr__(), self.code)))
        return "while " + expr + ":\n\t" + code + "\n\tEND_WHILE"


class IfNode(Node):
    ''' A node for defining if-statements
    '''
    def __init__(self, condition: List[str], code: List[Node]) -> None:
        ''' Inits the class

        condition: A list containing the condition that needs to be true in order to run the given code
        code: A list of nodes that are to be executed if the condition is true
        '''
        Node.__init__(self)
        self.lhs, operator, self.rhs = condition
        self.condition = Condition(operator)
        self.code = code
    
    def __repr__(self) -> str:
        ''' Function for returning a printable version of the class

        return: A str representation of the class
        '''
        expr = self.lhs + " " + self.condition.__repr__() + " " + self.rhs
        code = "\n\t".join(list(map(lambda x: x.__repr__(), self.code)))
        return "if " + expr + ":\n\t" + code + "\n\tEND_IF"


class Condition():
    ''' A class for defining conditions
    '''
    def __init__(self, operator: str) -> None:
        ''' Inits the class

        operator: The relational operator that compares different variables
        '''
        self.operator = operator

    def evaluate_statement(self, input_lhs: Any, input_rhs: Any) -> bool:
        ''' Function for evaluating a condition with the given inputs

        input_lhs: The input on the left hand side of the relational operator
        input_rhs: The input on the right hand side of the relational operator
        return: The boolean that is the result of the evaluated condition
        '''
        # Make sure that both sides of the condition are of the same type
        if type(input_lhs) == str and type(input_rhs) != str:
            lhs = type(input_rhs)(input_lhs)
            rhs = input_rhs
        elif type(input_lhs) != str and type(input_rhs) == str:
            lhs = input_lhs
            rhs = type(input_lhs)(input_rhs)
        else:
            lhs = input_lhs
            rhs = input_rhs

        # Evaluate the correct condition
        if self.operator == "wiecej":
            return lhs > rhs
        elif self.operator == "mniej":
            return lhs < rhs
        elif self.operator == "nie":
            return lhs != rhs
        elif self.operator == "jest":
            return lhs == rhs
        else:
            raise Exception("Condition " + lhs + " " + self.operator + " " + rhs + " failed.")
    
    def __repr__(self):
        ''' Function for returning a printable version of the class

        return: A str representation of the class
        '''
        return self.operator


class DefFunc(Node):
    ''' A class for defining functions
    '''
    def __init__(self, name: str, return_type: str, params: List[AssignVar], code: List[Node]) -> Node:
        ''' Inits the class

        name: The name of the function
        return_type: The type of variable that the class returns
        params: The required parameters for running the function
        code: The nodes that need to be executed when running this function
        '''
        Node.__init__(self)
        self.name = name
        self.return_type = return_type
        self.params = params
        self.code = code

    def __repr__(self):
        ''' Function for returning a printable version of the class

        return: A str representation of the class
        '''
        full_str = self.return_type.__repr__() + " " + self.name + "("
        full_str += ", ".join(list(map(lambda x: x.__repr__(), self.params)))
        full_str += "):"
        full_str += "\n\t".join(list(map(lambda x: x.__repr__(), self.code)))
        return full_str + "\nEND_FUNC"


class ExeFunc(Node):
    ''' A class for defining how to run a function
    '''
    def __init__(self, name: str, param_names: List[str], storing_var: str=None) -> None:
        ''' Inits the class

        name: The name of the to be ran function
        param_names: The names of the parameters passed to the function
        storing_var: An optional variable that defines in what variable the result of the function needs to be saved
        '''
        Node.__init__(self)
        self.name = name
        self.param_names = param_names
        self.storing_var = storing_var

    def get_new_vars(self, VARS: List[Tuple[str, Any]], func_params: List[AssignVar], index: int=0):
        ''' Function for getting the correct variables for function start
        For every parameter desired by the function, get the corresponding variable name given to this class (in self.param_names).
        Then get the corresponding data for said variable name, combine this data with the name that the function itself gives to its'
         parameters, and return all of these new variables.
        Example:
            def foo_bar(one, two) is a function called foo_bar that requires 2 parameters: one and two.
            When called using foo_bar(test_1, test_2) it runs the function, and passes the variables test_1 and test_2
             as parameters one and two.
            To properly use the given variables of test_1 and test_2, the associated data needs to be fetched from the list
             with all available variables. This way the function actually receives the correct data.
            Then to properly use said data within the function itself, the names currently associated with the given data need to
             be changed to the parameter names expected by the function.
            This way the function receives the data that is associated with the originally passed variables, but under a name that the
             function actually expects and thus is useful to it.
            Basically, this happens:
            def foo_bar(one, two)
            VARS = [[test_1, 1], [test_2, 2], [test_3, 3], [test_4, 4]]
            foo_bar(test_1, test_2)
            VARS within function = [[one, data from test_1], [two, data from test_2]] = [[one, 1], [two, 2]]


        index: An integer denoting how far through the list of parameters the function has already gone
        VARS: A list of variables defined outside of the called function
        func_params: A list with the desired parameters of the called function
        returns: A list containing the renamed variables with their corresponding data
        '''
        if index == len(self.param_names):
            return []
        else:
            # Check if correct type of var has been entered
            entered_var = get_entry_by_name(VARS, self.param_names[index], 0, exception=True)
            if entered_var[1] != func_params[index].var_type:
                error = ("Expected variable of type " + func_params[index].var_type +
                        " but received " + entered_var[1])
                raise Exception(error)

            new_var = [func_params[index].name] + entered_var[1:]
            return self.get_new_vars(VARS, func_params, index=index + 1) + [new_var]

    def __repr__(self):
        ''' Function for returning a printable version of the class

        return: A str representation of the class
        '''
        params = ", ".join(self.param_names)
        if self.storing_var:
            return self.name + "(" + params + ") -> " + self.storing_var
        else:
            return self.name + "(" + params + ")"


class Return(ExeFunc):
    ''' A class for the return function, because this function is special
    '''
    def __init__(self, param_name):
        ''' Inits the class

        param_name: The name of the parameter that is to be returned
        '''
        ExeFunc.__init__(self, "return", [param_name])


class Print(ExeFunc):
    ''' A class for the print function, because this function is special
    '''
    def __init__(self, param_name):
        ''' Inits the class

        param_name: The name of the variable that is to be printed
        '''
        ExeFunc.__init__(self, "print", [param_name])


class AssignVar(Node):
    ''' A class for assigning new variables
    '''
    def __init__(self, name: str, var_type: str, value: Any) -> None:
        ''' Inits the class
        
        name: The name of the new variable
        var_type: The type of the new variable
        value: The data stored in the new variable
        '''
        Node.__init__(self)
        self.name = name
        self.var_type = var_type
        self.value = value
        self.value = self.correct_value_type(self.value)
    
    def correct_value_type(self, value: Any, index: int=0) -> Any:
        ''' Function that returns the given value as the correct type
        This is necessary since most of the time values are passed as strings, even when they're
         meant to be integers or floats.
        
        value: The value which is to be run through the function
        index: An integer denoting how far through the list of parameters the function has already gone
               In this case such a parameter is completely useless, it's only included so this function call
                can be used for assigning lists.
        return: The given value but of the correct type
        '''
        try:
            if value == "pustka":
                return empty_types[self.var_type]
            elif type(value) != str or (value.find("-") != -1 and value.find("-") != 0):
                return value
            else:
                return self.check_if_empty_value(value)
        except:
            raise Exception("Turning " + value + " from " + self.name + " into " + self.var_type + " not possible.")

    def check_if_empty_value(self, value: Any) -> Any:
        ''' A function that transforms the given value to the correct typing, if necessary

        value: The value that is to be transformed
        return: The transformed value
        '''
        if self.var_type == "INT":
            try:
                return int(value)
            except:
                error = ("Expected something of type INT but received \'" +
                        str(value) + "\' which can\'t be turned into a INT")
                raise Exception(error)
        elif self.var_type == "FLOAT":
            try:
                return float(value)
            except:
                error = ("Expected something of type FLOAT but received \'" +
                        str(value) + "\' which can\'t be turned into a FLOAT")
                raise Exception(error)
        elif self.var_type == "ANY":
            return value
        elif self.var_type == "STRING":
            return str(value)

    def __repr__(self):
        ''' Function for returning a printable version of the class

        return: A str representation of the class
        '''
        return self.var_type + " " + self.name + " = " + str(self.value)


class AssignList(AssignVar):
    ''' A class for assigning lists as new variables
    '''
    def __init__(self, name: str, list_type: str, values: List[Any]) -> None:
        ''' Inits the class

        name: The name of the new variable
        list_type: The types that the list is filled with
        values: The values that the list is filled with
        '''
        AssignVar.__init__(self, name, list_type, values)

    def correct_value_type(self, value: List[Any], index: int=0) -> None:
        ''' Function that returns the given values as the correct type
        This is necessary since most of the time values are passed as strings, even when they're
         meant to be integers or floats.
        
        value: The values which are to be run through the function
        index: An integer denoting how far through the list of values the function has already gone
        return: The given values but of the correct type
        '''
        if len(value) == index or value[index] == "pustka":
            return []
        else:
            return self.correct_value_type(value, index + 1) + [AssignVar.correct_value_type(self, value[index])]
            
    def __repr__(self):
        ''' Function for returning a printable version of the class

        return: A str representation of the class
        '''
        return "LIST;" + self.var_type + " " + self.name + " = " + str(self.value)


class ChangeVar(Node):
    ''' A class for changing existing variables
    '''
    def __init__(self, name: str, value: List[Any]) -> None:
        ''' Inits the class

        name: The name of the to be changed variable
        value: A list containing instructions for how to change the given variable
        '''
        Node.__init__(self)
        self.name = name
        self.value = value
    
    def apply_change(self, VARS: List[Tuple[str, Any]]) -> Any:
        ''' A function for applying a selected change to a selected variable
        Supported calculations are as follows: addition, subtraction, multiplication and division.

        VARS: A list of currently defined variables and their data
        return: The altered version of the given variable
        '''
        # Function limited to just one calculation when calculating new variable
        lhs = self.value[0] if not get_entry_by_name(VARS, self.value[0], 0) else get_entry_by_name(VARS, self.value[0], 0)[-1]
        rhs = self.value[2] if not get_entry_by_name(VARS, self.value[2], 0) else get_entry_by_name(VARS, self.value[2], 0)[-1]
        
        # 3 possible types: int, float and str
        # Float and int can be combined so they won't cause problems
        # String and string can be combined aswell
        # The only possible problem caused is when combining strings and 
        # numbers, so make sure this combination doesn't happen
        if type(lhs) == str and type(rhs) != str:
            lhs = type(rhs)(lhs)
        elif type(lhs) != str and type(rhs) == str:
            rhs = type(lhs)(rhs)

        if self.value[1] == "i":
            return lhs + rhs
        elif self.value[1] == "bez":
            return lhs - rhs
        elif self.value[1] == "razy":
            return lhs * rhs
        elif self.value[1] == "przez":
            return lhs / rhs
    
    def __repr__(self):
        ''' Function for returning a printable version of the class

        return: A str representation of the class
        '''
        return "CHANGE " + self.name + " = " + " ".join(self.value)


class AST():
    ''' Class for containing all nodes within a AST
    '''
    def __init__(self, segments: List[Node]) -> None:
        ''' Inits the class

        segments: A list containing all nodes within the AST
        '''
        self.segments = segments

    def __repr__(self) -> str:
        ''' Function for returning a printable version of the class

        return: A str representation of the class
        '''
        return "\n".join(list(map(lambda x: x.__repr__(), self.segments)))
