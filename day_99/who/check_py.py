import sys

with open(sys.argv[1]) as f:
    code = f.readlines()
    print(len(code))
