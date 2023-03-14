import re

def is_valid_hexa_code(str):
    p = re.compile("^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")
    if(str == None):
        return False
    if(re.search(p, str)):
        return True
    else:
        return False
