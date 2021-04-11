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

#parse instructions
def parse(instruction):
    #constants
    var = r"^(GF|TF|LF)@(\_|\?|\-|\\$|\&|\%|\*|\!|[A-Z]|[a-z])+(\_|\?|\-|\\$|\&|\%|\*|\!|[A-Z]|[a-z]|[0-9])*$" #ok
    tbool = r"^(true|false)$" #ok
    tnil = r"^nil$" #ok
    tint = r"^(\-|\+)?[0-9]+$" #ok
    tstring = r"^([^#\s\\]|(\\\d{3}))+$" #ok
    symb = "((" + var + ")|(" + tbool + ")|(" + tnil + ")|(" + tint + ")|(" + tstring + "))"  #ok
    label = r"^(\_|\?|\-|\\$|\&|\%|\*|\!|[A-Z]|[a-z])+(\_|\?|\-|\\$|\&|\%|\*|\!|[A-Z]|[a-z]|[0-9])*$" #ok
    ttype = r"^(int|string|bool)$"  #??
    symbList = ["var", "bool", "nil", "int", "string"]
    
    instr = {
        "MOVE": ["var", "symb"],
        "CREATEFRAME": [],
        "PUSHFRAME": [],
        "POPFRAME": [],
        "DEFVAR": ["var"],
        "CALL": ["label"],
        "RETURN": [],
        "PUSHS": ["symb"],
        "POPS": ["var"],
        "ADD": ["var", "symb", "symb"],
        "SUB": ["var", "symb", "symb"],
        "MUL": ["var", "symb", "symb"],
        "IDIV": ["var", "symb", "symb"],
        "LT": ["var", "symb", "symb"],
        "EQ": ["var", "symb", "symb"],
        "GT": ["var", "symb", "symb"],
        "AND": ["var", "symb", "symb"],
        "OR": ["var", "symb", "symb"],
        "NOT": ["var", "symb"],
        "INT2CHAR": ["var", "symb"],
        "STRI2INT": ["var", "symb", "symb"],
        "READ": ["var", "type"],
        "WRITE": ["symb"],
        "CONCAT": ["var", "symb", "symb"],
        "STRLEN": ["var", "symb"],
        "GETCHAR": ["var", "symb", "symb"],
        "SETCHAR": ["var", "symb", "symb"],
        "TYPE": ["var", "symb"],
        "LABEL": ["label"],
        "JUMP": ["label"],
        "JUMPIFEQ": ["label", "symb", "symb"],
        "JUMPIFNEQ": ["label", "symb", "symb"],
        "EXIT": ["symb"],
        "DPRINT": ["symb"],
        "BREAK": [],
    }

    #If instruction is exist
    try:
        operands = instr[instruction[0].upper()]
    except:
        sys.exit(Errors.unexpectedXML())

    operandNumber = 1
    for operand in operands:
        if operand == "var":

            if instruction[operandNumber][1] != "var" or not(re.match(var, instruction[operandNumber][2])):
                sys.exit(Errors.unexpectedXML())
        
        elif operand == "symb":
            if instruction[operandNumber][1] not in symbList:
                sys.exit(Errors.unexpectedXML())
            if (instruction[operandNumber][2] != None) and instruction[operandNumber][1] == "string":
                if not(re.match(symb, instruction[operandNumber][2])):
                    sys.exit(Errors.unexpectedXML())

        elif operand == "label":
            if instruction[operandNumber][1] != "label" or not(re.match(label, instruction[operandNumber][2])):
                sys.exit(Errors.unexpectedXML())
        
        elif operand == "type":
            if instruction[operandNumber][1] != "type" or not(re.match(ttype, instruction[operandNumber][2])):
                sys.exit(Errors.unexpectedXML())

        operandNumber += 1
    
    #if operands more the need
    errorFlag = False
    try:
        instruction[operandNumber] = 1
        errorFlag = True
    except:
        pass

    if errorFlag:
        sys.exit(Errors.unexpectedXML())
    

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
    numberTypeList = []
    for child in root.iterfind(".//"):
        #generating list with instructions
        if child.tag == "instruction":
            numberTypeList = []
            if child.items()[0][0] == "order" and child.items()[1][0] == "opcode":
                if oneInstList:
                    InstrList.append(oneInstList)
                    oneInstList = []

                oneInstList.append(child.items()[0][1])
                oneInstList.append(child.items()[1][1])
                continue
            else:
                sys.exit(Errors.unexpectedXML())
            
        if child.items()[0][0] == "type" and re.match(r"^arg([123])", child.tag):
            #checks if XML syntax is correct
            if child.tag[3:] in numberTypeList:
                sys.exit(Errors.unexpectedXML())
            numberTypeList.append(child.tag[3:])
            oneInstList.append((child.tag[3:], child.items()[0][1], child.text))
        else:
            sys.exit(Errors.unexpectedXML())

    InstrList.append(oneInstList)
    numberList = []
    for x in InstrList:
    #adding instructions to one list
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
    return checkChilds(root)

#main function
def main():
    sourceFile, inputFile = argumentParse()
    instrList = XMLParse(sourceFile)
    for instruction in instrList:
        parse(instruction[1:])

    print("Program success")
    sys.exit(0)

#calling main function
if __name__ == "__main__":
    main()

"""
end of file interpret.py
"""