def transformNumber(oriNumber):
    import re
    number_re=re.compile('^[0-9]?$')
    oriNumber=oriNumber.replace('元','')
    oriNumber=oriNumber.replace('人','')
    tempNumber=""
    tempWord=""
    result=0
    for Numberchar in oriNumber:
        if len(number_re.findall(Numberchar))>0:
            if len(tempWord)>0:
                result=result+getRealValue(tempNumber,tempWord)
                tempNumber=""
                tempWord=""
            tempNumber=tempNumber+Numberchar
        else:
            tempWord=tempWord+Numberchar
    if len(tempNumber)>0:
        result=result+getRealValue(tempNumber,tempWord)
    if result>0:
        return str(result)
    else:
        return ""

def getRealValue(number,word):
    number=int(number)
    if word=="十":
        return number*10
    elif word=="百":
        return number*100
    elif word=="千":
        return number*1000
    elif word=="萬":
        return number*10000        
    elif word=="十萬":
        return number*100000
    elif word=="百萬":
        return number*1000000
    elif word=="千萬":
        return number*10000000
    elif word=="億":
        return number*100000000
    elif word=="十億":
        return number*1000000000
    elif word=="百億":
        return number*10000000000
    elif word=="千億":
        return number*100000000000
    elif word=="兆":
        return number*1000000000000
    elif word=="十兆":
        return number*10000000000000
    elif word=="百兆":
        return number*100000000000000
    elif word=="千兆":
        return number*1000000000000000
    else:
        return number