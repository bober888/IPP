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
    def semError():
        return 52
    def invalidOperands():
        return 53
    def nonExistingVariable():
        return 54
    def nonExistingFrame():
        return 55
    def invalidValue():
        return 56
    def badValueOperand():
        return 57
    def stringError():
        return 58

#class for labels
class label:
    # methods
    def __init__(self, name, idx):
        self.name = name
        self.idx = idx  #index in instruction list    
    
    def isExists(self, name):
        if self.name == name:
            return True
        else:
            return False

    #Function which ckecks if object in list is exists
    def labelExist(labelList, name):
        for el in labelList:
            if el.isExists(name):
                return True
        return False

#class for variables
class variable:
    #methods
    varType = None
    value = None

    #constructor for variables, name = variable name 
    def __init__(self, name):
        self.name = name

    def isExist(self, name):
        if self.name == name:
            return True
        else:
            return False
    
    def varExist(varList, name):
        for el in varList:
            if el.isExist(name):
                return True
        return False
    
    def move(self, other):
        self.value = other.value
        self.varType = other.varType
    
    def moveValue(self, type1, value):
        self.value = value
        self.varType = type1

#class for program interpretation
class program:
    #attributes
    #list for labels
    labelList = []
    #lists for variable
    #List for global variables   
    gloablFrame = []
    #list for LF
    localFrame = []
    localFrameFlag = False #True if local frame is available
    #list for TF
    temporaryFrame = []
    temporaryFrameFlag = False  #True if temporary frame is available
    #stack frames
    stackFrame = []
    #instruction order 
    actualIdx = 0
    
    #methods
    #constructor, adds labels to labelList
    def __init__(self, instrList):
        idx = 0 #index for labels
        
        for instruction in instrList:
            instruction = instruction[1:]
            #adding label to the List
            if instruction[0].upper() == "LABEL":
                labelName = instruction[1][2]
                if label.labelExist(self.labelList, labelName):
                    sys.exit(Errors.semError())
                self.labelList.append(label(labelName, idx))  

            idx += 1
    
    #Function read instructions and calls theirs functions
    def readInstructions(self, instrList):
        countInstr = len(instrList)
        while True:
            if self.actualIdx == countInstr:
                return
            instrName = instrList[self.actualIdx][1]
            operands = instrList[self.actualIdx][2:]
            
            methodToCall = getattr(program, instrName.upper())
            methodToCall(self, operands)
    
    #returns object if it exist
    def varObj(self, varName):
        frame = varName[:2]
        name = varName[3:]
        if frame == "GF":
            for obj in self.gloablFrame:
                if obj.isExist(name):
                    return obj
        elif frame == "LF":
            for obj in self.localFrame:
                if obj.isExist(name):
                    return obj
        elif frame == "TF":
            for obj in self.temporaryFrame:
                if obj.isExist(name):
                    return obj
        return None

    #return True is variable was defined
    def isDefined(self, varName):
        frame = varName[:2]
        name = varName[3:]
        if frame == "GF":
            if variable.varExist(self.gloablFrame, name):
                return True
        elif frame == "LF":
            if variable.varExist(self.localFrame, name):
                return True
        elif frame == "TF":
            if variable.varExist(self.temporaryFrame, name):  
                return True

        return False      

    def DEFVAR(self, operand):
        self.actualIdx += 1
        frame = operand[0][2][:2]
        var = operand[0][2]
        varName = var[3:]
        if self.isDefined(var):    #If variable was defined
                sys.exit(Errors.semError())
        
        if frame == "GF":
            self.gloablFrame.append(variable(varName))
        elif frame == "LF":
            if self.localFrameFlag:
                self.localFrame.append(variable(varName))
            else:
                sys.exit(Errors.nonExistingFrame())
        elif frame == "TF":
            if self.temporaryFrameFlag:
                self.temporaryFrame.append(variable(varName))
            else:
                sys.exit(Errors.nonExistingFrame())

    def MOVE(self, operand):
        self.actualIdx += 1
        destFrame = operand[0][2][:2]
        varDest = self.varObj(operand[0][2])
        srcType = operand[1][1] 

        if varDest != None:
            if srcType == "var":
                varSrc = self.varObj(operand[1][2])
                srcFrame = operand[1][2][3:]
                
                #checks if srcVar is exist
                if (srcFrame == "LF" and not(self.localFrameFlag)) or (srcFrame == "TF" and not(self.temporaryFrameFlag)):
                    sys.exit(Errors.nonExistingFrame())
                elif varSrc == None:
                    sys.exit(Errors.nonExistingVariable())

                varDest.move(varSrc)
            else:
                varDest.moveValue(srcType, operand[1][2])

        elif (destFrame == "LF" and not(self.localFrameFlag)) or (destFrame == "TF" and not(self.temporaryFrameFlag)):
            sys.exit(Errors.nonExistingFrame())
        else:
            sys.exit(Errors.nonExistingVariable())

    def CREATEFRAME(self, operand):
        self.actualIdx += 1
        self.temporaryFrame = []    #clear temporary frame
        self.temporaryFrameFlag = True  #flag must be true
    
    def PUSHFRAME(self, operand):
        self.actualIdx += 1
        if not(self.temporaryFrameFlag):
            sys.exit(Errors.nonExistingFrame())
        self.stackFrame.append(self.temporaryFrame.copy())
        self.localFrame = self.temporaryFrame.copy()
        self.temporaryFrameFlag = False
        self.temporaryFrame = []
        self.localFrameFlag = True

    def POPFRAME(self, operand):
        self.actualIdx += 1
        self.temporaryFrame


#interpret
def interpret(instrList):
    programIPP21 = program(instrList)
    programIPP21.readInstructions(instrList)
    return
    
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
        if not(x[0].isdigit()) or int(x[0]) < 0:
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

    print("Interpret starts..")
    interpret(instrList)
    print("Program success")
    sys.exit(0)

#calling main function
if __name__ == "__main__":
    main()

"""
end of file interpret.py
"""