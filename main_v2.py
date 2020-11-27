import re
from enum import Enum


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
    "#": "COMMENT", 
    # "\w*": "REST"
}

class Token:
    def __init__(self, word, token_type):
        self.word = word
        self.type = token_type


def assign_token(word, token_types):
    if word in token_types:
        return token_types[word]
    else:
        return "REST"


def assign_sentence(words, word_index, token_types, tokens):
    if len(words) == word_index or words[word_index] == "\n":
        return tokens, word_index
    else:
        return assign_sentence(words, word_index + 1, token_types, 
                tokens + [assign_token(words[word_index], token_types)])

    
def lexer(words, word_index, token_types, tokens):
    if word_index == len(words):
        return tokens
    else:
        new_tokens, new_index = assign_sentence(words, word_index, token_types, [])
        return lexer(words, new_index, token_types, 
                tokens + new_tokens)


def main():
    code = re.split("(\n)| |, ", open("custom_code.txt", "r").read())
    print(len(code))
    print(lexer(code, 0, token_types, []))


main()