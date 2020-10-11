import re

def normsp(s, left=True, right=True):
    if left:
        s = re.sub(r"^[ \n\r\t\u00a0]+", "", s)
    if right:
        s = re.sub(r"[ \n\r\t\u00a0]+$", "", s)
    s = re.sub(r"[ \n\r\t\u00a0]+", " ", s)
    return s
