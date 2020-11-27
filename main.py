import re
from collections import Counter


class Lexer():
    def __init__(self, source_code):
        self.source_code = source_code
        self.splitted_code = []
        self.tokens = []
        self.fix_words = {
            "iTn": "int",
            "lSiT": "list",
            "cAhR": "char"
        }
    
    def set_source_code(self, source_code):
        self.source_code = source_code

    def split_source_code(self):
        filthy_splitted_code = re.split("(,,.+,,|->|<-|\(|\]|;|, |>|<|\n| )", self.source_code)
        self.splitted_code = [part for part in filthy_splitted_code if part and len(part) > 0]
        return self.splitted_code
        
    def get_name(self, words, word_index, endings, result, count):
        if words[word_index] in endings:
            return result, count
        else:
            return self.get_name(words, word_index + 1, endings, result + words[word_index], count + 1)

    def get_func_vars(self, words, word_index, result):
        if words[word_index] == ";":
            return result
        else:
            if words[word_index] != ", ":
                word, count = self.get_name(words, word_index, [", ", ";"], "", 0)
                return self.get_func_vars(words, word_index + count, 
                result + [word])
            else:
                return self.get_func_vars(words, word_index + 1, result)

    def get_func_var_types(self, words, word_index, result_types, result_std):
        print(words[word_index])
        if words[word_index] == "not_end":
            return result_types, result_std
        else:
            if words[word_index] == ", " or words[word_index] == " ":
                return self.get_func_var_types(words, word_index + 1, result_types, result_std)
            else:
                # List with standard values
                if words[word_index] == "lSiT" and words[word_index + 4] == "!=":
                    # Create list of std variable
                    lst = self.get_list_entries(words, word_index + 7, [])
                    return self.get_func_var_types(words, word_index + len(lst) + 8, result_types + 
                            [[words[word_index], words[word_index + 2]]], 
                            result_std + [lst])
                # Other variable with standard values
                elif words[word_index + 2] == "!=":
                    return self.get_func_var_types(words, word_index + 5,
                    result_types + [words[word_index]], result_std + [words[word_index + 4]])
                # List without standard values
                elif words[word_index] == "lSiT":
                    return self.get_func_var_types(words, word_index + 3,
                    result_types + [[words[word_index], words[word_index + 2]]],
                    result_std + [None])
                # Other variable without standard values
                else:
                    return self.get_func_var_types(words, word_index + 1,
                    result_types + [words[word_index]], result_std + [None])

    def get_list_entries(self, words, word_index, results):
        if words[word_index] == "<":
            return results
        else:
            return self.get_list_entries(words, word_index + 1, results + [words[word_index]])

    def create_tokens(self):
        word_index = 0
        #TODO: Dont check spaces, /n and other useless shite
        while word_index < len(self.splitted_code):
            word = self.splitted_code[word_index]
            # String
            if word[:2] == ",,":
                self.tokens.append(["STRING", word])
            # Function name
            elif word == "->" and self.splitted_code[word_index + 2] == "(":
                #TODO: Function could return list
                # Get the function type
                FUNC_TYPE = self.fix_words[self.splitted_code[word_index - 2]]
                word_index += 2

                # Append the entire function name
                FUNC_NAME, count = self.get_name(self.splitted_code, word_index + 1, ["]"], "", 1)
                word_index += count

                # Append all variable names
                FUNC_VARS = self.get_func_vars(self.splitted_code, word_index + 1, [])
                word_index += len(FUNC_VARS) + 2

                # Append the types of the previous vars, and their standard values
                FUNC_VAR_TYPES, VAR_STD_VALS = self.get_func_var_types(self.splitted_code, word_index + 2, [], [])                    
                self.tokens.append(["FUNC DEC", [FUNC_NAME, FUNC_TYPE, FUNC_VARS, FUNC_VAR_TYPES, VAR_STD_VALS]])
            elif word == "not_end":
                self.tokens.append(["FUNC START", word])
            elif word == "not_start":
                self.tokens.append(["FUNC END", word])
            elif word == "fI":
                self.tokens.append(["IF", word])
            elif word == "Fi":
                self.tokens.append(["ELIF", word])
            elif word == "eSlE":
                self.tokens.append(["ELSE", word])
            elif word == "(":
                
            word_index += 1
        return self.tokens

    def get_func_call(self, words, word_index, result):
        if words[word_index] == "]":
            return result
        else:



def main():
    test = open("custom_code.txt", "r").read()
    lexer = Lexer(test)
    print(lexer.split_source_code())
    print(lexer.create_tokens())


main()