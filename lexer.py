import re
import sys


token_types = {
    "kazdy": "WHILE", 
    "jesli": "IF", 
    "koniec": "END", 
    "defa": "DEF_FUNC", 
    "runa": "RUN_FUNC", 
    "siekiera": "STAT_START", 
    "motyka" : "STAT_START",
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
    "#": "COMMENT",
    "rozno": "MANYTYPES",
    "zmien": "CHANGE"
}


class Token:
    def __init__(self, word, token_type):
        self.word = word
        self.type = token_type
    
    def __repr__(self):
        if self.word != "\n":
            return self.word + " " + self.type
        else:
            return self.type

# Lexer
def create_simple_token(word, token_types):
    if word in token_types:
        return [word, token_types[word]]
    elif word and word != "":
        return [word, "REST"]


def create_regular_token(word, token_types):
    if word in token_types:
        return Token(word, token_types[word])
    elif word and word != "":
        return Token(word, "REST")
 

def get_tokens(words, word_index, token_types, tokens, token_func):
    if word_index == len(words):
        return tokens
    else:
        token = token_func(words[word_index], token_types)
        if token:
            return get_tokens(words, word_index + 1, token_types, tokens + [token], token_func)
        else:
            return get_tokens(words, word_index + 1, token_types, tokens, token_func)


def lexer(t_types, simple_token):
    def wrapper(words):
        if simple_token:
            return get_tokens(words, 0, t_types, [], create_simple_token)
        else:
            return get_tokens(words, 0, t_types, [], create_regular_token)
    return wrapper
    

def main():
    #TODO: Optimise search ranges when giving index (token_count)
    words = re.split("(\n)| |, |#.*", open("custom_code.txt", "r").read())
    sys.setrecursionlimit(len(words) * 2)
    print(len(words))
    custom_lexer = lexer(token_types, False)
    print(custom_lexer(words))
