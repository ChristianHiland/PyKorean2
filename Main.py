from Helpers import *
import sys

args = sys.argv

if args[1].lower() == "scratch":
    test = False

    if test:
        print("Test 1:", advanced_translate_logic("I like to program read and make games"))
        print("Test 2:", advanced_translate_logic("I think wolves are cute"))
        print("Test 3:", advanced_translate_logic("I go to the store"))
        print("Test 4:", advanced_translate_logic("I went to the store, and I bought some milk"))
        print("Test 5:", advanced_translate_logic("He went to the store, and bought some milk"))
        print("Test 6:", advanced_translate_logic("Lunbin went to the store, and he bought some milk"))
    else:
        words = input("Words: ")
        final = advanced_translate_logic(words)
        print(final)
elif args[1].lower() == "learn":
    