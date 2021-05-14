from my_lexer import lexer, token_types, Token
import re
import sys
import nodes
from typing import List, Tuple, Union


class Parser():
    ''' A parser that turns a list of tokens into an AST
    '''
    def __init__(self, tokens: List[Token]) -> None:
        ''' Inits the class

        tokens: A list of Token-type entries, that represent all information gained from the written code
        '''
        self.tokens = tokens   
    
    # Get all functions that can be ran from outside of a function
    from _parser_OutFunc import get_function_declaration_out_func, get_func_params_out_func, get_var_out_func, fill_list_out_func, get_function_execution_vars_out_func
    # Get all functions that can be ran from inside of a function
    from _parser_InFunc import get_code_segment_in_func, get_paragraph_data_in_func, get_function_execution_vars_in_func, get_condition_in_func, fill_list_in_func

    # The only functions defined in this file, are the ones universally useable, and the main parse-function: get_AST()
    def find_token_type_index(self, token_count: int, token_types: List[str]) -> Tuple[int, str]:
        ''' Function that finds the first token of a certain type, starting from the given index and counting forwards

        token_count: A counter that keeps track of where in the list of tokens we're operating
        token_types: A list of possible token types that need to be found
        return: The index of the first token which is of one of the types contained within token_types, also returns the type of the found token
        '''
        if self.tokens[token_count].type in token_types:
            return token_count, self.tokens[token_count].type
        else:
            return self.find_token_type_index(token_count + 1, token_types)
    
    def find_token_not_type_index(self, token_count: int, token_types: List[str]) -> Tuple[int, str]:
        ''' Function that finds the first token that isn't a certain type, starting from the given index and 
             counting forwards

        token_count: A counter that keeps track of where in the list of tokens we're operating
        token_types: A list of possible token types that need to be skipped
        return: The index of the first token which is of one of the types contained within token_types, also returns the type of the found token
        '''
        if self.tokens[token_count].type not in token_types:
            return token_count, self.tokens[token_count].type
        else:
            return self.find_token_not_type_index(token_count + 1, token_types)
    
    def get_paragraph_end_index(self, token_count: int) -> int:
        ''' Get index of end of paragraph, by way of searching for 2 consecutive NEWLINEs
        This function can be used both in- and outside a function definition.

        token_count: A counter that keeps track of where in the list of tokens we're operating
        return: The index of the end of the current paragraph
        '''
        if self.tokens[token_count].type == "NEWLINE" and self.tokens[token_count + 1].type == "NEWLINE":
            return token_count
        else:
            return self.get_paragraph_end_index(token_count + 1)
 
    def get_commands(self, token_count: int) -> List[nodes.Node]:
        ''' Function creates a list of nodes based on the nodes that are created using self.tokens

        token_count: A counter that keeps track of where in the list of tokens we're operating
        return: A list containing all of the node
        '''
        if token_count >= len(self.tokens):
            # If all tokens have been analysed
            return []

        elif self.tokens[token_count].type == "STAT_START" and self.tokens[token_count + 1].type == "STAT_START":
            # Important statements always start with "siekiera, motyka"
            line_end = self.find_token_type_index(token_count, ["NEWLINE"])[0]
            
            if self.tokens[line_end - 1].type == "DEF_FUNC":
                # If current statement denotes the start of a function definition
                # First get function declaration
                func_name, func_type, func_dec, new_count = self.get_function_declaration_out_func(line_end - 1)

                # Then get func definition
                def_start = self.find_token_not_type_index(self.get_paragraph_end_index(new_count), ["NEWLINE"])[0]
                func_def, new_count = self.get_code_segment_in_func(def_start, "END")

                # Create node for function and save it
                node = nodes.DefFunc(func_name, func_type, func_dec, func_def)
                return [node] + self.get_commands(new_count)

            elif self.tokens[line_end - 1].type in ["INT", "FLOAT", "STRING", "LIST"]:
                # If sentence ends with a type, create a new variable and save it
                node, new_count = self.get_var_out_func(line_end - 1)
                return [node] + self.get_commands(new_count)

            elif self.tokens[line_end - 1].type == "RUN_FUNC":
                # If current statement denotes the start of a function definition
                # Create node for executing a function, and save it
                func_name = self.tokens[line_end - 2].word
                func_params, new_count = self.get_function_execution_vars_out_func(self.find_token_not_type_index(
                                                                          self.get_paragraph_end_index(token_count), 
                                                                          ["NEWLINE"])[0], func_name)
                if func_name == "print":
                    node = nodes.Print(func_params[0])
                else:
                    func_storage = self.tokens[self.find_token_type_index(line_end + 1, ["NEWLINE"])[0] + 3].word
                    node = nodes.ExeFunc(func_name, func_params, func_storage)
                return [node] + self.get_commands(new_count)
            
            else:
                # Nothing interesting happens
                return self.get_commands(token_count + 1)

        else:
            # If currently selected tokens doesn't have any significant meaning
            return self.get_commands(token_count + 1)

    def get_AST(self) -> nodes.AST:
        ''' Function returns an AST created from the output of self.get_commands()

        return: The desired AST
        '''
        return nodes.AST(self.get_commands(0))

    def __repr__(self):
        ''' Function for returning a printable version of the class

        return: A str representation of the class
        '''
        return str(self.tokens)


def main():
    words = re.split("(\n)| |, |#.*", open("test_files/test_2.txt", "r").read())
    sys.setrecursionlimit(len(words) * 2)
    custom_lexer = lexer(token_types, True)
    tokens = custom_lexer(words)
    test = Parser(tokens)
    print(test.get_AST())

# main()
