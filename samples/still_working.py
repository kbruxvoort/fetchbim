import time
import random

count = 1
while True:
    if count % 10:
        print("Hi Brad")
    else:
        print("Still working")
    time.sleep(5)
    count += 1
