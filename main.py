from my_parser import Parser
from my_lexer import lex
from my_interpreter import interpret

def main():
    tokens = lex("test_1.txt")
    AST = Parser(tokens).get_AST()
    test_nodes = AST.segments
    interpret(test_nodes, 0, [], [])

    tokens = lex("test_2.txt")
    AST = Parser(tokens).get_AST()
    test_nodes = AST.segments
    interpret(test_nodes, 0, [], [])


main()
