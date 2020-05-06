import re

def is_dollar_amount(s):
    return re.match(r'^\$?\d[\d,]+(\.\d\d)?$',s) != None
    
def dollar_amount(s):
    if is_dollar_amount(s):
        return float(s.replace('$','').replace(',',''))
    else:
        return 0
