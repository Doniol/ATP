import nodes as _nodes
from nodes import get_entry_by_name, unfold_variables
import copy
from my_parser import Parser
from my_lexer import lex
from typing import List, Tuple, Any


def interpret(nodes: List[_nodes.Node], node_count: int=0, VARS: List[Tuple[str, str, Any]]=[], 
              FUNCS: List[Tuple[str, _nodes.DefFunc]]=[], asm: str) -> Tuple[List[Tuple[str, str, Any]], List[Tuple[str, _nodes.DefFunc]]]:
    ''' Function that interpretes the given code

    nodes: A list of nodes that contain what needs to happen
    node_count: A counter to keep track what nodes have been executed already
    VARS: A list keeping track of all created variables that are currently available
    FUNCS: A list keeping track of all created functions that are currently available
    asm: The generated ASM code
    return: 
    '''
    if node_count == 0:
        # Create Assembly file
        f = open("assembly.asm", "w")
        f.write(".cpu cortex-m0\n.text\n.align 2\n\n.global main")
        f.close()


    if node_count == len(nodes):
        return asm
    
    node = nodes[node_count]
    if isinstance(node, _nodes.WhileNode):
        label = "_" + str(node.id) + "_while"
        start = label + ":\n"
        loader = "\tLDR R0, =" + node.lhs + "_var\n"
        loader += "\tLDR R1, =" + node.rhs + "_var\n"

        if node.condition.operator == "wiecej":
            condition = "\tCMP R0, R1\n\tBHI " + label + "_end\n"
        elif node.condition.operator == "mniej":
            condition = "\tCMP R0, R1\n\tBLO " + label + "_end\n"
        elif node.condition.operator == "nie":
            condition = "\tCMP R0, R1\n\tBNE " + label + "_end\n"
        elif node.condition.operator == "jest":
            condition = "\tCMP R0, R1\n\tBEQ " + label + "_end\n"
        else:
            raise Exception("Incompatible operator for while-loop used")

        pre_code = start + loader + condition

        code = interpret(node.code, 0, other_count + 1, VARS, FUNCS)

        post_code = 
        

    # elif isinstance(node, _nodes.IfNode):

    # elif isinstance(node, _nodes.DefFunc):

    # elif isinstance(node, _nodes.Return):

    elif isinstance(node, _nodes.Print):
        new_asm = "PUSH {R4, LR}\nMOV R4, R0\nLDR R0, =" + node.param_names[0]
        new_asm += "\nBL print_asciz\nPOP {R4, PC}\n"
        return asm + new_asm
    
    # elif isinstance(node, _nodes.ExeFunc) and node.name == "len":

    # elif isinstance(node, _nodes.ExeFunc):

    # elif isinstance(node, _nodes.AssignVar):

    # elif isinstance(node, _nodes.ChangeVar):


def main():
    tokens = lex("test_files/test_3.txt")
    AST = Parser(tokens).get_AST()
    interpret(AST.segments)


main()
