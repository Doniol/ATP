from my_parser import Parser
from my_lexer import lex
from my_interpreter import interpret

def main():
    # Capabilities:
        # Always:
            # - Create var; list and single
            # - Run functions
            # - Print shit
            # - Select item from list by index, only useable with assigning new vars
        # Inside function:
            # - Change existing var
            # - Run functions
            # - While-loops
            # - If-statements
            # - Return something
            # - Len of list
        # Outside function:
            # - Create functions

    # Var or func names with whitespaces arent allowed, nor is anything really, fuck whitepaces
    # File needs to end with NEWLINE
    tokens = lex("test_1.txt")
    AST = Parser(tokens).get_AST()
    test_nodes = AST.segments
    interpret(test_nodes, 0, [], [])

    tokens = lex("test_2.txt")
    AST = Parser(tokens).get_AST()
    test_nodes = AST.segments
    interpret(test_nodes, 0, [], [])


main()
