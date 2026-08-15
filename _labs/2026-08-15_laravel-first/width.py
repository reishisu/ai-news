import sys, unicodedata
def w(s):
    n=0
    for ch in s:
        if unicodedata.combining(ch): continue
        n += 2 if unicodedata.east_asian_width(ch) in ('W','F') else 1
    return n
mx=0
for line in open(sys.argv[1], encoding='utf-8'):
    line=line.rstrip('\n')
    c=w(line); mx=max(mx,c)
    print(f"{c:3d}|{line}")
print(f"--- max display width = {mx} (limit 40)")
