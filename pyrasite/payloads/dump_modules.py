import sys

for name in sorted(sys.modules):
    print(f'{name}: {sys.modules[name]}')
