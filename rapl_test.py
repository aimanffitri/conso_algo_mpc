import pyRAPL
import os

pyRAPL.setup()

@pyRAPL.measure
def foo():
    #os.system('python microapp.py')
    print("test")
    a = 2
    b = 1
    c = a + b

    while i < 10:
        a *= c
        i += 1

    print(a)
    print("c=" + c)

foo()