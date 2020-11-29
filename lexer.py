token_types = {
    "kazdy": "WHILE", 
    "jesli": "IF", 
    "koniec": "END", 
    "defa": "DEF_FUNC", 
    "runa": "RUN_FUNC", 
    "siekiera": "STAT_START", 
    "slowo": "STRING", 
    "lista": "LIST", 
    "inta": "INT", 
    "flota": "FLOAT", 
    "oddaj": "RETURN", 
    "ducem": "END_FUNC", 
    "\n": "NEWLINE", 
    "len": "LEN", 
    "print": "PRINT", 
    "nic": "NOTHING", 
    "pustka": "EMPTY", 
    "#": "COMMENT"
}


class Token:
    def __init__(self, word, token_type):
        self.word = word
        self.type = token_type

# Lexer
def assign_token(word, token_types):
    if word in token_types:
        return [token_types[word], word]
    elif word and word != "":
        return ["REST", word]
    

def lexer(words, word_index, token_types, tokens):
    if word_index == len(words):
        return tokens
    else:
        token = assign_token(words[word_index], token_types)
        if token:
            return lexer(words, word_index + 1, token_types, tokens + [token])
        else:
            return lexer(words, word_index + 1, token_types, tokens)
