from codecarbon import EmissionsTracker
import os
tracker = EmissionsTracker()
tracker.start()

print("test")
a = 2
b = 1
c = a + b
i=0
while i < 10:
    a *= c
    i += 1

print(a)
print("c=" + str(c))
#os.system("python microapp.py")
emissions = tracker.stop()