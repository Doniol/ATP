paragraph = self.get_paragraph_type(token_count)
        paragraph_type = paragraph[0]
        if paragraph[0] == ending:
            # If paragraph denotes the end to a segment of the code; e.g. if/while/func def
            return result, paragraph[-1]
        elif paragraph[0] == "WHILE_START":
            # If paragraph denotes the start to a while-loop
            statement = paragraph[1]
            code, new_count = self.get_code_segment(paragraph[-1], "WHILE_END", [])
            # Create while node
            node = nodes.WhileNode(statement, code)
            return self.get_code_segment(new_count, ending, result + [node])
        elif paragraph[0] == "IF_START":
            # If paragraph denotes the start to a if-thingy
            statement = paragraph[1]
            code, new_count = self.get_code_segment(paragraph[-1], "IF_END", [])
            # Create if node
            node = nodes.IfNode(statement, code)
            return self.get_code_segment(new_count, ending, result + [node])
        else:
            # If nothing special happens
            return self.get_code_segment(paragraph[-1], ending, result + [paragraph[1]])