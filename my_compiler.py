import nodes as _nodes
from nodes import get_entry_by_name, unfold_variables
import copy
from my_parser import Parser
from my_lexer import lex
from typing import List, Tuple, Any


def get_data_asm(nodes: List[_nodes.Node], node_count: int=0, asm: str=""):
    if node_count == len(nodes):
        return asm
    
    node = nodes[node_count]
    if isinstance(node, _nodes.AssignVar):
        # ASM will be as follows:
        # In the beginning of the file, create variable with given value
        additional_asm = node.name + ":\n\t"

        if node.var_type == "INT":
            additional_asm += ".int " + str(node.value) + "\n\n"
        elif node.var_type == "FLOAT":
            additional_asm += ".float " + str(node.value) + "\n\n"
        elif node.var_type == "STRING":
            additional_asm += ".asciz " + node.value + "\n\n"
        else:
            raise Exception("Unsupported variable type for ASM-compiler in:\n" + node.__repr__())

        return get_data_asm(nodes, node_count + 1, asm + additional_asm)
    if isinstance(node, _nodes.DefFunc):
        additional_asm = get_data_asm(node.params) + get_data_asm(node.code)
        return get_data_asm(nodes, node_count + 1, asm + additional_asm)
    else:
        return get_data_asm(nodes, node_count + 1, asm)


def load_label_asm(var_name, register, request_var, optional_register=None):
    # Desires only address
    asm = "\tLDR " + register + ", =" + var_name + "\n"
    if optional_register:
        # Desires both variable and address
        asm += "\tLDR" + optional_register + ", [" + register + "]\n"
    elif request_var:
        # Desires only variable
        asm += "\tLDR " + register + ", [" + register + "]\n"
    return asm


