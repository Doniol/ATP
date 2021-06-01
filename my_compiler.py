import nodes as _nodes
from my_parser import Parser
from my_lexer import lex
from typing import Dict, List, Tuple, Any


def merge_dicts(dict1: Dict[str, Dict[str, Tuple[int, str]]], dict2: Dict[str, Dict[str, Tuple[int, str]]], keys: List[str], 
                newdict: Dict[str, Dict[str, Tuple[int, str]]]={}, count: int=0) -> Dict[str, Dict[str, Tuple[int, str]]]:
    ''' Merges 2 dicts in a functional way

    dict1: The first dict to be merged.
    dict2: The second dict to be merged.
    keys: A list of all of the unique keys within the 2 dicts.
    newdict: The dict that contains all the merges that have already been done.
    count: A counter that keeps track of where in the list of keys the function is.
    return: A dict that contains the combination of the 2 given dicts.
    '''
    if count == len(keys):
        return newdict
    else:
        key = keys[count]
        temp_dict = {key: {**dict1.get(key, {}), **dict2.get(key, {})}}
        return merge_dicts(dict1, dict2, keys, {**temp_dict, **newdict}, count + 1)


def get_all_variables(nodes: List[_nodes.Node], file: str="", curr_name: str="", var_register: Dict[str, Dict[str, Tuple[int, str]]]={}, 
                 node_count: int=0) -> Dict[str, Dict[str, Tuple[int, str]]]:
    ''' Function that creates a dict containing all created variable names

    This function searches out each and every variables that is defined within the source-code. These found variables
     are stored within the Dict under the name of the local scope in which they appear (for example a function name).
    Additionally, the function creates string variables at the start of the .asm file.

    nodes: A list containing all of the nodes that contain the source-code.
    file: A string defining the .asm file in which has to be written.
    curr_name: A string defining the current local scope.
    var_register: A dictionary that contains all of the found variables.
    node_count: A counter that keeps track of where in the list of nodes the function is.
    return: The var_register.
    '''
    if node_count == len(nodes):
        # If all nodes from the current list have been analysed
        return var_register
    
    node = nodes[node_count]
    if isinstance(node, _nodes.DefFunc):
        # If the current node defines the creation of a new function
        in_function_vars = get_all_variables(node.code, file, node.name, var_register)
        # Combine old and additional var_register
        all_keys = list(set(list(var_register.keys()) + list(in_function_vars.keys())))
        new_vars = merge_dicts(var_register, in_function_vars, all_keys)

        function_params = get_all_variables(node.params, file, node.name, new_vars)
        # Combine old and additional var_register
        all_keys = list(set(list(new_vars.keys()) + list(function_params.keys())))
        newer_vars = merge_dicts(new_vars, function_params, all_keys)

        return get_all_variables(nodes, file, curr_name, newer_vars, node_count + 1)

    elif isinstance(node, _nodes.AssignVar):
        # If the current node defines a new variable
        if node.var_type == "STRING":
            f = open(file, "a")
            f.write(node.name + ":\n\t.asciz \"" + node.value + "\"\n\n")

        additional_counts = {curr_name: {node.name: [len(var_register.get(curr_name, [])) * 4, node.var_type]}}
        # Combine old and additional var_register
        all_keys = list(set(list(var_register.keys()) + list(additional_counts.keys())))
        new_vars = merge_dicts(var_register, additional_counts, all_keys)

        return get_all_variables(nodes, file, curr_name, new_vars, node_count + 1)

    elif isinstance(node, _nodes.WhileNode) or isinstance(node, _nodes.IfNode):
        # If the current node defines a set of code within a if-statement or while-loop
        additional_counts = get_all_variables(node.code, file, curr_name, var_register)

        # Combine old and additional var_register
        all_keys = list(set(list(var_register.keys()) + list(additional_counts.keys())))
        new_vars = merge_dicts(var_register, additional_counts, all_keys)
        
        return get_all_variables(nodes, file, curr_name, new_vars, node_count + 1)

    else:
        return get_all_variables(nodes, file, curr_name, var_register, node_count + 1)


def access_local_stack(curr_scope: str, var_name: str, all_vars: Dict[str, Dict[str, Tuple[int, str]]], register: str, load: bool) -> str:
    ''' This function returns a string containing a command to load or store the desired value

    curr_scope: The name of the current local scope in which the variable is desired.
    var_name: The name of the desired variable.
    all_vars: A dict containing all of the variables within the code. (The return value of get_all_variables())
    register: The register where a variable is stored in, or from which to store in the stack.
    load: A bool with which a choice between loading into or storing from the selected register can be made.
    return: A string containing the generated line of code.
    '''
    if load:
        # Load from stack into register
        return "\tLDR " + register + ", [SP, #" + str(all_vars[curr_scope][var_name][0]) + "]\n"
    else:
        # Store from stack into register
        return "\tSTR " + register + ", [SP, #" + str(all_vars[curr_scope][var_name][0]) + "]\n"


