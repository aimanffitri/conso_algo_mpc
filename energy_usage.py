import energyusage
import os

def microapp():
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

energyusage.evaluate(microapp, 40, pdf=True)