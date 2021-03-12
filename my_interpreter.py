import nodes as _nodes
from nodes import get_entry_by_name, unfold_variables
import copy
from my_parser import Parser
from my_lexer import lex
from typing import List, Tuple, Any


def interpret(nodes: List[_nodes.Node], node_count: int=0, VARS: List[Tuple[str, str, Any]]=[], FUNCS: List[Tuple[str, _nodes.DefFunc]]=[]) -> Tuple[List[Tuple[str, str, Any]], List[Tuple[str, _nodes.DefFunc]]]:
    ''' Function that interpretes the given code

    nodes: A list of nodes that contain what needs to happen
    node_count: A counter to keep track what nodes have been executed already
    VARS: A list keeping track of all created variables that are currently available
    FUNCS: A list keeping track of all created functions that are currently available
    return: The VARS and FUNCS that are currently available
    '''
    if node_count == len(nodes):
        # If last node has been ran
        return VARS, FUNCS
    
    node = nodes[node_count]
    if isinstance(node, _nodes.WhileNode):
        # Register condition
        lhs = node.lhs if not get_entry_by_name(VARS, node.lhs, 0) else get_entry_by_name(VARS, node.lhs, 0)[-1]
        rhs = node.rhs if not get_entry_by_name(VARS, node.rhs, 0) else get_entry_by_name(VARS, node.rhs, 0)[-1]
        
        ans = node.condition.evaluate_statement(lhs, rhs)
        # Check whether condition is True or False
        if ans:
            # New vars need to be read, 'cause the ones used in the condition could change
            new_VARS, new_FUNCS = interpret(node.code, 0, VARS, FUNCS)
            # Keep repeating until ans is false
            end_VARS, end_FUNCS = interpret([node], 0, new_VARS, new_FUNCS)
            # Go to the next node
            return interpret(nodes, node_count + 1, end_VARS, end_FUNCS)
        else:
            # Go to the next node
            return interpret(nodes, node_count + 1, VARS, FUNCS)

    elif isinstance(node, _nodes.IfNode):
        # Register condition
        var_lhs = node.lhs if not get_entry_by_name(VARS, node.lhs, 0) else get_entry_by_name(VARS, node.lhs, 0)[-1]
        var_rhs = node.rhs if not get_entry_by_name(VARS, node.rhs, 0) else get_entry_by_name(VARS, node.rhs, 0)[-1]
        
        lhs = unfold_variables(VARS, [var_lhs])[0]
        rhs = unfold_variables(VARS, [var_rhs])[0]
        
        ans = node.condition.evaluate_statement(lhs, rhs)
        # Check whether condition is True or False
        if ans:
            # Run the code within if-statement
            new_VARS, new_FUNCS = interpret(node.code, 0, VARS, FUNCS)
            # Go to next node
            return interpret(nodes, node_count + 1, new_VARS, new_FUNCS)
        else:
            # Go to next node
            return interpret(nodes, node_count + 1, VARS, FUNCS)

    elif isinstance(node, _nodes.DefFunc):
        # Got to next node, and add new function to FUNCS
        return interpret(nodes, node_count + 1, VARS, FUNCS + [[node.name, node]])

    elif isinstance(node, _nodes.Return):
        returns = unfold_variables(VARS, node.param_names)
        return returns if len(returns) > 1 else returns[0]

    elif isinstance(node, _nodes.Print):
        print(unfold_variables(VARS, node.param_names))
        return interpret(nodes, node_count + 1, VARS, FUNCS)
    
    elif isinstance(node, _nodes.ExeFunc) and node.name == "len":
        new_VARS = list(filter(lambda var: var[0] != node.storing_var, VARS)) + [[node.storing_var, 
                        "INT", len(get_entry_by_name(VARS, node.param_names[0], 0)[-1])]]
        return interpret(nodes, node_count + 1, new_VARS, FUNCS)

    elif isinstance(node, _nodes.ExeFunc):
        # Find selected function
        selected_func = get_entry_by_name(FUNCS, node.name, 0, exception=True)[-1]
        # Create new vars, rename vars because the given vars are named differently than the ones mentioned in the function declaration
        new_VARS = node.get_new_vars(VARS, selected_func.params)
        # Run all the code within the selected function
        result = interpret(selected_func.code, 0, new_VARS, FUNCS)
        # If something is returned, add it to the list of variables
        if selected_func.return_type:
            new_VARS = list(filter(lambda var: var[0] != node.storing_var, VARS)) + [[node.storing_var, 
                        get_entry_by_name(FUNCS, node.name, 0)[-1].return_type, result]]
            return interpret(nodes, node_count + 1, new_VARS, FUNCS)
        else:
            return interpret(nodes, node_count + 1, VARS, FUNCS)

    elif isinstance(node, _nodes.AssignVar):
        # If variable is already assigned, remove the existing entry
        if get_entry_by_name(VARS, node.name, 0):
            new_VARS = list(filter(lambda x: x[0] != node.name, VARS))
        else:
            new_VARS = VARS

        # Go to next node, and add new variable to VARS
        if type(node.value) == str:
            if "-" in node.value:
                # If the variable is a entry within a list
                selected_list = get_entry_by_name(new_VARS, node.value[:node.value.find("-")], 0)[-1] if get_entry_by_name(new_VARS, node.value[:node.value.find("-")], 0) else int(node.value[:node.value.find("-")])
                selected_index = get_entry_by_name(new_VARS, node.value[node.value.find("-") + 1:], 0)[-1] if get_entry_by_name(new_VARS, node.value[node.value.find("-") + 1:], 0) else int(node.value[node.value.find("-") + 1:])
                new_var = type(node)(node.name, node.var_type, selected_list[selected_index])
                return interpret(nodes, node_count + 1, new_VARS + [[new_var.name, new_var.var_type, new_var.value]], FUNCS)
        new_var = type(node)(node.name, node.var_type, node.value)
        return interpret(nodes, node_count + 1, new_VARS + [[new_var.name, new_var.var_type, new_var.value]], FUNCS)

    elif isinstance(node, _nodes.ChangeVar):
        # Get the changed value
        new_val = node.apply_change(VARS)
        # Save a new variable with the same name and new value
        var_type = get_entry_by_name(VARS, node.name, 0, exception=True)[1]
        new_var = _nodes.AssignVar(node.name, var_type, new_val)
        new_VARS = list(filter(lambda var: var[0] != node.name, VARS)) + [[new_var.name, new_var.var_type, new_var.value]]
        # Go to next node
        return interpret(nodes, node_count + 1, new_VARS, FUNCS)


def main():
    tokens = lex("test_2.txt")
    AST = Parser(tokens).get_AST()
    interpret(AST.segments)


# main()