def compile_to_ASM(file: str, AST_segments: List[_nodes.Node]) -> None:
    ''' A function that writes the complete desired .asm file

    file: The name of the file that is to be written
    AST_segments: A list containing all of the nodes, and thus the code, of the source-file
    '''
    # Clear file
    f = open(file, "w")
    f.close()

    # Get ASM (and write string variables into file)
    all_vars = get_all_variables(AST_segments, file, "main")
    asm = compile(AST_segments, "main", all_vars)

    # Write the rest of the code
    f = open(file, "a")
    f.write(".cpu cortex-m3\n.text\n.align 2\n.global main\n\n")
    f.write("main:\n\tBL wait\n\tPUSH {LR}\n\tSUB SP, SP, #" + str(len(all_vars["main"]) * 4) + "\n")
    f.write(asm)
    f.write("\tSUB SP, SP, #" + str(len(all_vars["main"]) * 4) + "\n\tPOP {PC}\n")
    f.close()


def compile(nodes: List[_nodes.Node], curr_scope: str, all_vars: Dict[str, List[str]], node_count: int=0, asm: str="") -> str:
    ''' Function that writes .asm code for the given list of nodes

    nodes: A list containing  all of the nodes, and thus code, that needs to be turned to .asm.
    curr_scope: A string showing the current scope in which code is being translated to .asm.
    all_vars: A dict containing all of the variables within the code. (The return value of get_all_variables())
    node_count: A counter that keeps track of where in the list of nodes the function is.
    asm: The up to now written .asm code.
    return: All of the written .asm code.
    '''
    if node_count == len(nodes):
        # If all nodes have been translated
        return asm
    
    node = nodes[node_count]
    if isinstance(node, _nodes.WhileNode):
        # ASM will be as follows:
        # Tag for while-loop start
        # Load requested variables into R0 and R1
        # if-statement, if True goto actual loop tag
        # Branch to loop end-tag
        # Loop tag
        # Whatever loop does
        # Goto while-loop start
        # Tag for loop end

        # Note what happens
        comment = "@While-loop\n"

        # Create label
        label = "_" + str(node.id) + "_while"
        start = label + ":\n"

        # Load variables into R0 and R1, check if it's a raw number
        try:
            loader = "\tMOV R0, #" + str(int(node.lhs)) + "\n"
        except:
            loader = access_local_stack(curr_scope, node.lhs, all_vars, "R0", True)
        
        try:
            loader += "\tMOV R1, #" + str(int(node.rhs)) + "\n"
        except:
            loader = access_local_stack(curr_scope, node.rhs, all_vars, "R1", True)

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
        loop_insides = compile(node.code, curr_scope, all_vars)
        # Goto beginning of while-loop
        restart = "\tB " + label + "\n"
        # Create tag for end of while-loop
        end_tag = label + "_end:\n"

        # Combine all created asm code and add it to the file
        additional_asm = comment + start + loader + condition + branch_end + loop_tag + loop_insides + restart + end_tag

        return compile(nodes, curr_scope, all_vars, node_count + 1, asm + additional_asm)

    elif isinstance(node, _nodes.IfNode):
        # ASM will be as follows:
        # Store requested variables into R0 and R1
        # if-statement, if True goto true tag
        # Goto end tag
        # True tag
        # Whatever if does
        # End tag

        # Note what happens
        comment = "@If-statement\n"
        
        # Create label
        label = "_" + str(node.id) + "_if"

        # Load variables into R0 and R1, check if it's a raw number
        try:
            loader = "\tMOV R0, #" + str(int(node.lhs)) + "\n"
        except:
            loader = access_local_stack(curr_scope, node.lhs, all_vars, "R0", True)
        
        try:
            loader += "\tMOV R1, #" + str(int(node.rhs)) + "\n"
        except:
            loader = access_local_stack(curr_scope, node.rhs, all_vars, "R1", True)

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
        if_insides = compile(node.code, curr_scope, all_vars)
        # Create end-tag
        end_tag = label + "_end:\n"

        # Combine all created asm code and add it to the file
        additional_asm = comment + loader + condition + branch_end + true_tag + if_insides + end_tag

        return compile(nodes, curr_scope, all_vars, node_count + 1, asm + additional_asm)

    elif isinstance(node, _nodes.DefFunc):
        # ASM will be as follows:
        # Branch to function end tag
        # Push LR
        # Reserve the required amount of space on the stack
        # Store given variables in the stack
        # Do whatever func needs to do
        # Unreserve space on the stack
        # POP PC
        # Function end tag

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
        store_vars = "".join(list(map(lambda param: access_local_stack(node.name, param.name, all_vars, "R" + str(node.params.index(param)), False), 
                              node.params)))

        # Do whatever the code needs to do
        func_insides = compile(node.code, node.name, all_vars)

        # Remove reserved stack space
        unreserve_stack = "\tADD SP, SP, #" + str(len(all_vars[node.name]) * 4) + "\n"

        # Pop PC
        pop = "\tPOP {PC}\n"

        # Create tag for end of function
        end_tag = label + "_end:\n"

        # Combine all created asm code and add it to the file
        additional_asm = comment + branch_to_end + start + push + reserve_stack + store_vars + func_insides + unreserve_stack + pop + end_tag

        return compile(nodes, curr_scope, all_vars, node_count + 1, asm + additional_asm)

    elif isinstance(node, _nodes.Return):
        # ASM will be as follows:
        # Store selected variable from the stack into R0
        # POP PC to return from function

        # Note what happens
        comment = "@Return\n"

        additional_asm = access_local_stack(curr_scope, node.param_names[0], all_vars, "R0", True)
        additional_asm += "\tADD SP, SP, #" + str(len(all_vars[curr_scope]) * 4) + "\n"
        additional_asm += "\tPOP {PC}\n"

        return compile(nodes, curr_scope, all_vars, node_count + 1, asm + comment + additional_asm)

    elif isinstance(node, _nodes.Print):
        # ASM will be as follows:
        # Load desired variable from stack into R0
        # BL to correct print (either for integers or for strings)

        # Note what happens
        comment = "@Print\n"

        return_type = all_vars[curr_scope][node.param_names[0]][1]
        if return_type == "STRING":
            additional_asm = access_local_stack(curr_scope, node.param_names[0], all_vars, "R0", True)
            additional_asm += "\tBL print_asciz\n"
        elif return_type == "INT":
            additional_asm = access_local_stack(curr_scope, node.param_names[0], all_vars, "R0", True)
            additional_asm += "\tBL print_int\n"
        else:
            raise Exception("Unsupported type of variable printed")

        return compile(nodes, curr_scope, all_vars, node_count + 1, asm + comment + additional_asm)

    elif isinstance(node, _nodes.ExeFunc):
        # ASM will be as follows:
        # Load every selected parameter from the stack into the registers
        # Branch to function
        # (Optional) Store result in stack

        # Note what happens
        comment = "@Execute Function\n"

        # Load parameter values from stack into registers
        additional_asm = "".join(list(map(lambda param_name: access_local_stack(curr_scope, param_name, all_vars, "R" + str(node.param_names.index(param_name)), 
                                          True), node.param_names)))

        # Branch to function
        additional_asm += "\tBL _" + node.name + "\n"

        # If selected; store result in stack
        if node.storing_var:
            additional_asm += access_local_stack(curr_scope, node.storing_var, all_vars, "R0", False)

        return compile(nodes, curr_scope, all_vars, node_count + 1, asm + comment + additional_asm)        

    elif isinstance(node, _nodes.ChangeVar):
        # ASM will be as follows:
        # Load requested variables into R2 and R3
        # Perform desired calculation and store result in R1
        # Load R1 onto stack

        # If calculation is something other that SUB or ADD, throw an error
        if node.value[1] != "bez" and node.value[1] != "i":
            raise Exception("Unsupported operand for changing variables")
        # If values for calculation are other than integer, throw an error
        if all_vars[curr_scope][node.name][1] != "INT":
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
            additional_asm += access_local_stack(curr_scope, node.value[0], all_vars, "R2", True)

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
                additional_asm += access_local_stack(curr_scope, node.value[2], all_vars, "R2", True)
            else:
                # If both numbers are positive
                additional_asm += access_local_stack(curr_scope, node.value[2], all_vars, "R3", True)

        if node.value[1] == "i" and not invert_command or node.value[1] == "bez" and invert_command:
            # ADD 2 numbers, either when the request is to add 2 positive numbers, or when subtracting
            # a negative number: -- equals +
            additional_asm += "\tADD R1, R2, R3\n"
        elif node.value[1] == "bez" and not invert_command or node.value[1] == "i" and invert_command:
            # SUB 2 numbers, either when the request is to sub 2 positive numbers, or when adding a 
            # negative number: +- equals -
            additional_asm += "\tSUB R1, R2, R3\n"
        
        additional_asm += access_local_stack(curr_scope, node.name, all_vars, "R1", False)
        return compile(nodes, curr_scope, all_vars, node_count + 1, asm + comment + additional_asm) 

    elif isinstance(node, _nodes.AssignVar):
        # Assigning negative numbers is not possible
        # ASM will be as follows:
        # Load/Move the desired value into R0
        # Store R0 in the stack, under the address of the to be changed variable

        # Store the desired value in R0
        if node.var_type == "INT":
            additional_asm = "\tMOV R0, #" + str(node.value) + "\n"
        elif node.var_type == "STRING":
            additional_asm = "\tLDR R0, =" + node.name + "\n"
        else:
            raise Exception("Unsupported variable type for ASM-compiler in:\n" + node.__repr__())

        # Store R0 into the right place on the stack
        additional_asm += access_local_stack(curr_scope, node.name, all_vars, "R0", False)
        return compile(nodes, curr_scope, all_vars, node_count + 1, asm + additional_asm) 

    else:
        # If nothing of note happens
        return compile(nodes, curr_scope, all_vars, node_count + 1, asm)


def main():
    tokens = lex("test_files/test_4.txt")
    AST_segments = Parser(tokens).get_AST().segments
    compile_to_ASM("main.asm", AST_segments)


main()
