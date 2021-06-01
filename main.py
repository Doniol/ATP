from my_parser import Parser
from my_lexer import lex
from my_interpreter import interpret
from my_compiler import compile_to_ASM

def main():
    # Capabilities:
        # Always:
            # - Create var; list and single
            # - Run functions
            # - Print shit, works only when printing previously created variables, no raw data
            # - Select item from list by index, only useable with assigning new vars
            # - Len of list
        # Inside function:
            # - Change existing var
            # - Run functions
            # - While-loops
            # - If-statements
            # - Return something
        # Outside function:
            # - Create functions
    #.ASM compiler changes:
        # Lists, floats and any's are not supported
        # MUL and DIV are not supported, only ADD and SUB are
        # No calculations using strings are possible, only calculations using integers are allowed
        # Assigning negative values to variable names is impossible, as is using them in comparisons, they can be used in calculations though
    # Var or func names with whitespaces arent allowed, nor is anything really, fuck whitepaces
    # File needs to end with NEWLINE
    
    test_nr = input("Select a test file (1-4): ")
    tokens = lex("test_files/test_" + test_nr + ".txt")
    AST = Parser(tokens).get_AST()
    AST_segments = AST.segments

    what_do = input("Select whether to interpret or compile the code (I/C): ")
    if what_do == "C":
        # Compile selected code to a .asm file. Only works for test 3 and 4.
        compile_to_ASM("main.asm", AST_segments)
    elif what_do == "I":
        # Immediatly interpret and execute selected code. Works for all tests.
        interpret(AST_segments, 0, [], [])
    else:
        print("No valid selection, choose between C for compiler and I for interpreter")


main()
