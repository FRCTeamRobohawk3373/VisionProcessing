import sys


def listOfDicts2List(dictList, valueName):
    return [d[valueName] for d in dictList if valueName in d]


def listOfDicts2Dict(dictList, keyName, valueName):
    output = {}
    for item in dictList:
        output[item[keyName]] = item[valueName]
    return output


def filterList(inputlist, listOfValues, inclusive=False):
    output = []
    if inclusive:
        for item in inputlist:
            if(item in listOfValues):
                output.append(item)
    else:
        for item in inputlist:
            if(item not in listOfValues):
                output.append(item)
    if(len(output) > 0):
        return output
    else:
        return None


def filterDict(input, names, inclusive=False):
    item = {}
    for k, v in input.items():
        if(inclusive):
            if(k in names):
                item[k] = v
        else:
            if(k not in names):
                item[k] = v
    return item


def filterListOfDicts(input, names, inclusive=False):
    output = []
    for i in input:
        item = {}
        for k, v in i.items():
            if(inclusive):
                if(k in names):
                    item[k] = v
            else:
                if(k not in names):
                    item[k] = v
        output.append(item)
    return output


def removeStrFromList(inputList, searchString):
    for i in inputList:
        if(searchString in i):
            inputList.remove(i)
            return inputList
    return inputList


def renameStrFromList(inputList, oldString, newString):
    for i, s in enumerate(inputList):
        if(oldString in s):
            print(s, file=sys.stdout)
            s = s.replace(oldString, newString)
            inputList[i] = s
            return inputList
    return inputList

    i = inputList.index(oldString)
    inputList[i] = newString
    return inputList
