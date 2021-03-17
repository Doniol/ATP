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
    if node_count == 0:
        # Create Assembly file
        f = open("assembly.asm", "w")
        f.write(".cpu cortex-m0\n.text\n.align 1")
        f.close()


    # if node_count == len(nodes):
    
    # node = nodes[node_count]
    # if isinstance(node, _nodes.WhileNode):

    # elif isinstance(node, _nodes.IfNode):

    # elif isinstance(node, _nodes.DefFunc):

    # elif isinstance(node, _nodes.Return):

    # elif isinstance(node, _nodes.Print):
    
    # elif isinstance(node, _nodes.ExeFunc) and node.name == "len":

    # elif isinstance(node, _nodes.ExeFunc):

    # elif isinstance(node, _nodes.AssignVar):

    # elif isinstance(node, _nodes.ChangeVar):


def main():
    tokens = lex("test_files/test_3.txt")
    AST = Parser(tokens).get_AST()
    interpret(AST.segments)


main()
