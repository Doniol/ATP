from lexer import lexer, token_types
import re
import sys
import nodes


class Parser():
    def __init__(self, tokens):
        self.tokens = tokens

    def find_token_type_index(self, token_count, token_types):
        ''' Function that finds the first token of a certain type, starting from the given index and counting forwards

        token_count: A counter that keeps track of where in the list of tokens we're operating
        token_types: A list of possible token types that need to be found
        return: The index of the first token which is of one of the types contained within token_types, also returns the type of the found token
        '''
        if self.tokens[token_count][1] in token_types:
            return token_count, self.tokens[token_count][1]
        else:
            return self.find_token_type_index(token_count + 1, token_types)
    
    def find_token_not_type_index(self, token_count, token_types):
        ''' Function that finds the first token that isn't a certain type, starting from the given index and 
             counting forwards

        token_count: A counter that keeps track of where in the list of tokens we're operating
        token_types: A list of possible token types that need to be skipped
        return: The index of the first token which is of one of the types contained within token_types, also returns the type of the found token
        '''
        if self.tokens[token_count][1] not in token_types:
            return token_count, self.tokens[token_count][1]
        else:
            return self.find_token_not_type_index(token_count + 1, token_types)
    
    def find_token_type_index_backwards(self, token_count, token_types):
        ''' Function that finds the first token of a certain type, starting from the given index and counting backwards

        token_count: A counter that keeps track of where in the list of tokens we're operating
        token_types: A list of possible token types that need to be found
        return: The index of the first token which is of one of the types contained within token_types, also returns the type of the found token
        '''
        if self.tokens[token_count][1] in token_types:
            return token_count, self.tokens[token_count][1]
        else:
            return self.find_token_type_index_backwards(token_count - 1, token_types)
    
    def get_func_params_out_func(self, token_count, result, par_num):
        ''' Function that returns a list of all parameters found in a new function declaration
        Function only for use outside of function definitions; can be used within function declaration though

        token_count: A counter that keeps track of where in the list of tokens we're operating
        result: A list keeping track of all found parameters
        par_num: Amount of parameters to be found
        return: A list containing all found parameters, and a integer representing where in the list of tokens the current section of code ends
        '''
        if self.tokens[token_count][1] == "STAT_START" and self.tokens[token_count + 1][1] == "STAT_START":
            # All important statements start with "siekiera, motyka"
            if par_num == -1:
                # If par_num hasn't been read yet
                par_count = int(self.tokens[token_count + 2][0])
                return self.get_func_params_out_func(self.get_paragraph_end_index(token_count), result, par_count)
            elif len(result) == par_num:
                # If refrain is still going, but all params have already been found
                return result, token_count
            elif par_num == 0:
                # If there are no parameters to be found
                return result + [None], token_count
            else:
                # If refrain is still going, but not all params have already been given
                param, new_count = self.get_var_out_func(self.find_token_type_index(token_count, ["NEWLINE"])[0] - 1)
                return self.get_func_params_out_func(new_count, result + [param], par_num)

        else:
            # If not in important statement
            if len(result) != par_num:
                # If not in a relevant part of the refrain
                return self.get_func_params_out_func(token_count + 1, result, par_num)
            else:
                # If all vars have already been given
                return result, token_count

    def fill_list_out_func(self, token_count, list_name, results):
        ''' Function that fills a found list with the corresponding entries
        Function only for use outside of function definitions

        token_count: A counter that keeps track of where in the list of tokens we're operating
        list_name: The name of the currently selected list
        results: A list keeping track of all of the variables stored in the selected list
        return: A list filled with all of the variables stored in the selected list, and a integer representing where in the 
         list of tokens the current section of code ends
        '''
        if self.tokens[token_count][1] == "STAT_START" and self.tokens[token_count + 1][1] == "STAT_START":
            # All relevant statements start with "siekiera, motyka"
            line_end = self.find_token_type_index(token_count + 2, ["NEWLINE"])[0]
            if self.tokens[token_count + 2][1] != "NOTHING":
                # If current line is indeed adding another entry to the list
                if self.tokens[token_count + 2][0] == list_name:
                    # Check if we're still in the correct list
                    return self.fill_list_out_func(self.find_token_type_index(line_end + 1, ["NEWLINE"])[0] + 1,
                                          list_name, results + [self.tokens[line_end + 1][0]])
                else:
                    # Error
                    return None, None
            else:
                # If current line signifies end of new entries to current list
                return results, self.find_token_type_index(line_end + 1, ["NEWLINE"])[0] + 1
        else:
            # If current token is not the start of a new statement
            return self.fill_list_out_func(token_count + 1, list_name, results)

    def get_function_declaration_out_func(self, token_count):
        ''' Function that gets all data that is relevant to new function declaration
        Function only for use outside of function definitions

        token_count: A counter that keeps track of where in the list of tokens we're operating
        return: A tuple containing all information about the function (except the actual code within), and a integer representing 
         where in the list of tokens the current section of code ends
        '''
        # Get all necessary function details
        func_name = self.tokens[token_count - 1][0]
        func_type = self.tokens[token_count + 2][1]
        func_dec, new_count = self.get_func_params_out_func(self.find_token_type_index(token_count + 2, ["STAT_START"])[0], [], -1)
        return func_name, func_type, func_dec, new_count

    def fill_list_in_func(self, token_count, result):
        ''' Function that returns all data stored in a newly declared list
        Function only for use inside of function definitions

        token_count: A counter that keeps track of where in the list of tokens we're operating
        result: A list keeping track of all of the variables stored in the selected list
        return: A list filled with all of the variables stored in the selected list, and a integer representing where in the 
         list of tokens the current section of code ends
        '''
        if self.tokens[token_count][1] != "NOTHING":
            # Select first text token
            line_end = self.find_token_type_index(token_count, ["NEWLINE"])[0]
            next_line_end = self.find_token_type_index(line_end + 1, ["NEWLINE"])[0]
            first_non_newline = self.find_token_not_type_index(next_line_end + 1, ["NEWLINE"])[0]
            # Run this function again but for next paragraph/part of lyrics
            return self.fill_list_in_func(first_non_newline, result + [self.tokens[token_count][0]])
        else:
            # All data to be stored in the list has been found, return this data together with the index of the end of 
            #   the current paragraph
            return result, self.get_paragraph_end_index(token_count)

    def get_function_execution_vars_in_func(self, token_count, result, func_name):
        ''' Function that returns all variables that are passed to a to be run function
        Function only for use inside of function definitions

        token_count: A counter that keeps track of where in the list of tokens we're operating
        result: A list keeping track of all the variables that are to be passed to a function
        func_name: The name of the to be ran function
        return: A list containing all the variables that are to be passed to a function, and a integer representing where in the 
         list of tokens the current section of code ends
        '''
        if self.tokens[token_count][0] == func_name and self.tokens[token_count + 1][1] == "NEWLINE":
            # Get the next variable for the function
            var_index = self.find_token_type_index(token_count + 2, ["NEWLINE"])[0] + 1
            var_name = self.tokens[var_index][0]
            # Call this function anew, but for the next paragraph
            return self.get_function_execution_vars_in_func(self.get_paragraph_end_index(token_count), result + [var_name], func_name)
        elif self.tokens[token_count][1] == "NOTHING":
            # All given vars have been found, return them together with a index for the end of the current paragraph
            return result, self.get_paragraph_end_index(token_count)
        else:
            # Nothing of interest happens
            return self.get_function_execution_vars_in_func(token_count + 1, result, func_name)

    def get_paragraph_end_index(self, token_count):
        ''' Get index of end of paragraph, by way of searching for 2 consecutive NEWLINEs
        This function can be used both in- and outside a function definition.

        token_count: A counter that keeps track of where in the list of tokens we're operating
        return: The index of the end of the current paragraph
        '''
        if self.tokens[token_count][1] == "NEWLINE" and self.tokens[token_count + 1][1] == "NEWLINE":
            return token_count
        else:
            return self.get_paragraph_end_index(token_count + 1)

    def get_change_in_func(self, token_count, result):
        ''' Function for recording what is going to happen to the selected variable
        Function only for use inside of function definitions

        token_count: A counter that keeps track of where in the list of tokens we're operating
        result: A list that keeps of track of how the selected variable is to be changed
        return: A list containing how the selected variable is to be changed
        '''
        if len(result) == 0:
            # If no change has been recorded yet
            return self.get_change_in_func(token_count + 1, result + [self.tokens[token_count][0]])
        else:
            if self.tokens[token_count][0] == "i": # 'i' means '+'
                # If more changes need to be recorded
                return self.get_change_in_func(token_count + 2, result + [self.tokens[token_count][0], self.tokens[token_count + 1][0]])
            else:
                # If everything has already been recorded
                return result

    def get_statement_in_func(self, token_count, result):
        ''' Function that returns the statement following a if/else declaration
        Function only for use inside of function definitions

        token_count: A counter that keeps track of where in the list of tokens we're operating
        result: A list keeping track of the created statement
        return: A list containing the created statement
        '''
        if len(result) == 0:
            return self.get_statement_in_func(token_count + 1, result + [self.tokens[token_count][0]])
        else:
            if self.tokens[token_count][0] in ["wiecej", "mniej"]: # > or <, and must be follow with a non-relevant word
                return self.get_statement_in_func(token_count + 3, result + [self.tokens[token_count][0], self.tokens[token_count + 2][0]])
            elif self.tokens[token_count][0] in ["jest", "nie"]: # == or !=
                return self.get_statement_in_func(token_count + 2, result + [self.tokens[token_count][0], self.tokens[token_count + 1][0]])
            else:
                return result

    def get_func_paragraph_data_in_func(self, token_count):
        ''' Return what happens in current paragraph
        Function only for use inside of function definitions

        token_count: A counter that keeps track of where in the list of tokens we're operating
        return: A tuple that always contains the type of the paragraph and the index of the paragraphs' end, sometimes also
         contains newly created nodes
        '''
        if self.tokens[token_count][1] == "RUN_FUNC":
            # Call on another function within the currently selected one
            # Find end of next line
            new_line = self.find_token_type_index(token_count + 2, ["NEWLINE"])[0]
            # Find end of following line and use it to get save var name
            next_line = self.find_token_type_index(new_line + 1, ["NEWLINE"])[0]

            # Get necessary values
            func_name = self.tokens[token_count - 1][0]
            func_save = self.tokens[next_line - 1][0]
            func_vars, new_count = self.get_function_execution_vars_in_func(self.find_token_type_index(next_line + 1, ["NEWLINE"])[0] + 1, [], func_name)
            # Create new node
            node = nodes.ExeFunc(func_name, func_vars, func_save)
            return "RUN_FUNC", node, new_count

        elif self.tokens[token_count][1] == "RETURN":
            # If the function wants to return something
            # Get necessary values
            var_name = self.tokens[self.find_token_type_index(token_count, ["NEWLINE"])[0] + 1][0]
            # Create new node
            node = nodes.Return(var_name)
            return "RETURN", node, self.get_paragraph_end_index(token_count)

        elif self.tokens[token_count][1] == "END_FUNC":
            # If the function has ended
            return "END", self.get_paragraph_end_index(token_count)

        elif self.tokens[token_count][1] == "NOTHING":
            # Nothing happens this paragraph
            return None, self.get_paragraph_end_index(token_count)

        elif self.tokens[token_count][1] in ["INT", "FLOAT", "STRING"]:
            # Create new non-list variable
            newline = self.find_token_type_index(token_count, ["NEWLINE"])[0]
            # Get necessary values
            var_name = self.tokens[token_count + 1][0]
            var_type = self.tokens[token_count][1]
            var_val = self.tokens[newline + 1][0]
            # Create new node
            node = nodes.AssignVar(var_name, var_type, var_val)
            return "NEWVAR", node, self.get_paragraph_end_index(token_count)

        elif self.tokens[token_count][1] == "LIST":
            # Create new list variable
            newline = self.find_token_type_index(token_count, ["NEWLINE"])[0]
            # Get necessary values
            var_name = self.tokens[token_count + 2][0]
            list_type = ["LIST", self.tokens[token_count + 1][1]]
            vals, new_count = self.fill_list_in_func(newline + 1, [])
            # Create new node
            node = nodes.AssignList(var_name, list_type, vals)
            return "NEWVAR", node, new_count

        elif self.tokens[token_count][1] == "CHANGE":
            # An existing variable is being changed
            # Get necessary values
            var_name = self.tokens[self.find_token_type_index(self.find_token_type_index(token_count, 
                                ["NEWLINE"])[0] + 1, ["NEWLINE"])[0] - 1][0]
            line_end = self.find_token_type_index(token_count, ["NEWLINE"])[0]
            val = self.get_change_in_func(self.find_token_type_index(line_end + 1, ["NEWLINE"])[0] + 1, [])
            # Create new node
            node = nodes.ChangeVar(var_name, val)
            return "VAR_CHANGE", node, self.get_paragraph_end_index(token_count)

        elif self.tokens[token_count][1] == "WHILE":
            # Refrain is while loop
            if self.tokens[token_count + 1][1] == "END":
                # Refrain denotes end of while-loop
                return "WHILE_END", self.get_paragraph_end_index(token_count)  
            else:
                # While loop is starting
                # Get necessary values
                statement_start = self.find_token_type_index(token_count, ["NEWLINE"])[0] + 1
                statement = self.get_statement_in_func(statement_start, [])
                # Dont create new node yet, do so only when all underlying code has been found
                return "WHILE_START", statement, self.get_paragraph_end_index(statement_start)

        elif self.tokens[token_count][1] == "IF":
            # Refrain is if-statement
            if self.tokens[token_count + 1][1] == "END":
                # Refrain denotes end of if-statement
                return "IF_END", self.get_paragraph_end_index(token_count) 
            else:
                # If statement is starting
                # Get necessary values
                statement_start = self.find_token_type_index(token_count, ["NEWLINE"])[0] + 1
                statement = self.get_statement_in_func(statement_start, [])
                # Dont create new node yet, do so only when all underlying code has been found
                return "IF_START", statement, self.get_paragraph_end_index(statement_start)

        else:
            # Nothing interesting found
            return self.get_func_paragraph_data_in_func(token_count + 1)

    def get_code_segment_in_func(self, token_count, ending, result):
        ''' Function returns all of the different commands within a function
        Function only for use inside of function definitions

        token_count: A counter that keeps track of where in the list of tokens we're operating
        ending: A token_type upon which the current segment of code (eg. while-loop, func definition or if-statement) ends
        result: A list keeping track of all newly created nodes within this code segment
        return: A list containing all newly created nodes within this code segment, and a integer representing where in the 
         list of tokens the current section of code ends
        '''
        # Get data about paragraph
        paragraph = self.get_func_paragraph_data_in_func(token_count)
        paragraph_type = paragraph[0]
        if paragraph_type == ending:
            # If paragraph denotes the end to a segment of the code; e.g. if/while/func def
            return result, paragraph[-1]
        elif paragraph_type == "WHILE_START":
            # If paragraph denotes the start to a while-loop
            statement = paragraph[1]
            code, new_count = self.get_code_segment_in_func(paragraph[-1], "WHILE_END", [])
            # Create while node
            node = nodes.WhileNode(statement, code)
            return self.get_code_segment_in_func(new_count, ending, result + [node])
        elif paragraph_type == "IF_START":
            # If paragraph denotes the start to a if-thingy
            statement = paragraph[1]
            code, new_count = self.get_code_segment_in_func(paragraph[-1], "IF_END", [])
            # Create if node
            node = nodes.IfNode(statement, code)
            return self.get_code_segment_in_func(new_count, ending, result + [node])
        else:
            # If nothing special happens
            return self.get_code_segment_in_func(paragraph[-1], ending, result + [paragraph[1]])

    def get_var_out_func(self, token_count):
        ''' Function for getting al details about a var that is assigned outside of a function
        Function only for use outside of function definitions

        token_count: A counter that keeps track of where in the list of tokens we're operating
        return: A newly created node containing the new variable, and a integer representing where in the 
         list of tokens the current section of code ends
        '''
        var_type = self.tokens[token_count][1]
        var_name = self.tokens[token_count - 1][0]
        if var_type in ["INT", "FLOAT", "STRING"]:
            # If variable isn't list
            val = self.tokens[token_count + 2][0]
            node = nodes.AssignVar(var_name, var_type, val)
            return node, self.find_token_type_index(token_count + 2, ["NEWLINE"])[0]
        elif var_type == "LIST":
            # If variable is list
            list_type = self.tokens[token_count + 2][0]
            vals, new_count = self.fill_list_out_func(self.find_token_type_index(token_count + 2, 
                                                              ["NEWLINE"])[0] + 1, var_name, [])
            node = nodes.AssignList(var_name, [var_type, list_type], vals)
            return node, new_count

    def get_function_execution_vars_out_func(self, token_count, name, result):
        ''' Function for finding what variables to give to a function when running it
        Function only for use outside of function definitions

        token_count: A counter that keeps track of where in the list of tokens we're operating
        name: The name of the to be ran function
        result: A list that keeps track of all of the variables are to be passed to the selected function
        return: A list containing all of the variables that are to be passed to the selected function, and a integer representing where in the 
         list of tokens the current section of code ends
        '''
        if self.tokens[token_count][1] == "STAT_START" and self.tokens[token_count + 1][1] == "STAT_START":
            # All relevant statements start with "siekiera, motyka"
            next_line = self.find_token_type_index(token_count, ["NEWLINE"])[0] + 1
            if self.tokens[token_count + 2][1] == "NOTHING":
                # If end of variables has been found
                return result, self.find_token_type_index(next_line, ["NEWLINE"])[0] + 1
            elif self.tokens[token_count + 2][0] == name:
                # If another variable for the function has been found
                return self.get_function_execution_vars_out_func(self.find_token_type_index(next_line, ["NEWLINE"])[0] + 1, 
                                                  name, result + [self.tokens[next_line][0]])
            else:
                # Error
                return None, None
        else:
            # If nothing interesting happens
            return self.get_function_execution_vars_out_func(token_count + 1, name, result)

    def split_into_commands(self, token_count, commands):
        ''' Function creates a AST based on the nodes that are created using self.tokens

        token_count: A counter that keeps track of where in the list of tokens we're operating
        commands: A list keeping track of all of the segments of code that have been found
        return: An AST containing all of the code
        '''
        if token_count >= len(self.tokens):
            # If all tokens have been analysed
            return nodes.AST(commands)

        elif self.tokens[token_count][1] == "STAT_START" and self.tokens[token_count + 1][1] == "STAT_START":
            # Important statements always start with "siekiera, motyka"
            line_end = self.find_token_type_index(token_count, ["NEWLINE"])[0]
            
            if self.tokens[line_end - 1][1] == "DEF_FUNC":
                # If current statement denotes the start of a function definition
                # First get function declaration
                func_name, func_type, func_dec, new_count = self.get_function_declaration_out_func(line_end - 1)

                # Then get func definition
                def_start = self.find_token_not_type_index(self.get_paragraph_end_index(new_count), ["NEWLINE"])[0]
                func_def, new_count = self.get_code_segment_in_func(def_start, "END", [])

                # Create node for function and save it
                node = nodes.DefFunc(func_name, func_type, func_dec, func_def)
                return self.split_into_commands(new_count, commands + [node])

            elif self.tokens[line_end - 1][1] in ["INT", "FLOAT", "STRING", "LIST"]:
                # If sentence ends with a type, create a new variable and save it
                node, new_count = self.get_var_out_func(line_end - 1)
                return self.split_into_commands(new_count, commands + [node])
            
            elif self.tokens[line_end - 1][1] == "RUN_FUNC":
                # If current statement denotes the start of a function definition
                # Create node for executing a function, and save it
                func_name = self.tokens[line_end - 2][0]
                func_storage = self.tokens[self.find_token_type_index(line_end + 1, ["NEWLINE"])[0] + 3][0]
                func_params, new_count = self.get_function_execution_vars_out_func(self.find_token_not_type_index(
                                                                          self.get_paragraph_end_index(token_count), 
                                                                          ["NEWLINE"])[0], func_name, [])
                node = nodes.ExeFunc(func_name, func_params, func_storage)
                return self.split_into_commands(new_count, commands + [node])
            
            else:
                # Nothing interesting happens
                return self.split_into_commands(token_count + 1, commands)

        else:
            # If currently selected tokens doesn't have any significant meaning
            return self.split_into_commands(token_count + 1, commands)

    def __repr__(self):
        return str(self.tokens)

def main():
    # Capabilities:
        # Allways:
            # - Create var; list and single
            # - Run functions
        # Inside function:
            # - Change existing var
            # - Run functions
            # - While-loops
            # - If-statements
            # - Return something
        # Outside function:
            # - Create functions

    # Var or func names with whitespaces arent allowed, nor is anything really, fuck whitepaces
    # File needs to end with NEWLINE
    code = re.split("(\n)| |, |#.*", open("custom_code.txt", "r").read())
    sys.setrecursionlimit(len(code) * 2)
    tokens = lexer(code, 0, token_types, [])
    test = Parser(tokens)
    print(test.split_into_commands(0, []))

main()