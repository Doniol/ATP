def func_name(number: int=0, string: str=""):
    while number > 0:
        print(string)
        number = number - 1
    return number


amount: int = 3
word: str = "test"
output: int = 0
output = func_name(amount, word)
print(output)