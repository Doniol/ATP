import nodes
from nodes import get_entry_by_name
import copy


def visit_nodes(self, nodes, node_count, VARS, FUNCS):
    # Errors need to be implemented; types, no var, no func, variable already created etc.
    # Create own implementation for python keyword "in"
    if node_count == len(nodes):
        # If last node has been ran
        return VARS, FUNCS
    
    node = nodes[node_count]
    if isinstance(node, nodes.AssignVar) or isinstance(node, nodes.AssignList):
        # Go to next node, and add new variable to VARS
        visit_nodes(nodes, node_count + 1, VARS + [node.name, node.var_type, node.value], FUNCS)

    if isinstance(node, nodes.ChangeVar):
        # Get the changed value
        new_val = node.apply_change(0, VARS)
        # Save a new variable with the same name and new value
        var_type = get_entry_by_name(VALS, node.name, 0)[1]
        new_VALS = [val for val in VALS if val[0] != node.name] + [node.name, var_type, new_val]
        # Go to next node
        visit_nodes(nodes, node_count + 1, new_VALS)

    elif isinstance(node, nodes.IfNode):
        # Register expression
        lhs = node.expression[0] if node.expression[0] not in VARS else get_entry_by_name(VARS, node.expression[0], 0)[0]
        rhs = node.expression[-1] if node.expression[-1] not in VARS else get_entry_by_name(VARS, node.expression[-1], 0)[0]
        ans = node.expression.evaluate_statement(lhs[-1], rhs[-1])
        # Check whether expression is True or False
        if ans:
            new_VARS = copy.deepcopy(VARS)
            new_FUNCS = copy.deepcopy(FUNCS)
            # Run the code within if-statement
            visit_nodes(node.code, 0, new_VARS, new_FUNCS)
        # Got to next node
        visit_nodes(nodes, node_count + 1, VARS, FUNCS)

    elif isinstance(node, nodes.WhileNode):
        # Register expression
        lhs = node.expression[0] if node.expression[0] not in VARS else get_entry_by_name(VARS, node.expression[0], 0)[0]
        rhs = node.expression[-1] if node.expression[-1] not in VARS else get_entry_by_name(VARS, node.expression[-1], 0)[0]
        ans = node.expression.evaluate_statement(lhs, rhs)
        # Check whether expression is True or False
        if ans:
            new_VARS = copy.deepcopy(VARS)
            new_FUNCS = copy.deepcopy(FUNCS)
            # New vars need to be read, 'cause the ones used in the expression could change
            temp_VARS, temp_FUNCS = visit_nodes(node.code, 0, new_VARS, new_FUNCS)
            # Keep repeating until ans is false
            visit_nodes([node], 0, temp_VARS, temp_FUNCS)
        # Got to next node
        visit_nodes(nodes, node_count + 1, VARS, FUNCS)

    elif isinstance(node, nodes.DefFunc):
        # Got to next node, and add new function to FUNCS
        visit_nodes(nodes, node_count + 1, VARS, FUNCS + [node.name, node])

    elif isinstance(node, nodes.ExeFunc):
        # Find selected function
        selected_func = get_entry_by_name(FUNCS, node.name, 0)
        # Create new vars, rename vars because the given vars are named differently than the ones mentioned in the function declaration
        new_VARS = node.get_new_vars(0, VARS, selected_func.params, [])
        # Run all the code within the selected function
        visit_nodes(selected_func.code, 0, new_VARS, FUNCS)
        # Got to next node
        visit_nodes(nodes, node_count + 1, VARS, FUNCS)





def main():
    AST = nodes.AST()
    nodes = AST.segments
    visit_nodes(nodes, 0, [], [])