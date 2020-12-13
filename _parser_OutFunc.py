import nodes


def get_func_params_out_func(self, token_count, result, par_num):
    ''' Function that returns a list of all parameters found in a new function declaration
    Function only for use outside of function definitions; can be used within function declaration though

    token_count: A counter that keeps track of where in the list of tokens we're operating
    result: A list keeping track of all found parameters
    par_num: Amount of parameters to be found
    return: A list containing all found parameters, and a integer representing where in the list of tokens the current section of code ends
    '''
    if self.tokens[token_count].type == "STAT_START" and self.tokens[token_count + 1].type == "STAT_START":
        # All important statements start with "siekiera, motyka"
        if par_num == -1:
            # If par_num hasn't been read yet
            par_count = int(self.tokens[token_count + 2].word)
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
    if self.tokens[token_count].type == "STAT_START" and self.tokens[token_count + 1].type == "STAT_START":
        # All relevant statements start with "siekiera, motyka"
        line_end = self.find_token_type_index(token_count + 2, ["NEWLINE"])[0]
        if self.tokens[token_count + 2].type != "NOTHING":
            # If current line is indeed adding another entry to the list
            if self.tokens[token_count + 2].word == list_name:
                # Check if we're still in the correct list
                return self.fill_list_out_func(self.find_token_type_index(line_end + 1, ["NEWLINE"])[0] + 1,
                                        list_name, results + [self.tokens[line_end + 1].word])
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
    func_name = self.tokens[token_count - 1].word
    func_type = self.tokens[token_count + 2].type
    func_dec, new_count = self.get_func_params_out_func(self.find_token_type_index(token_count + 2, ["STAT_START"])[0], [], -1)
    return func_name, func_type, func_dec, new_count


def get_var_out_func(self, token_count):
    ''' Function for getting al details about a var that is assigned outside of a function
    Function only for use outside of function definitions

    token_count: A counter that keeps track of where in the list of tokens we're operating
    return: A newly created node containing the new variable, and a integer representing where in the 
        list of tokens the current section of code ends
    '''
    var_type = self.tokens[token_count].type
    var_name = self.tokens[token_count - 1].word
    if var_type in ["INT", "FLOAT", "STRING"]:
        # If variable isn't list
        val = self.tokens[token_count + 2].word
        node = nodes.AssignVar(var_name, var_type, val)
        return node, self.find_token_type_index(token_count + 2, ["NEWLINE"])[0]
    elif var_type == "LIST":
        # If variable is list
        list_type = self.tokens[token_count + 2].word
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
    if self.tokens[token_count].type == "STAT_START" and self.tokens[token_count + 1].type == "STAT_START":
        # All relevant statements start with "siekiera, motyka"
        next_line = self.find_token_type_index(token_count, ["NEWLINE"])[0] + 1
        if self.tokens[token_count + 2].type == "NOTHING":
            # If end of variables has been found
            return result, self.find_token_type_index(next_line, ["NEWLINE"])[0] + 1
        elif self.tokens[token_count + 2].word == name:
            # If another variable for the function has been found
            return self.get_function_execution_vars_out_func(self.find_token_type_index(next_line, ["NEWLINE"])[0] + 1, 
                                                name, result + [self.tokens[next_line].word])
        else:
            # Error
            return None, None
    else:
        # If nothing interesting happens
        return self.get_function_execution_vars_out_func(token_count + 1, name, result)