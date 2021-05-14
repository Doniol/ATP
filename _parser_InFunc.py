import nodes
from typing import Tuple, List, Union, Any


def fill_list_in_func(self, token_count: int) -> Tuple[List[str], int]:
    ''' Function that returns all data stored in a newly declared list
    Function only for use inside of function definitions

    token_count: A counter that keeps track of where in the list of tokens we're operating
    return: A list filled with all of the variables stored in the selected list, and a integer representing where in the 
        list of tokens the current section of code ends
    '''
    if self.tokens[token_count].type != "NOTHING":
        # Select first text token
        line_end = self.find_token_type_index(token_count, ["NEWLINE"])[0]
        next_line_end = self.find_token_type_index(line_end + 1, ["NEWLINE"])[0]
        first_non_newline = self.find_token_not_type_index(next_line_end + 1, ["NEWLINE"])[0]
        # Run this function again but for next paragraph/part of lyrics
        other_vars = self.fill_list_in_func(first_non_newline)
        return [self.tokens[token_count].word] + other_vars[0], other_vars[1]
    else:
        # All data to be stored in the list has been found, return this data together with the index of the end of 
        #   the current paragraph
        return [], self.get_paragraph_end_index(token_count)


def get_function_execution_vars_in_func(self, token_count: int, func_name: str) -> Tuple[List[str], int]:
    ''' Function that returns all variables that are passed to a to be run function
    Function only for use inside of function definitions

    token_count: A counter that keeps track of where in the list of tokens we're operating
    func_name: The name of the to be ran function
    return: A list containing all the variables that are to be passed to a function, and a integer representing where in the 
        list of tokens the current section of code ends
    '''
    if self.tokens[token_count].word == func_name and self.tokens[token_count + 1].type == "NEWLINE":
        # Get the next variable for the function
        var_index = self.find_token_type_index(token_count + 2, ["NEWLINE"])[0] + 1
        var_name = self.tokens[var_index].word
        # Call this function anew, but for the next paragraph
        other_vars = self.get_function_execution_vars_in_func(self.get_paragraph_end_index(token_count), func_name)
        return [var_name] + other_vars[0], other_vars[1]
    elif self.tokens[token_count].type == "NOTHING":
        # All given vars have been found, return them together with a index for the end of the current paragraph
        return [], self.get_paragraph_end_index(token_count)
    else:
        # Nothing of interest happens
        return self.get_function_execution_vars_in_func(token_count + 1, func_name)


def get_condition_in_func(self, token_count: int) -> List[str]:
    ''' Function that returns the statement following a if/else declaration
    Function only for use inside of function definitions

    token_count: A counter that keeps track of where in the list of tokens we're operating
    return: A list containing the created statement
    '''
    condition = [self.tokens[token_count].word]
    
    if self.tokens[token_count + 1].word in ["wiecej", "mniej"]: # > or <, and must be follow with a non-relevant word
        condition += [self.tokens[token_count + 1].word, self.tokens[token_count + 3].word]
    elif self.tokens[token_count + 1].word in ["jest", "nie"]: # == or !=
        condition += [self.tokens[token_count + 1].word, self.tokens[token_count + 2].word]
    else:
        raise Exception("Incorrect condition using following tokens: " + self.tokens[token_count: token_count + 3])
    
    return condition


