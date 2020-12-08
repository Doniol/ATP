from lexer import lexer, token_types
import re
import sys
import nodes


class Parser():
    def __init__(self, tokens):
        self.tokens = tokens
        self.commands = []

    def find_token_type_index(self, token_count, token_types):
        ''' Function that finds the first token of a certain type, starting from the given index and counting forwards

        token_count: 
        token_types: 
        return: 
        '''
        if self.tokens[token_count][1] in token_types:
            return token_count, self.tokens[token_count][1]
        else:
            return self.find_token_type_index(token_count + 1, token_types)
    
    def find_token_not_type_index(self, token_count, token_types):
        ''' Function that finds the first token that isn't a certain type, starting from the given index and 
             counting forwards

        token_count: 
        token_types: 
        return: 
        '''
        if self.tokens[token_count][1] not in token_types:
            return token_count, self.tokens[token_count][1]
        else:
            return self.find_token_not_type_index(token_count + 1, token_types)
    
    def find_token_type_index_backwards(self, token_count, token_types):
        ''' Function that finds the first token of a certain type, starting from the given index and counting backwards

        token_count: 
        token_types: 
        return: 
        '''
        if self.tokens[token_count][1] in token_types:
            return token_count, self.tokens[token_count][1]
        else:
            return self.find_token_type_index_backwards(token_count - 1, token_types)
    
    def get_func_params(self, token_count, result, par_num):
        ''' Function that returns a list of all parameters found in a new function declaration

        token_count: 
        result:
        par_num:
        return: 
        '''
        if self.tokens[token_count][1] == "STAT_START" and self.tokens[token_count + 1][1] == "STAT_START":
            # All important statements start with "siekiera, motyka"
            if par_num == -1:
                # If par_num hasn't been read yet
                par_count = int(self.tokens[token_count + 2][0])
                return self.get_func_params(self.get_paragraph_end_index(token_count), result, par_count)
            elif len(result) == par_num:
                # If refrain is still going, but all params have already been found
                return result, token_count
            elif par_num == 0:
                # If there are no parameters to be found
                return result + [None], token_count
            else:
                # If refrain is still going, but not all params have already been given
                param, new_count = self.get_var_out_func(self.find_token_type_index(token_count, ["NEWLINE"])[0] - 1)
                return self.get_func_params(new_count, result + [param], par_num)

        else:
            # If not in important statement
            if len(result) != par_num:
                # If not in a relevant part of the refrain
                return self.get_func_params(token_count + 1, result, par_num)
            else:
                # If all vars have already been given
                return result, token_count

    def fill_list_outside_function(self, token_count, list_name, results):
        ''' Function that fills a found list with the corresponding entries

        token_count: 
        list_name: 
        results: 
        return: 
        '''
        if self.tokens[token_count][1] == "STAT_START" and self.tokens[token_count + 1][1] == "STAT_START":
            # All relevant statements start with "siekiera, motyka"
            line_end = self.find_token_type_index(token_count + 2, ["NEWLINE"])[0]
            if self.tokens[token_count + 2][1] != "NOTHING":
                # If current line is indeed adding another entry to the list
                if self.tokens[token_count + 2][0] == list_name:
                    # Check if we're still in the correct list
                    return self.fill_list_outside_function(self.find_token_type_index(line_end + 1, ["NEWLINE"])[0] + 1,
                                          list_name, results + [self.tokens[line_end + 1][0]])
                else:
                    # Error
                    return None, None
            else:
                # If current line signifies end of new entries to current list
                return results, self.find_token_type_index(line_end + 1, ["NEWLINE"])[0] + 1
        else:
            # If current token is not the start of a new statement
            return self.fill_list_outside_function(token_count + 1, list_name, results)

    def declare_function(self, token_count):
        ''' Function that gets all data that is relevant to new function declaration

        token_count: 
        return: 
        '''
        # Get all necessary function details
        func_name = self.tokens[token_count - 1][0]
        func_type = self.tokens[token_count + 2][1]
        func_dec, new_count = self.get_func_params(self.find_token_type_index(token_count + 2, ["STAT_START"])[0], [], -1)
        return func_name, func_type, func_dec, new_count

    def get_list_in_func(self, token_count, result):
        ''' Function that returns all data stored in a newly declared list

        token_count: 
        result: 
        return: 
        '''
        if self.tokens[token_count][1] != "NOTHING":
            # Select first text token
            line_end = self.find_token_type_index(token_count, ["NEWLINE"])[0]
            next_line_end = self.find_token_type_index(line_end + 1, ["NEWLINE"])[0]
            first_non_newline = self.find_token_not_type_index(next_line_end + 1, ["NEWLINE"])[0]
            # Run this function again but for next paragraph/part of lyrics
            return self.get_list_in_func(first_non_newline, result + [self.tokens[token_count][0]])
        else:
            # All data to be stored in the list has been found, return this data together with the index of the end of 
            #   the current paragraph
            return result, self.get_paragraph_end_index(token_count)

    def get_func_vars_in_func(self, token_count, result, save_var):
        #TODO: Combine with get_func_run_in_func()
        ''' Function that returns all variables that are passed to a to be run function
        This function is only meant for use within a function declaration.

        token_count: 
        result: 
        save_var: 
        return: 
        '''
        if self.tokens[token_count][0] == save_var and self.tokens[token_count + 1][1] == "NEWLINE":
            # Get the next variable for the function
            var_index = self.find_token_type_index(token_count + 2, ["NEWLINE"])[0] + 1
            var_name = self.tokens[var_index][0]
            # Call this function anew, but for the next paragraph
            return self.get_func_vars_in_func(self.get_paragraph_end_index(token_count), result + [var_name], save_var)
        elif self.tokens[token_count][1] == "NOTHING":
            # All given vars have been found, return them together with a index for the end of the current paragraph
            return result, self.get_paragraph_end_index(token_count)
        else:
            # Nothing of interest happens
            return self.get_func_vars_in_func(token_count + 1, result, save_var)

    def get_func_run_in_func(self, token_count):
        #TODO: Make it so that more variables arent denoted by the save_var, but by func_name
        ''' Function that returns all data pertraining to running a new function
        This function is only meant for use within a function declaration.

        token_count: 
        return: 
        '''
        # Find end of next line
        new_line = self.find_token_type_index(token_count + 2, ["NEWLINE"])[0]
        # Find end of following line and use it to get save var name
        next_line = self.find_token_type_index(new_line + 1, ["NEWLINE"])[0]

        # Get all vars, given token_count is end of current paragraph
        func_name = self.tokens[token_count - 1][0]
        save_var = self.tokens[next_line - 1][0]
        func_vars, new_count = self.get_func_vars_in_func(self.find_token_type_index(next_line + 1, ["NEWLINE"])[0] + 1, [], save_var)
        return func_name, func_vars, save_var, new_count

    def get_paragraph_end_index(self, token_count):
        ''' Get index of end of paragraph, by way of searching for 2 consecutive NEWLINEs
        This function can be used both in- and outside a function definition.

        token_count: 
        return: 
        '''
        if self.tokens[token_count][1] == "NEWLINE" and self.tokens[token_count + 1][1] == "NEWLINE":
            return token_count
        else:
            return self.get_paragraph_end_index(token_count + 1)

    def get_change_in_func(self, token_count, result):
        ''' Function for recording what is going to happen to the selected variable

        token_count: 
        result: 
        return: 
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

    def get_change_var_in_func(self, token_count):
        #TODO: Fuck right off with this function, remove it somehow
        ''' Why the fuck does this exist?
        '''
        line_end = self.find_token_type_index(token_count, ["NEWLINE"])[0]
        return self.get_change_in_func(self.find_token_type_index(line_end + 1, ["NEWLINE"])[0] + 1, [])

    def get_statement(self, token_count, result):
        ''' Function that returns the statement following a if/else declaration

        token_count: 
        result: 
        return: 
        '''
        if len(result) == 0:
            return self.get_statement(token_count + 1, result + [self.tokens[token_count][0]])
        else:
            if self.tokens[token_count][0] in ["wiecej", "mniej"]: # > or <, and must be follow with a non-relevant word
                return self.get_statement(token_count + 3, result + [self.tokens[token_count][0], self.tokens[token_count + 2][0]])
            elif self.tokens[token_count][0] in ["jest", "nie"]: # == or !=
                return self.get_statement(token_count + 2, result + [self.tokens[token_count][0], self.tokens[token_count + 1][0]])
            else:
                return result

    def get_paragraph_type(self, token_count):
        #TODO: Returns too many unnecessary things, fix it
        ''' Return what happens in current paragraph
        This function is only meant for use within a function declaration.

        token_count:
        return:
        '''
        if self.tokens[token_count][1] == "RUN_FUNC":
            # Call on another function within the currently selected one
            # Get necessary values
            func_name, func_vars, func_save, new_count = self.get_func_run_in_func(token_count)
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
            vals, new_count = self.get_list_in_func(newline + 1, [])
            # Create new node
            node = nodes.AssignList(var_name, list_type, vals)
            return "NEWVAR", node, new_count

        elif self.tokens[token_count][1] == "CHANGE":
            # An existing variable is being changed
            # Get necessary values
            var_name = self.tokens[self.find_token_type_index(self.find_token_type_index(token_count, 
                                ["NEWLINE"])[0] + 1, ["NEWLINE"])[0] - 1][0]
            val = self.get_change_var_in_func(token_count)
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
                statement = self.get_statement(statement_start, [])
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
                statement = self.get_statement(statement_start, [])
                # Dont create new node yet, do so only when all underlying code has been found
                return "IF_START", statement, self.get_paragraph_end_index(statement_start)

        else:
            # Nothing interesting found
            return self.get_paragraph_type(token_count + 1)

    def get_code_segment(self, token_count, ending, result):
        #TODO: More efficiency in while/if declarations?
        ''' Function returns all of the different commands within a function

        token_count: 
        ending: 
        result: 
        return: 
        '''
        # Get data about paragraph
        refrain_type = self.get_paragraph_type(token_count)
        if refrain_type[0] in ending:
            # If paragraph denotes the end to a segment of the code; e.g. if/while/func def
            return result, refrain_type[-1]
        elif refrain_type[0] in "WHILE_START":
            # If paragraph denotes the start to a while-loop
            statement = refrain_type[1]
            code, new_count = self.get_code_segment(refrain_type[-1], "WHILE_END", [])
            # Create while node
            node = nodes.WhileNode(statement, code)
            return self.get_code_segment(new_count, ending, result + [node])
        elif refrain_type[0] in "IF_START":
            # If paragraph denotes the start to a if-thingy
            statement = refrain_type[1]
            code, new_count = self.get_code_segment(refrain_type[-1], "IF_END", [])
            # Create if node
            node = nodes.IfNode(statement, code)
            return self.get_code_segment(new_count, ending, result + [node])
        else:
            # If nothing special happens
            return self.get_code_segment(refrain_type[-1], ending, result + [refrain_type[1]])

    def get_var_out_func(self, token_count):
        ''' Function for getting al details about a var that is assigned outside of a function

        token_count: 
        return: 
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
            vals, new_count = self.fill_list_outside_function(self.find_token_type_index(token_count + 2, 
                                                              ["NEWLINE"])[0] + 1, var_name, [])
            node = nodes.AssignList(var_name, [var_type, list_type], vals)
            return node, new_count

    def get_func_run_out_func_params(self, token_count, name, result):
        ''' Function for finding what variables to give to a function when running it

        token_count: 
        name: 
        result: 
        return: 
        '''
        if self.tokens[token_count][1] == "STAT_START" and self.tokens[token_count + 1][1] == "STAT_START":
            # All relevant statements start with "siekiera, motyka"
            next_line = self.find_token_type_index(token_count, ["NEWLINE"])[0] + 1
            if self.tokens[token_count + 2][1] == "NOTHING":
                # If end of variables has been found
                return result, self.find_token_type_index(next_line, ["NEWLINE"])[0] + 1
            elif self.tokens[token_count + 2][0] == name:
                # If another variable for the function has been found
                return self.get_func_run_out_func_params(self.find_token_type_index(next_line, ["NEWLINE"])[0] + 1, 
                                                  name, result + [self.tokens[next_line][0]])
            else:
                # Error
                return None, None
        else:
            # If nothing interesting happens
            return self.get_func_run_out_func_params(token_count + 1, name, result)

    def split_into_commands(self, token_count, commands):
        # Specify inside of each function comment where that function is to be used; e.g. inside or outside functions
        ''' Function creates a AST based on the nodes that are created using self.tokens

        token_count: 
        commands: 
        return: 
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
                func_name, func_type, func_dec, new_count = self.declare_function(line_end - 1)

                # Then get func definition
                def_start = self.find_token_not_type_index(self.get_paragraph_end_index(new_count), ["NEWLINE"])[0]
                func_def, new_count = self.get_code_segment(def_start, "END", [])

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
                func_params, new_count = self.get_func_run_out_func_params(self.find_token_not_type_index(
                                                                          self.get_paragraph_end_index(token_count), 
                                                                          ["NEWLINE"])[0], func_name, [])
                node = nodes.ExeFunc(func_name, func_params, func_storage)
                return self.split_into_commands(new_count, commands + [node])
            
            else:
                # TEMPORARY SOLUTION TO PROBLEM
                #TODO: Fix this shit
                return self.split_into_commands(token_count + 1, commands)

        else:
            # If currently selected tokens doesn't have any significant meaning
            return self.split_into_commands(token_count + 1, commands)


def main():
    # Var or func names with whitespaces arent allowed
    # File needs to end with NEWLINE
    # The only thing that can be done outside of functions are creating a function, running a function and creating vars
    code = re.split("(\n)| |, |#.*", open("custom_code.txt", "r").read())
    sys.setrecursionlimit(len(code) * 2)
    tokens = lexer(code, 0, token_types, [])
    test = Parser(tokens)
    print(test.split_into_commands(0, []))

main()