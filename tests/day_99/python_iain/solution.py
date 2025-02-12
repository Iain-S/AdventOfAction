from pathlib import Path

num = int(Path("input.txt").read_text())
print(num * 2)
print(num * 3)
