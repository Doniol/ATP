import nodes
from typing import List, Tuple, Union


def get_func_params_out_func(self, token_count: int, par_num: int=-1, result: List[nodes.AssignVar]=[]) -> Tuple[List[nodes.AssignVar], int]:
    ''' Function that returns a list of all parameters found in a new function declaration
    Function only for use outside of function definitions; can be used within function declaration though

    token_count: A counter that keeps track of where in the list of tokens we're operating
    par_num: Amount of parameters to be found
    result: A list keeping track of all found parameters
    return: A list containing all found parameters, and a integer representing where in the list of tokens the current section of code ends
    '''
    if self.tokens[token_count].type == "STAT_START" and self.tokens[token_count + 1].type == "STAT_START":
        # All important statements start with "siekiera, motyka"
        if par_num == -1:
            # If par_num hasn't been read yet
            par_count = int(self.tokens[token_count + 2].word)
            return self.get_func_params_out_func(self.get_paragraph_end_index(token_count), par_count, result)
        elif len(result) == par_num:
            # If refrain is still going, but all params have already been found
            return result, token_count
        elif par_num == 0:
            # If there are no parameters to be found
            return [None], token_count
        else:
            # If refrain is still going, but not all params have already been given
            param, new_count = self.get_var_out_func(self.find_token_type_index(token_count, ["NEWLINE"])[0] - 1)
            return self.get_func_params_out_func(new_count, par_num, result + [param])

    else:
        # If not in important statement
        if len(result) != par_num:
            # If not in a relevant part of the refrain
            return self.get_func_params_out_func(token_count + 1, par_num, result)
        else:
            # If all vars have already been given
            return result, token_count


def fill_list_out_func(self, token_count: int, list_name: str) -> Tuple[List[str], int]:
    ''' Function that fills a found list with the corresponding entries
    Function only for use outside of function definitions

    token_count: A counter that keeps track of where in the list of tokens we're operating
    list_name: The name of the currently selected list
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
                other_vars = self.fill_list_out_func(self.find_token_type_index(line_end + 1, ["NEWLINE"])[0] + 1, list_name)
                return [self.tokens[line_end + 1].word] + other_vars[0], other_vars[1]
            else:
                raise Exception("List called " + list_name + " not properly closed after filling.")
        else:
            # If current line signifies end of new entries to current list
            return [], self.find_token_type_index(line_end + 1, ["NEWLINE"])[0] + 1
    else:
        # If current token is not the start of a new statement
        return self.fill_list_out_func(token_count + 1, list_name)


def get_function_declaration_out_func(self, token_count: int) -> Tuple[str, Union[str, List[str]], List[nodes.AssignVar], int]:
    ''' Function that gets all data that is relevant to new function declaration
    Function only for use outside of function definitions

    token_count: A counter that keeps track of where in the list of tokens we're operating
    return: A tuple containing all information about the function (except the actual code within), and a integer representing 
     where in the list of tokens the current section of code ends
    '''
    # Get all necessary function details
    func_name = self.tokens[token_count - 1].word
    temp_type = self.tokens[token_count + 2].type
    if temp_type == "LIST":
        func_type = [temp_type, self.tokens[token_count + 3].type]
    else:
        func_type = temp_type
    func_dec, new_count = self.get_func_params_out_func(self.find_token_type_index(token_count + 2, ["STAT_START"])[0])
    return func_name, func_type, func_dec, new_count


def get_var_out_func(self, token_count: int) -> Tuple[nodes.AssignVar, int]:
    ''' Function for getting all details about a var that is assigned outside of a function
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
        list_type = self.tokens[token_count + 2].type
        vals, new_count = self.fill_list_out_func(self.find_token_type_index(token_count + 2, ["NEWLINE"])[0] + 1, var_name)
        node = nodes.AssignList(var_name, list_type, vals)
        return node, new_count


def get_function_execution_vars_out_func(self, token_count: int, name: str):
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
            return [], self.find_token_type_index(next_line, ["NEWLINE"])[0] + 1
        elif self.tokens[token_count + 2].word == name:
            # If another variable for the function has been found
            other_vars = self.get_function_execution_vars_out_func(self.find_token_type_index(next_line, ["NEWLINE"])[0] + 1, name)
            return [self.tokens[next_line].word] + other_vars[0], other_vars[1]
        else:
            # Error
            return None, None
    else:
        # If nothing interesting happens
        return self.get_function_execution_vars_out_func(token_count + 1, name)

