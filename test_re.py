import re
print(re.sub(r"[^\w\-\. ]", "_", "file_name_ó.txt", flags=re.ASCII))
