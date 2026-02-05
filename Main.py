from Helpers import *

test = True

if test:
    print("Test 1:", advanced_translate_logic("I like to program read and make games"))
    # Result: 나는 프로그램, 읽다, 계략, 만들다를 좋아한다

    print("Test 2:", advanced_translate_logic("I think wolves are cute"))
    # Result: 나는 늑대가 귀엽다 고 생각하다

    print("Test 3:", advanced_translate_logic("I go to the store"))
    # Result: 나는 가게를 가다
else:
    words = input("Words: ")
    final = advanced_translate_logic(words)
    print(final)