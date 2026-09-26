import re
print(re.sub(r"[^\w\-\. ]", "_", "filéname.txt"))
print(re.sub(r"[^\w\-\. ]", "_", "filéname.txt", flags=re.ASCII))