def get_paragraph_data_in_func(self, token_count: int) -> Union[Tuple[str, Any, int], Tuple[str, int]]:
    ''' Return what happens in current paragraph
    Function only for use inside of function definitions

    token_count: A counter that keeps track of where in the list of tokens we're operating
    return: A tuple that always contains the type of the paragraph and the index of the paragraphs' end, sometimes also
        contains newly created nodes
    '''
    if self.tokens[token_count].type == "RUN_FUNC":
        # Call on another function within the currently selected one
        # Find end of next line
        new_line = self.find_token_type_index(token_count + 2, ["NEWLINE"])[0]
        # Find end of following line and use it to get save var name
        next_line = self.find_token_type_index(new_line + 1, ["NEWLINE"])[0]

        # Get necessary values
        func_name = self.tokens[token_count - 1].word
        func_save = self.tokens[next_line - 1].word
        func_vars, new_count = self.get_function_execution_vars_in_func(self.find_token_type_index(next_line + 1, ["NEWLINE"])[0] + 1, func_name)
        # Create new node
        node = nodes.ExeFunc(func_name, func_vars, func_save)
        return "RUN_FUNC", node, new_count

    elif self.tokens[token_count].type == "RETURN":
        # If the function wants to return something
        # Get necessary values
        var_name = self.tokens[self.find_token_type_index(token_count, ["NEWLINE"])[0] + 1].word
        # Create new node
        node = nodes.Return(var_name)
        return "RETURN", node, self.get_paragraph_end_index(token_count)    

    elif self.tokens[token_count].type == "PRINT":
        # If the function wants to print something
        # Get necessary values
        var_name = self.tokens[self.find_token_type_index(token_count, ["NEWLINE"])[0] + 1].word
        # Create new node
        node = nodes.Print(var_name)
        return "PRINT", node, self.get_paragraph_end_index(token_count) 

    elif self.tokens[token_count].type == "END_FUNC":
        # If the function has ended
        return "END", self.get_paragraph_end_index(token_count)

    elif self.tokens[token_count].type == "NOTHING":
        # Nothing happens this paragraph
        return None, self.get_paragraph_end_index(token_count)

    elif self.tokens[token_count].type in ["INT", "FLOAT", "STRING"]:
        # Create new non-list variable
        newline = self.find_token_type_index(token_count, ["NEWLINE"])[0]
        # Get necessary values
        var_name = self.tokens[token_count + 1].word
        var_type = self.tokens[token_count].type
        var_val = self.tokens[newline + 1].word
        # Create new node
        node = nodes.AssignVar(var_name, var_type, var_val)
        return "NEWVAR", node, self.get_paragraph_end_index(token_count)

    elif self.tokens[token_count].type == "LIST":
        # Create new list variable
        newline = self.find_token_type_index(token_count, ["NEWLINE"])[0]
        # Get necessary values
        var_name = self.tokens[token_count + 2].word
        list_type = self.tokens[token_count + 1].type
        vals, new_count = self.fill_list_in_func(newline + 1)
        # Create new node
        node = nodes.AssignList(var_name, list_type, vals)
        return "NEWVAR", node, new_count

    elif self.tokens[token_count].type == "CHANGE":
        # An existing variable is being changed
        # Get necessary values
        var_name = self.tokens[self.find_token_type_index(self.find_token_type_index(token_count, 
                            ["NEWLINE"])[0] + 1, ["NEWLINE"])[0] - 1].word
        line_end = self.find_token_type_index(token_count, ["NEWLINE"])[0]
        # Get instructions for changing variable; a change always consists of 3 parts: a lhs variable, a calculation and a rhs variable
        val = list(map(lambda x: x.word, self.tokens[self.find_token_type_index(line_end + 1, ["NEWLINE"])[0] + 1: self.find_token_type_index(line_end + 1, ["NEWLINE"])[0] + 4]))
        # Create new node
        node = nodes.ChangeVar(var_name, val)
        return "VAR_CHANGE", node, self.get_paragraph_end_index(token_count)

    elif self.tokens[token_count].type == "WHILE":
        # Refrain is while loop
        if self.tokens[token_count + 1].type == "END":
            # Refrain denotes end of while-loop
            return "WHILE_END", self.get_paragraph_end_index(token_count)  
        else:
            # While loop is starting
            # Get necessary values
            statement_start = self.find_token_type_index(token_count, ["NEWLINE"])[0] + 1
            statement = self.get_condition_in_func(statement_start)
            # Dont create new node yet, do so only when all underlying code has been found
            return "WHILE_START", statement, self.get_paragraph_end_index(statement_start)

    elif self.tokens[token_count].type == "IF":
        # Refrain is if-statement
        if self.tokens[token_count + 1].type == "END":
            # Refrain denotes end of if-statement
            return "IF_END", self.get_paragraph_end_index(token_count) 
        else:
            # If statement is starting
            # Get necessary values
            statement_start = self.find_token_type_index(token_count, ["NEWLINE"])[0] + 1
            statement = self.get_condition_in_func(statement_start)
            # Dont create new node yet, do so only when all underlying code has been found
            return "IF_START", statement, self.get_paragraph_end_index(statement_start)

    else:
        # Nothing interesting found
        return self.get_paragraph_data_in_func(token_count + 1)


def get_code_segment_in_func(self, token_count, ending):
    ''' Function returns all of the different commands within a function
    Function only for use inside of function definitions

    token_count: A counter that keeps track of where in the list of tokens we're operating
    ending: A token_type upon which the current segment of code (eg. while-loop, func definition or if-statement) ends
    result: A list keeping track of all newly created nodes within this code segment
    return: A list containing all newly created nodes within this code segment, and a integer representing where in the 
        list of tokens the current section of code ends
    '''
    # Get data about paragraph
    paragraph = self.get_paragraph_data_in_func(token_count)
    paragraph_type = paragraph[0]
    if paragraph_type == ending:
        # If paragraph denotes the end to a segment of the code; e.g. ending the if/while/func def
        return [], paragraph[-1]
    elif paragraph_type == "WHILE_START":
        # If paragraph denotes the start to a while-loop
        statement = paragraph[1]
        code, new_count = self.get_code_segment_in_func(paragraph[-1], "WHILE_END")
        # Create while node
        node = nodes.WhileNode(token_count, statement, code)
        other_segments = self.get_code_segment_in_func(new_count, ending)
        return [node] + other_segments[0], other_segments[1]
    elif paragraph_type == "IF_START":
        # If paragraph denotes the start to a if-thingy
        statement = paragraph[1]
        code, new_count = self.get_code_segment_in_func(paragraph[-1], "IF_END")
        # Create if node
        node = nodes.IfNode(token_count, statement, code)
        other_segments = self.get_code_segment_in_func(new_count, ending)
        return [node] + other_segments[0], other_segments[1]
    else:
        # If nothing special happens
        other_segments = self.get_code_segment_in_func(paragraph[-1], ending)
        return [paragraph[1]] + other_segments[0], other_segments[1]

