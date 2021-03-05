import re
import sys
from typing import List, Dict, Callable, Any, Union


# This is a dictionary filled with all token types, and what word assigns said type
# This list can be changed up to make rhyming easier, or to make the song-text sound better
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
    "rozno": "ANY", 
    "zmien": "CHANGE"
}


class Token:
    ''' Class for individual tokens
    '''
    def __init__(self, word: str, token_type: str) -> None:
        ''' Inits the class

        word: The word that is assigned to this token
        token_type: The type of token
        '''
        self.word = word
        self.type = token_type
    
    def __repr__(self) -> str:
        ''' Returns a string representing the class

        return: A string denoting what is contained within this class
        '''
        if self.word != "\n":
            return self.word + " " + self.type
        else:
            return self.type


def create_simple_token(word: str, token_types: Dict[str, str]) -> List[str]:
    ''' Creates a new token without using the Token class

    word: The word that is to be tokenised
    token_types: A dictionary filled with token_types and their corresponding words
    return: A list containing the given word, and the corresponding token type
    '''
    if word in token_types:
        return [word, token_types[word]]
    elif word and word != "":
        return [word, "REST"]


def create_regular_token(word: str, token_types: Dict[str, str]) -> Token:
    ''' Creates a new token using the Token class

    word: The word that is to be tokenised
    token_types: A dictionary filled with token_types and their corresponding words
    return: A token containing the given word, and the corresponding token type
    '''
    if word in token_types:
        return Token(word, token_types[word])
    elif word and word != "":
        return Token(word, "REST")
 

def get_tokens(words: List[str], word_index: int, token_types: Dict[str, str], tokens: List[Any], token_func: Callable[[str, Dict[str, str]], Any]) -> List[Any]:
    ''' A function for tokenising a list of words

    words: A list of to be tokenised words
    word_index: A index denoting how far into the list the function has gotten
    token_types: A dictionary filled with token_types and their corresponding words
    tokens: A list containing the created tokens
    token_func: The selected function for creating tokens
    return: A list containing the created tokens
    '''
    if word_index == len(words):
        return tokens
    else:
        token = token_func(words[word_index], token_types)
        # Necessary if/else statement, because some words within the words-list are None, which if not dealt with properly could cause problems
        if token:
            return get_tokens(words, word_index + 1, token_types, tokens + [token], token_func)
        else:
            return get_tokens(words, word_index + 1, token_types, tokens, token_func)


def lexer(token_types: Dict[str, str], simple_token: bool) -> Callable[[Union[List[str], List[Token]]], List[Any]]:
    ''' Returns a function that lexes a list of words

    token_types: A dictionary filled with token_types and their corresponding words
    simple_token: A boolean value to choose between using the Token-class or just regular lists for creating tokens
    return: A function that can tokenise a list of words
    '''
    def wrapper(words: List[str]) -> Union[List[str], List[Token]]:
        ''' The function that is to be returned

        words: A list containing the to be tokenised words
        return: A list of tokens made from the given words
        '''
        if simple_token:
            return get_tokens(words, 0, token_types, [], create_regular_token)
        else:
            return get_tokens(words, 0, token_types, [], create_simple_token)
    return wrapper
    

def lex(file: str) -> Union[List[str], List[Token]]:
    ''' A function to tokenise all words from a given file

    file: The name of the file in string format
    return: A list containing the resulting tokens
    '''
    words = re.split("(\n)| |, |#.*", open(file, "r").read())
    sys.setrecursionlimit(len(words) * 2)
    custom_lexer = lexer(token_types, True)
    return custom_lexer(words)


def main():
    ''' Runs and prints the lexed data
    '''
    print(lex("test_2.txt"))

# main()
