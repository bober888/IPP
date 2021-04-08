"""
IPP project part 2 VUT FIT 2021. Interpret.py
Author: Yehro Pohrebniak
Login: xpohre00
Date: 06.04.2021
"""
#Librarries
import sys
import re
import xml.etree.ElementTree as ET

#Class with errors codes
class Errors:
    def invalidXMLFormat():
        return 31
    def unexpectedXML():
        return 32
    def invalidArguments():
        return 10
    def notPossibleOpenInputFile():
        return 11
    def notPossibleOpenOutputFile():
        return 12

#Function for argument parsing
def argumentParse():
    arguments = sys.argv[1:] 
    argumentsLen = len(arguments)
    sourceFile = False
    inputFile = False
    for argument in arguments:
        if (argumentsLen < 2 and "--help" in arguments):
            print("Usage: python3.8 interpret.py --input=file --source=file")
            sys.exit(0)
        elif (re.match(r"^--source=", argument)):
            sourceFile = argument.split("=")[1]
            if not sourceFile:
                sys.exit(Errors.invalidArguments())
        elif (re.match(r"^--input=", argument)):
            inputFile = argument.split("=")[1]
            if not inputFile:
                sys.exit(Errors.invalidArguments())
        else:
            sys.exit(Errors.invalidArguments())
    
    if not(sourceFile) and not(inputFile):
        sys.exit(Errors.invalidArguments())
    
    return sourceFile, inputFile

#checks XML header
def checkHeader(header):
    keyList = ["language", "name", "description"]
    try:
        if header["language"] != "IPPcode21":
            sys.exit(Errors.unexpectedXML())
    except:
            sys.exit(Errors.unexpectedXML())

    for key in header.keys():
        if key not in keyList:
            sys.exit(Errors.unexpectedXML())

#Generating list with operands and opcodes in format [order opcode (arg, type, text), (arg, type, text), (arg, type, text)], checks syntax
def checkChilds(root):
    for child in root:
        #first childs of root must be with tag instruction
        if child.tag != "instruction":
            sys.exit(Errors.unexpectedXML())
    
    InstrList = []
    oneInstList = []
    for child in root.iterfind(".//"):
        #generating list with instructions
        if child.tag == "instruction":
            if child.items()[0][0] == "order" and child.items()[1][0] == "opcode":
                if oneInstList:
                    InstrList.append(oneInstList)
                    oneInstList = []

                oneInstList.append(child.items()[0][1])
                oneInstList.append(child.items()[1][1])
                continue
            else:
                sys.exit(Errors.unexpectedXML())
            
        if child.items()[0][0] == "type" and re.match(r"^arg([0-9])+", child.tag):
            #checks if XML syntax is correct
            oneInstList.append((child.tag[3:], child.items()[0][1], child.text))
        else:
            sys.exit(Errors.unexpectedXML())

    InstrList.append(oneInstList)
    numberList = []
    for x in InstrList:
        #order must be >= 0
        if int(x[0]) < 0:
            sys.exit(Errors.unexpectedXML())

        #checks if numbers are not duplicates
        if x[0] not in numberList:
            numberList.append(x[0])
        else:
            sys.exit(Errors.unexpectedXML())

        #sorting arguments in list
        
        x[2:] = sorted(x[2:], key=lambda y: int(y[0]))

    InstrList = sorted(InstrList, key=lambda x: int(x[0]))
    return InstrList

#parsing XMLi input
def XMLParse(file):
    try:
        #checking XML format
        if file:
            #if file is exist
            tree = ET.parse(file)
            root = tree.getroot()
        else:
            #if stdin
            stringXML = ""
            for line in sys.stdin:
                stringXML += line
            root = ET.fromstring(stringXML)
    except IOError:
        sys.exit(Errors.notPossibleOpenInputFile())
    except:
        #invalid XMLformat
        sys.exit(Errors.invalidXMLFormat())
     
    
    checkHeader(root.attrib)
    InstrList = checkChilds(root)

#main function
def main():
    sourceFile, inputFile = argumentParse()
    XMLParse(sourceFile)
    print("Program success")
    sys.exit(0)

#calling main function
if __name__ == "__main__":
    main()

"""
end of file interpret.py
"""