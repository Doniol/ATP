    def get_refrain_type(self, token_count, result):
        # What if name consists of multiple tokens?
        # Too bad, isnt allowed
        if self.tokens[token_count][1] is "REST":
            # Nothing interesting found
            return self.get_refrain_type(token_count + 1)
        elif self.tokens[token_count][1] is "RUN_FUNC":
            #TODO: Figure out how to do this in the custom codeformat
            # Call on another function within this one
            
        elif self.tokens[token_count][1] is "RETURN":
            # If the function wants to return something
            return "RETURN", self.tokens[self.find_token_type_index(token_count, ["NEWLINE"]) + 1]
        elif self.tokens[token_count][1] is "END_FUNC":
            # If the function has ended
            return "FUNC_END"
        elif self.tokens[token_count][1] is "NOTHING":
            # Nothing happens this paragraph
            return None
        elif self.tokens[token_count][1] is "CHANGE":
            #TODO: What if name of return var is multiple tokens?
            #TODO: Function for additions/getting values
            # An existing variable is being changed
            var_name = self.tokens[self.find_token_type_index(self.find_token_type_index(token_count, ["NEWLINE"]) + 1, ["NEWLINE"])]
            new_data = #
            return "VAR_CHANGE", []
        elif self.tokens[token_count][1] is in ["INT", "FLOAT", "STRING"]:
            # Return newly created var
            newline = self.find_token_type_index(token_count, ["NEWLINE"])
            var_name = self.get_string_between(token_count + 1, newline)
            std_val = self.tokens[newline + 1]
            return "NEWVAR", self.tokens[token_count][1], [var_name, self.tokens[token_count][1], std_val]
        elif self.tokens[token_count][1] is "LIST":
            #TODO: function for getting list values
            # Return newly created var
            newline = self.find_token_type_index(token_count, ["NEWLINE"])
            var_name = self.get_string_between(token_count + 2, newline)
            var_type = ["LIST", self.tokens[token_count + 1]]
            std_val = #
            return "NEWVAR", var_type, [var_name, std_val]
        elif self.tokens[token_count][1] is "WHILE":
            # Refrain is while loop
            if self.tokes[token_count + 1][1] is "END":
                # Refrain denotes end of while-loop
                return "IF", "END"
            else:
                #TODO: Create function for reading if/while statements
                # While loop is starting
                statement = #
                return "IF", "START", statement
        elif self.tokens[token_count][1] is "IF":
            # Refrain is if-statement
            if self.tokes[token_count + 1][1] is "END":
                # Refrain denotes end of if-statement
                return "WHILE", "END"            
            else:
                #TODO: Create function for reading if/while statements
                # If statement is starting
                statement = #
                return "WHILE", "START", statement