def interpret(nodes: List[_nodes.Node], node_count: int=0, asm: str=""):
    ''' Function that interpretes the given code

    nodes: A list of nodes that contain what needs to happen
    node_count: A counter to keep track what nodes have been executed already
    VARS: A list keeping track of all created variables that are currently available
    FUNCS: A list keeping track of all created functions that are currently available
    asm: The generated ASM code
    return: 
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
        designation = "@While-loop\n"

        # Create label
        label = "_" + str(node.id) + "_while"
        start = label + ":\n"

        # Load variables into R0 and R1, check if it's a raw number
        try:
            loader = "\tMOV R0, #" + str(int(node.lhs)) + "\n"
        except:
            loader = load_label_asm(node.lhs, "R0", True)
        
        try:
            loader += "\tMOV R0, #" + str(int(node.rhs)) + "\n"
        except:
            loader += load_label_asm(node.rhs, "R1", True)
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
        branch_end = "\tBL " + label + "_end\n"

        # Create tag for loop
        loop_tag = label + "_loop:\n"
        # Do whatever needs to be done within loop
        loop_insides = interpret(node.code)
        # Goto beginning of while-loop
        restart = "\tBL " + label + "\n"
        # Create tag for end of while-loop
        end_tag = label + "_end:\n"

        # Combine all created asm code and add it to the file
        additional_asm = designation + start + loader + condition + branch_end + loop_tag + loop_insides + restart + end_tag

        return interpret(nodes, node_count + 1, asm + additional_asm)

    elif isinstance(node, _nodes.IfNode):
        # ASM will be as follows:
        # if-statement, if True goto true tag
        # Goto false tag
        # True tag
        # Whatever if does
        # Tag for end if

        # Note what happens
        designation = "@If-statement\n"
        
        # Create label
        label = "_" + str(node.id) + "_if"

        # Load variables into R0 and R1, check if it's a raw number
        try:
            loader = "\tMOV R0, #" + str(int(node.lhs)) + "\n"
        except:
            loader = load_label_asm(node.lhs, "R0", True)
        
        try:
            loader += "\tMOV R1, #" + str(int(node.rhs)) + "\n"
        except:
            loader += load_label_asm(node.rhs, "R1", True)

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
        branch_end = "\tBL " + label + "_end\n"

        # Create tag for true
        true_tag = label + "_true:\n"
        # Do whatever needs to be done within if
        if_insides = interpret(node.code)
        # Create end-tag
        end_tag = label + "_end:\n"

        # Combine all created asm code and add it to the file
        additional_asm = designation + loader + condition + branch_end + true_tag + if_insides + end_tag

        return interpret(nodes, node_count + 1, asm + additional_asm)

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
        designation = "@Define function\n"

        # Create label
        label = "_" + node.name
        # Write branch to end of func (so it doesn't execute immediately)
        branch_to_end = "\tBL " + label + "_end\n"
        start = label + ":\n"

        # Push LR and R6 onto stack
        push = "\tPUSH {LR}\n\tPUSH {R6}\n"

        # Store all given variables, in the correct order, under selected variable names
        store_vars = ""
        for param_int in range(0, len(node.params)):
            # Load address of given param into R6
            store_vars += "\tLDR R6, =" + node.params[param_int].name + "\n"
            # Store given variable under that params' address
            store_vars += "\tSTR R" + str(param_int) + ", [R6]\n"
        
        # Restore R6
        pop_R6 = "\tPOP {R6}\n"

        # Do whatever the code needs to do
        func_insides = interpret(node.code, 0)

        # Pop PC
        pop = "\tPOP {PC}\n"

        # Create tag for end of function
        end_tag = label + "_end:\n"

        # Combine all created asm code and add it to the file
        additional_asm = designation + branch_to_end + start + push + store_vars + pop_R6 + func_insides + pop + end_tag

        return interpret(nodes, node_count + 1, asm + additional_asm)

    elif isinstance(node, _nodes.Return):
        # ASM will be as follows:
        # Store selected tag in R0
        # POP PC to return from function

        # Note what happens
        designation = "@Return\n"

        additional_asm = load_label_asm(node.param_names[0], "R0", True)
        additional_asm += "\tPOP {PC}\n"

        return interpret(nodes, node_count + 1, asm + designation + additional_asm)

    elif isinstance(node, _nodes.Print):
        # ASM will be as follows:
        # PUSH relevant registers
        # Store to-be-printed variable in R0
        # Branch to print-function (BL)
        # POP relevant registers

        # Note what happens
        designation = "@Print\n"

        additional_asm = "\tPUSH {R0-R6}\n"
        additional_asm += load_label_asm(node.param_names[0], "R0", False)
        additional_asm += "\tBL print_asciz\n"
        additional_asm += load_label_asm(node.param_names[0], "R0", False)
        additional_asm += "\tBL print_int\n"
        additional_asm += "\tPOP {R0-R6}\n"


        return interpret(nodes, node_count + 1, asm + designation + additional_asm)

    elif isinstance(node, _nodes.ExeFunc):
        # ASM will be as follows:
        # Store the correct values in R0, R1, etc.
        # Branch to function (BL)

        # Note what happens
        designation = "@Execute Function\n"

        additional_asm = ""
        for param_int in range(0, len(node.param_names)):
            additional_asm += load_label_asm(node.param_names[param_int], "R" + str(param_int), True)

        additional_asm += "\tBL _" + node.name + "\n"
        if node.storing_var:
            additional_asm += load_label_asm(node.storing_var, "R1", False)
            additional_asm += "\tSTR R0, [R1]\n"

        return interpret(nodes, node_count + 1, asm + designation + additional_asm)        

    elif isinstance(node, _nodes.ChangeVar):
        # STRING, MUL or DIV? We don't do that here
        # ASM will be as follows:
        # ?!?!?!?

        # Note what happens
        designation = "@Change Variable\n"

        additional_asm = load_label_asm(node.name, "R0", False)
        invert_command = False

        try:
            value = int(node.value[0])
            if value >= 0:
                # If positive number; nothing special happens
                additional_asm += "\tMOV R2, #" + str(value) + "\n"
            else:
                # Else, invert the selected operation
                additional_asm += "\tMOV R3, #" + str(value * -1) + "\n"
                invert_command = True
        except:
            additional_asm += load_label_asm(node.value[0], "R2", True)

        try:
            value = int(node.value[2])
            if value >= 0:
                if invert_command:
                    # If first number is negative, switch their places when subtracting
                    additional_asm += "\tMOV R2, #" + str(value) + "\n"
                else:
                    additional_asm += "\tMOV R3, #" + str(value) + "\n"
            else:
                # Else, invert the selected operation
                if invert_command:
                    raise Exception("Can\'t Subtract/Add 2 negative numbers")
                else:
                    additional_asm += "\tMOV R3, #" + str(value * -1) + "\n"
                    invert_command = True
        except:
            if invert_command:
                additional_asm += load_label_asm(node.value[2], "R2", True)
            else:
                additional_asm += load_label_asm(node.value[2], "R3", True)

        if node.value[1] == "i" and not invert_command or node.value[1] == "bez" and invert_command:
            additional_asm += "\tADD R1, R2, R3\n"
        elif node.value[1] == "bez" and not invert_command or node.value[1] == "i" and invert_command:
            additional_asm += "\tSUB R1, R2, R3\n"
        
        additional_asm += "\tSTR R1, [R0]\n"
        return interpret(nodes, node_count + 1, asm + designation + additional_asm) 

    else:
        return interpret(nodes, node_count + 1, asm)


def main():
    # NO SUPPORT FOR LISTS, NOR ANY
    # MAX LENGTH OF WORDS IS 4
    tokens = lex("test_files/test_3.txt")
    AST = Parser(tokens).get_AST()
    # print(AST.__repr__())

    # Create Assembly file
    f = open("assembly.asm", "w")
    f.write(".cpu cortex-m0\n")
    data = get_data_asm(AST.segments)
    if data:
        f.write(".data\n\n" + data)
    f.write(".text\n.align 2\n.global main\n\nmain:\n\tPUSH {LR}\n")
    f.close()
    code = interpret(AST.segments)
    f = open("assembly.asm", "a")
    f.write(code)
    f.write("\tPOP {PC}")
    f.close()


main()
