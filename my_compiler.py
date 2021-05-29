import nodes as _nodes
from nodes import AST, get_entry_by_name, unfold_variables
from my_parser import Parser
from my_lexer import lex
from typing import Dict, List, Tuple, Any


def get_data_asm(nodes: List[_nodes.Node], file, curr_name: str="", counts: Dict[str, int]={}, node_count: int=0):
    ''' Count amount of local variables each function creates, later to be used
         to calculate reserved stack size.
    '''
    if node_count == len(nodes):
        return counts
    
    node = nodes[node_count]
    if isinstance(node, _nodes.DefFunc):
        in_function_counts = get_data_asm(node.code, file, node.name, counts)
        # Combine old and additional counts
        new_counts = {key: {**counts.get(key, {}), **in_function_counts.get(key, {})}
                for key in set(counts).union(in_function_counts)}

        function_param_counts = get_data_asm(node.params, file, node.name, new_counts)
        # Combine old and additional counts
        newer_counts = {key: {**new_counts.get(key, {}), **function_param_counts.get(key, {})}
                    for key in set(new_counts).union(function_param_counts)}

        return get_data_asm(nodes, file, curr_name, newer_counts, node_count + 1)

    elif isinstance(node, _nodes.AssignVar):
        if node.var_type == "STRING":
            file.write(node.name + ":\n\t.asciz \"" + node.value + "\\n\"\n\n")

        additional_counts = {curr_name: {node.name: [len(counts.get(curr_name, [])) * 4, node.var_type]}}
        # Combine old and additional counts
        new_counts = {key: {**counts.get(key, {}), **additional_counts.get(key, {})}
                    for key in set(counts).union(additional_counts)}

        return get_data_asm(nodes, file, curr_name, new_counts, node_count + 1)

    elif isinstance(node, _nodes.WhileNode) or isinstance(node, _nodes.IfNode):
        additional_counts = get_data_asm(node.code, file, curr_name, counts)

        # Combine old and additional counts
        new_counts = {key: {**counts.get(key, {}), **additional_counts.get(key, {})}
                    for key in set(counts).union(additional_counts)}
        
        return get_data_asm(nodes, file, curr_name, new_counts, node_count + 1)

    else:
        return get_data_asm(nodes, file, curr_name, counts, node_count + 1)


def access_local_stack(func_name, var_name, all_vars, register, load):
    if load:
        return "\tLDR " + register + ", [SP, #" + str(all_vars[func_name][var_name][0]) + "]\n"
    else:
        return "\tSTR " + register + ", [SP, #" + str(all_vars[func_name][var_name][0]) + "]\n"


