
x = [1,2,3,4]
print(x[2:])

import Preprocessing

temp = Preprocessing.readPklFile("analysis/dict_nkey_test.pkl")
print(len(temp))
print(temp)

temp = Preprocessing.readPklFile("analysis/muldict_nkey_test.pkl")
print(len(temp))
print(temp)