def interpret(nodes: List[_nodes.Node], curr_func: str, all_vars: Dict[str, List[str]], node_count: int=0, asm: str=""):
    ''' Function that interpretes the given code
    '''
    if node_count == len(nodes):
        return asm
    
    node = nodes[node_count]
    if isinstance(node, _nodes.WhileNode):
        # ASM will be as follows:
        # Tag for loop name
        # if-statement, if True goto loop tag
        # Goto loop end
        # Loop tag
        # Whatever loop does
        # Goto loop name
        # Tag for loop end

        # Note what happens
        comment = "@While-loop\n"

        # Create label
        label = "_" + str(node.id) + "_while"
        start = label + ":\n"

        # Load variables into R0 and R1, check if it's a raw number
        #TODO: Negative raw number
        try:
            loader = "\tMOV R0, #" + str(int(node.lhs)) + "\n"
        except:
            loader = access_local_stack(curr_func, node.lhs, all_vars, "R0", True)
        
        try:
            loader += "\tMOV R0, #" + str(int(node.rhs)) + "\n"
        except:
            loader = access_local_stack(curr_func, node.rhs, all_vars, "R1", True)

        # Write correct comparison
        if node.condition.operator == "wiecej":
            condition = "\tCMP R0, R1\n\tBHI " + label + "_loop\n"
        elif node.condition.operator == "mniej":
            condition = "\tCMP R0, R1\n\tBLO " + label + "_loop\n"
        elif node.condition.operator == "nie":
            condition = "\tCMP R0, R1\n\tBNE " + label + "_loop\n"
        elif node.condition.operator == "jest":
            condition = "\tCMP R0, R1\n\tBEQ " + label + "_loop\n"
        else:
            raise Exception("Incompatible operator for while-loop used")

        # Branch to end-tag
        branch_end = "\tB " + label + "_end\n"

        # Create tag for loop
        loop_tag = label + "_loop:\n"
        # Do whatever needs to be done within loop
        loop_insides = interpret(node.code, curr_func, all_vars)
        # Goto beginning of while-loop
        restart = "\tB " + label + "\n"
        # Create tag for end of while-loop
        end_tag = label + "_end:\n"

        # Combine all created asm code and add it to the file
        additional_asm = comment + start + loader + condition + branch_end + loop_tag + loop_insides + restart + end_tag

        return interpret(nodes, curr_func, all_vars, node_count + 1, asm + additional_asm)

    elif isinstance(node, _nodes.IfNode):
        # ASM will be as follows:
        # if-statement, if True goto true tag
        # Goto false tag
        # True tag
        # Whatever if does
        # Tag for end if

        # Note what happens
        comment = "@If-statement\n"
        
        # Create label
        label = "_" + str(node.id) + "_if"

        # Load variables into R0 and R1, check if it's a raw number
        try:
            loader = "\tMOV R0, #" + str(int(node.lhs)) + "\n"
        except:
            loader = access_local_stack(curr_func, node.lhs, all_vars, "R0", True)
        
        try:
            loader += "\tMOV R1, #" + str(int(node.rhs)) + "\n"
        except:
            loader = access_local_stack(curr_func, node.rhs, all_vars, "R1", True)

        # Write correct comparison
        if node.condition.operator == "wiecej":
            condition = "\tCMP R0, R1\n\tBHI " + label + "_true\n"
        elif node.condition.operator == "mniej":
            condition = "\tCMP R0, R1\n\tBLO " + label + "_true\n"
        elif node.condition.operator == "nie":
            condition = "\tCMP R0, R1\n\tBNE " + label + "_true\n"
        elif node.condition.operator == "jest":
            condition = "\tCMP R0, R1\n\tBEQ " + label + "_true\n"
        else:
            raise Exception("Incompatible operator for if-statement used")
        
        # Branch to end-tag
        branch_end = "\tB " + label + "_end\n"

        # Create tag for true
        true_tag = label + "_true:\n"
        # Do whatever needs to be done within if
        if_insides = interpret(node.code, curr_func, all_vars)
        # Create end-tag
        end_tag = label + "_end:\n"

        # Combine all created asm code and add it to the file
        additional_asm = comment + loader + condition + branch_end + true_tag + if_insides + end_tag

        return interpret(nodes, curr_func, all_vars, node_count + 1, asm + additional_asm)

    elif isinstance(node, _nodes.DefFunc):
        # ASM will be as follows:
        # Skip to function end-tag, so as not to immediately run the function
        # Function name as tag
        # PUSH R0-R6, R8 and LR
        # Function stores given values under tags (tags that need to have been previously created at the start of the code)
        # POP R8
        # Function does whatever function needs to do
        # POP R0-R6 and PC
        # Function end-tag

        # Note what happens
        comment = "@Define function\n"

        # Create label
        label = "_" + node.name
        # Write branch to end of func (so it doesn't execute immediately)
        branch_to_end = "\tB " + label + "_end\n"
        start = label + ":\n"

        # Push LR and R6 onto stack
        push = "\tPUSH {LR}\n"

        # Reserve stack size and update SP
        reserve_stack = "\tSUB SP, SP, #" + str(len(all_vars[node.name]) * 4) + "\n"

        # Store all given variables, in the correct order, under selected variable names
        store_vars = ""
        for param_int in range(0, len(node.params)):
            # Load address of given param into R6
            store_vars += access_local_stack(node.name, node.params[param_int].name, 
                                             all_vars, "R" + str(param_int), False)

        # Do whatever the code needs to do
        func_insides = interpret(node.code, node.name, all_vars)

        # Remove reserved stack space
        unreserve_stack = "\tADD SP, SP, #" + str(len(all_vars[node.name]) * 4) + "\n"

        # Pop PC
        pop = "\tPOP {PC}\n"

        # Create tag for end of function
        end_tag = label + "_end:\n"

        # Combine all created asm code and add it to the file
        additional_asm = comment + branch_to_end + start + push + reserve_stack + store_vars + func_insides + unreserve_stack + pop + end_tag

        return interpret(nodes, curr_func, all_vars, node_count + 1, asm + additional_asm)

    elif isinstance(node, _nodes.Return):
        # ASM will be as follows:
        # Store selected tag in R0
        # POP PC to return from function

        # Note what happens
        comment = "@Return\n"

        additional_asm = access_local_stack(curr_func, node.param_names[0], all_vars, "R0", True)
        additional_asm += "\tADD SP, SP, #" + str(len(all_vars[curr_func]) * 4) + "\n"
        additional_asm += "\tPOP {PC}\n"

        return interpret(nodes, curr_func, all_vars, node_count + 1, asm + comment + additional_asm)

    elif isinstance(node, _nodes.Print):
        # ASM will be as follows:
        # PUSH relevant registers
        # Store to-be-printed variable in R0
        # Branch to print-function (BL)
        # POP relevant registers

        # Note what happens
        comment = "@Print\n"

        return_type = list(filter(lambda x: x.var_type if hasattr(x, "var_type") and x.name == node.param_names[0] else None, nodes))
        return_type = return_type[0].var_type
        if return_type == "STRING":
            additional_asm = access_local_stack(curr_func, node.param_names[0], all_vars, "R0", True)
            additional_asm += "\tBL print_asciz\n"
        elif return_type == "INT":
            additional_asm = access_local_stack(curr_func, node.param_names[0], all_vars, "R0", True)
            additional_asm += "\tBL print_int\n"
        else:
            raise Exception("Unsupported type of variable printed")

        return interpret(nodes, curr_func, all_vars, node_count + 1, asm + comment + additional_asm)

    elif isinstance(node, _nodes.ExeFunc):
        # ASM will be as follows:
        # Store the correct values in R0, R1, etc.
        # Branch to function (BL)

        # Note what happens
        comment = "@Execute Function\n"

        additional_asm = ""
        for param_int in range(0, len(node.param_names)):
            additional_asm += access_local_stack(curr_func, node.param_names[param_int], all_vars, "R" + str(param_int), True)

        additional_asm += "\tBL _" + node.name + "\n"
        if node.storing_var:
            additional_asm += access_local_stack(curr_func, node.storing_var, all_vars, "R0", False)

        return interpret(nodes, curr_func, all_vars, node_count + 1, asm + comment + additional_asm)        

    elif isinstance(node, _nodes.ChangeVar):
        # STRING, FLOAT, MUL or DIV? We don't do those here
        # ASM will be as follows:
        # ?!?!?!?

        if node.value[1] != "bez" and node.value[1] != "i":
            raise Exception("Unsupported operand for changing variables")
        if all_vars[curr_func][node.name][1] != "INT":
            raise Exception("Attempted calculation with non-INT value")

        # Note what happens
        comment = "@Change Variable\n"

        additional_asm = ""
        invert_command = False

        try:
            # See if the selected value is a raw number
            value = int(node.value[0])
            if value >= 0:
                # If positive number; nothing special happens
                additional_asm += "\tMOV R2, #" + str(value) + "\n"
            else:
                # Else, invert the selected operation
                additional_asm += "\tMOV R3, #" + str(value * -1) + "\n"
                invert_command = True
        except:
            # If it isn't a raw number
            additional_asm += access_local_stack(curr_func, node.value[0], all_vars, "R2", True)

        try:
            # See if the selected value is a raw number
            value = int(node.value[2])
            if value >= 0:
                if invert_command:
                    # If first number is negative, switch the places of both numbers when subtracting
                    # -2 + 3 becomes 3 - 2
                    additional_asm += "\tMOV R2, #" + str(value) + "\n"
                else:
                    # If the first number was a regular one
                    additional_asm += "\tMOV R3, #" + str(value) + "\n"
            else:
                # If the second number is a negative one
                if invert_command:
                    # If both are, raise an error
                    raise Exception("Can\'t Subtract/Add 2 negative numbers")
                else:
                    # Otherwise, just change the operation, not the order of numbers
                    # 3 + -2 becomes 3 - 2
                    additional_asm += "\tMOV R3, #" + str(value * -1) + "\n"
                    invert_command = True
        except:
            # If it isn't a raw number
            if invert_command:
                # If the previously given number is a negative one
                additional_asm += access_local_stack(curr_func, node.value[2], all_vars, "R2", True)
            else:
                # If both numbers are positive
                additional_asm += access_local_stack(curr_func, node.value[2], all_vars, "R3", True)

        if node.value[1] == "i" and not invert_command or node.value[1] == "bez" and invert_command:
            # ADD 2 numbers, either when the request is to add 2 positive numbers, or when subtracting
            # a negative number: -- equals +
            additional_asm += "\tADD R1, R2, R3\n"
        elif node.value[1] == "bez" and not invert_command or node.value[1] == "i" and invert_command:
            # SUB 2 numbers, either when the request is to sub 2 positive numbers, or when adding a 
            # negative number: +- equals -
            additional_asm += "\tSUB R1, R2, R3\n"
        
        additional_asm += access_local_stack(curr_func, node.name, all_vars, "R1", False)
        return interpret(nodes, curr_func, all_vars, node_count + 1, asm + comment + additional_asm) 

    elif isinstance(node, _nodes.AssignVar):
        # Assigning negative numbers is not possible
        # ASM will be as follows:
        if node.var_type == "INT":
            additional_asm = "MOV R0, #" + str(node.value) + "\n"
        elif node.var_type == "STRING":
            additional_asm = "STR R0, =" + node.name + "\n"
        else:
            raise Exception("Unsupported variable type for ASM-compiler in:\n" + node.__repr__())

        additional_asm += access_local_stack(curr_func, node.name, all_vars, "R0", False)
        return interpret(nodes, curr_func, all_vars, node_count + 1, asm + additional_asm) 

    else:
        return interpret(nodes, curr_func, all_vars, node_count + 1, asm)


def main():
    #TODO: Fix all comments, add explanations for each function and check old ones
    # NO SUPPORT FOR LISTS, NOR ANY, NOR FLOATS; that leaves strings and ints to be used
    tokens = lex("test_files/test_3.txt")
    AST_segments = Parser(tokens).get_AST().segments

    # Clear file
    f = open("assembly.asm", "w")
    f.close()
    f = open("assembly.asm", "a")

    # Get ASM
    all_vars = get_data_asm(AST_segments, f, "main")
    asm = interpret(AST_segments, "main", all_vars)

    # Add all code
    f.write(".cpu cortex-m3\n.text\n.align 2\n.global main\n\n")
    f.write("main:\n\tBL wait\n\tPUSH {LR}\n\tSUB SP, SP, #" + str(len(all_vars["main"]) * 4) + "\n")
    f.write(asm)
    f.write("\tSUB SP, SP, #" + str(len(all_vars["main"]) * 4) + "\n\tPOP {PC}\n")
    f.close()

main()
