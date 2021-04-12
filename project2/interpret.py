"""
IPP project part 2 VUT FIT 2021. Interpret.py
Author: Yehor Pohrebniak
Login: xpohre00
Date: 06.04.2021
"""
#Librarries
import sys
import re
import xml.etree.ElementTree as ET
import fileinput

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
    
    def isExist(self, name):
        if self.name == name:
            return True
        else:
            return False

    #Function which ckecks if object in list is exists
    def labelExist(labelList, name):
        for el in labelList:
            if el.isExist(name):
                return True
        return False

    def labelIdx(labelList, name):
        for el in labelList:
            if el.isExist(name):
                return el.idx
            else:
                return -1

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
        if type1 == "int":
            self.value = int(value)
        elif type1 == "string":
            self.value = value
        elif type1 == "bool":
            if value == "false":
                self.value == False
            else:
                self.value = True
        elif type1 == "nil":
            self.value = None
        
        self.varType = type1

#class for program interpretation
class program:
    #attributes
    #input file
    inputFile = None
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
    #stack for values in for (type, value)
    stackValue = []
    #stackCall
    stackCall = []
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

   #sets input file if it exist 
    def setInputFile(self, filename):
        try:
            self.inputFile = open(filename)
        except:
            sys.exit(Errors.notPossibleOpenInputFile())
    #Function read instructions and calls theirs functions
    def readInstructions(self, instrList):
        countInstr = len(instrList)
        while True:
            if self.actualIdx == countInstr:
                break #CHANGE TO RETURN
            instrName = instrList[self.actualIdx][1]
            operands = instrList[self.actualIdx][2:]
            
            methodToCall = getattr(program, instrName.upper())
            methodToCall(self, operands)
        #debuf DELETE BEFORE DEADLINE

    def typeWithValue(self, operand): #returns (type, value) of operand
        if operand[1] == "var":
            firOperand = self.varObj(operand[2])
            if firOperand != None:
                return (firOperand.varType, firOperand.value)
            else:
                sys.exit(Errors.nonExistingVariable())
        
        elif operand[1] == "int":
            return ("int", int(operand[2]))
        
        elif operand[1] == "string":
            return ("string", operand[2])
        
        elif operand[1] == "bool":
            if operand[2].upper() == "TRUE":
                boolValue = True
            elif operand[2].upper() == "FALSE":
                boolValue = False
            return ("bool", boolValue)
        
        elif operand[1] == "nil":
            return ("nil", None)
    
    #returns object if it exist
    def varObj(self, varName):
        if varName == None:
            return None
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
        self.localFrame = self.stackFrame[-1]
        self.temporaryFrameFlag = False
        self.temporaryFrame = []
        self.localFrameFlag = True

    def POPFRAME(self, operand):
        self.actualIdx += 1
        if self.stackFrame:
            self.temporaryFrame = (self.stackFrame.pop()).copy()
            self.temporaryFrameFlag = True

            if self.stackFrame:
                self.localFrame = self.stackFrame[-1]
            else:
                self.localFrame = []
                self.localFrameFlag = False
        else:
            sys.exit(Errors.nonExistingFrame())
    
    def CALL(self, operand):
        self.stackCall.append(self.actualIdx + 1)
        nextIdx = label.labelExist(self.labelList, operand[0][2])
        if  nextIdx != -1:
            self.actualIdx = nextIdx

    def RETURN(self, operand):
        if self.stackCall:
            self.actualIdx = self.stackCall.pop()
        else:
            sys.exit(Errors.invalidValue())

    def PUSHS(self, operand):
        self.actualIdx += 1
        obj = self.varObj(operand[0][2])

        if (obj == None) and (operand[0][1] != "var"): #int|bool|string|nil
            self.stackValue.append((operand[0][1], operand[0][2]))
        elif obj != None:
            self.stackValue.append((obj.varType, obj.value))
        else:
            sys.exit(Errors.nonExistingVariable())

    def POPS(self, operand):
        self.actualIdx += 1
        obj = self.varObj(operand[0][2])
        if self.stackValue:
            if obj != None:
                move = self.stackValue.pop()
                obj.moveValue(move[0], move[1])
            else:
                sys.exit(Errors.nonExistingVariable())
        else:
            sys.exit(Errors.invalidValue())
    
    def ADD(self, operand):
        self.actualIdx += 1
        destObj = self.varObj(operand[0][2])

        if destObj != None:
            firstOper = self.typeWithValue(operand[1])
            secondOper = self.typeWithValue(operand[2])
            
            if firstOper[0] == "int" and secondOper[0] == "int":
                destObj.value = firstOper[1] + secondOper[1]
                destObj.varType = "int"
            else:
                sys.exit(Errors.invalidOperands())

        else:
            sys.exit(Errors.nonExistingVariable())
    
    def SUB(self, operand):
        self.actualIdx += 1
        destObj = self.varObj(operand[0][2])

        if destObj != None:
            firstOper = self.typeWithValue(operand[1])
            secondOper = self.typeWithValue(operand[2])
            
            if firstOper[0] == "int" and secondOper[0] == "int":
                destObj.value = firstOper[1] - secondOper[1]
                destObj.varType = "int"
            else:
                sys.exit(Errors.invalidOperands())

        else:
            sys.exit(Errors.nonExistingVariable())
    
    def MUL(self, operand):
        self.actualIdx += 1
        destObj = self.varObj(operand[0][2])

        if destObj != None:
            firstOper = self.typeWithValue(operand[1])
            secondOper = self.typeWithValue(operand[2])
            
            if firstOper[0] == "int" and secondOper[0] == "int":
                destObj.value = firstOper[1] * secondOper[1]
                destObj.varType = "int"
            else:
                sys.exit(Errors.invalidOperands())

        else:
            sys.exit(Errors.nonExistingVariable())
    
    def IDIV(self, operand):
        self.actualIdx += 1
        destObj = self.varObj(operand[0][2])

        if destObj != None:
            firstOper = self.typeWithValue(operand[1])
            secondOper = self.typeWithValue(operand[2])
            
            if firstOper[0] == "int" and secondOper[0] == "int":
                if secondOper[1] == 0:
                    sys.exit(Errors.badValueOperand())
                destObj.value = firstOper[1] // secondOper[1]
                destObj.varType = "int"
            else:
                sys.exit(Errors.invalidOperands())

        else:
            sys.exit(Errors.nonExistingVariable())
        
    def LT(self, operand):
        self.actualIdx += 1
        destObj = self.varObj(operand[0][2])

        if destObj != None:
            firstOper = self.typeWithValue(operand[1])
            secondOper = self.typeWithValue(operand[2])
            
            if firstOper[0] == secondOper[0] and firstOper[0] != "nil":
                destObj.value = firstOper[1] < secondOper[1]
                destObj.varType = "bool"
            else:
                sys.exit(Errors.invalidOperands())
            
        else:
            sys.exit(Errors.nonExistingVariable())

    def GT(self, operand):
        self.actualIdx += 1
        destObj = self.varObj(operand[0][2])

        if destObj != None:
            firstOper = self.typeWithValue(operand[1])
            secondOper = self.typeWithValue(operand[2])
            
            if firstOper[0] == secondOper[0] and firstOper[0] != "nil":
                destObj.value = firstOper[1] > secondOper[1]
                destObj.varType = "bool"
            else:
                sys.exit(Errors.invalidOperands())
            
        else:
            sys.exit(Errors.nonExistingVariable())
    
    def EQ(self, operand):
        self.actualIdx += 1
        destObj = self.varObj(operand[0][2])

        if destObj != None:
            firstOper = self.typeWithValue(operand[1])
            secondOper = self.typeWithValue(operand[2])
            
            if firstOper[0] == secondOper[0] or firstOper[0] == "nil" or secondOper[0] == "nil":
                if firstOper[0] != "nil" and secondOper[0] == "nil":
                    destObj.value = False
                elif firstOper[0] == "nil" and secondOper[0] != "nil":
                    destObj.value = False
                else:
                    destObj.value = firstOper[1] == secondOper[1]
            else:
                sys.exit(Errors.invalidOperands())

            destObj.varType = "bool"
        else:
            sys.exit(Errors.nonExistingVariable())
        
    def AND(self, operand):
        self.actualIdx += 1
        destObj = self.varObj(operand[0][2])

        if destObj != None:
            firstOper = self.typeWithValue(operand[1])
            secondOper = self.typeWithValue(operand[2])
            
            if firstOper[0] == secondOper[0] and firstOper[0] == "bool":
                destObj.value = firstOper[1] and secondOper[1]
            else:
                sys.exit(Errors.invalidOperands())

            destObj.varType = "bool"
        else:
            sys.exit(Errors.nonExistingVariable())

    def OR(self, operand):
        self.actualIdx += 1
        destObj = self.varObj(operand[0][2])

        if destObj != None:
            firstOper = self.typeWithValue(operand[1])
            secondOper = self.typeWithValue(operand[2])
            
            if firstOper[0] == secondOper[0] and firstOper[0] == "bool":
                destObj.value = firstOper[1] or secondOper[1]
            else:
                sys.exit(Errors.invalidOperands())

            destObj.varType = "bool"
        else:
            sys.exit(Errors.nonExistingVariable())
    
    def NOT(self, operand):
        self.actualIdx += 1
        destObj = self.varObj(operand[0][2])

        if destObj != None:
            firstOper = self.typeWithValue(operand[1])
            
            if firstOper[0] == "bool":
                destObj.value = not(firstOper[1])
            else:
                sys.exit(Errors.invalidOperands())

            destObj.varType = "bool"
        else:
            sys.exit(Errors.nonExistingVariable())
    
    def INT2CHAR(self, operand):
        self.actualIdx += 1
        destObj = self.varObj(operand[0][2])

        if destObj != None:
            firstOper = self.typeWithValue(operand[1])
            
            if firstOper[0] == "int":
                try:
                    destObj.value = chr(firstOper[1])
                except:
                    sys.exit(Errors.stringError())
            else:
                sys.exit(Errors.invalidOperands())

            destObj.varType = "string"
        else:
            sys.exit(Errors.nonExistingVariable())
    
    def STRI2INT(self, operand):
        self.actualIdx += 1
        destObj = self.varObj(operand[0][2])

        if destObj != None:
            firstOper = self.typeWithValue(operand[1])
            secondOper = self.typeWithValue(operand[2])
            if secondOper[0] == "int" and firstOper[0] == "string":
                try:
                    symbToOrd = firstOper[1][secondOper[1]]
                    destObj.value = ord(symbToOrd)
                except:
                    sys.exit(Errors.stringError())
            else:
                sys.exit(Errors.invalidOperands())

            destObj.varType = "string"
        else:
            sys.exit(Errors.nonExistingVariable())
    
    def READ(self, operand):
        self.actualIdx += 1
        destObj = self.varObj(operand[0][2])
        typeToRead = operand[1][2]
        if destObj != None:
            if self.inputFile != None:
                try:
                    inputStr = self.inputFile.readline()
                except:
                    sys.exit(Errors.notPossibleOpenInputFile())
            else:
                inputStr = input()

            if inputStr == None:
                dest.Obj.value = None
                dest.Obj.varType = "nil"
            elif typeToRead == "int":
                try:
                    destObj.value = int(inputStr)
                    destObj.varType = "int"
                except:
                    dest.Obj.value = None
                    dest.Obj.varType = "nil"
            elif typeToRead == "bool":

                if inputStr.lower() == "true":
                    destObj.value = True
                else:
                    destObj.value = False
                destObj.varType = "bool"

            elif typeToRead == "string":
                destObj.value = inputStr
                destObj.varType = "string"
            else:
                sys.exit(Errors.invalidOperands())
        else:
            sys.exit(Errors.nonExistingVariable())
    
    def WRITE(self, operand):
        self.actualIdx += 1
        destObj = self.typeWithValue(operand[0])
        if destObj[0] == "string":
            if destObj[1] == None:
                print("")
            outPut = destObj[1]
            outPut = re.sub(r"\\([0-9]{3})", lambda x: chr(int(x[1])), outPut)
            print(outPut)
        elif destObj[0] == "bool":
            if destObj[1]:
                print("true", end="")
            else:
                print("false", end="")
        elif destObj[0] == "nil":
            print(end="")
        else:
            print(destObj[1])
        
    def CONCAT(self, operand):
        self.actualIdx += 1
        destObj = self.varObj(operand[0][2])
        
        if destObj != None:
            firstOper = self.typeWithValue(operand[1])
            secondOper = self.typeWithValue(operand[2])

            if firstOper[0] == secondOper[0] and firstOper[0] == "string":
                destObj.value = firstOper[1] + secondOper[1]
                destObj.varType = "string"
            else:
                sys.exit(Errors.invalidOperands())
            
        else:
            sys.exit(Errors.nonExistingVariable())

    def STRLEN(self, operand):
        self.actualIdx += 1
        destObj = self.varObj(operand[0][2])
        
        if destObj != None:
            firstOper = self.typeWithValue(operand[1])
            
            if firstOper[0] == "string":
                destObj.value = len(firstOper[1])    
                destObj.varType = "int"
            else:
                sys.exit(Errors.invalidOperands())
            
        else:
            sys.exit(Errors.nonExistingVariable())

    def GETCHAR(self, operand):
        self.actualIdx += 1
        destObj = self.varObj(operand[0][2])
        
        if destObj != None:
            firstOper = self.typeWithValue(operand[1])
            secondOper = self.typeWithValue(operand[2])

            if secondOper[0] == "int" and firstOper[0] == "string":
                try:
                    destObj.value = firstOper[1][secondOper[1]]
                except:
                    sys.exit(Errors.stringError())

                destObj.varType = "string"
            else:
                sys.exit(Errors.invalidOperands())
            
        else:
            sys.exit(Errors.nonExistingVariable())
    
    def SETCHAR(self, operand):
        self.actualIdx += 1
        destObj = self.varObj(operand[0][2])
        
        if destObj != None:
            firstOper = self.typeWithValue(operand[1])
            secondOper = self.typeWithValue(operand[2])
            
            if secondOper[0] == "string" and firstOper[0] == "int" and destObj.varType == "string":
                try:
                    idx = firstOper[1]
                    strToChange = destObj.value
                    destObj.value = "".join((strToChange[:idx], secondOper[1][0], strToChange[idx+1:]))
                    
                except:
                    sys.exit(Errors.stringError())

                destObj.varType = "string"
            else:
                sys.exit(Errors.invalidOperands())
            
        else:
            sys.exit(Errors.nonExistingVariable())

    def TYPE(self, operand):
        self.actualIdx += 1 
        destObj = self.varObj(operand[0][2])
        srcObj = False
        firstOper = False
        nilFlag = False

        if operand[1][1] == "var":
            srcObj = self.varObj(operand[1][2])
            if srcObj == None:
                nilFlag = True
        else:
            firstOper = self.typeWithValue(operand[1])

        if destObj != None:
            if firstOper:
                destObj.value = firstOper[0]
                destObj.varType = "string"
            elif nilFlag:
                destObj.value = "nil"
                destObj.varType = "string"
            else:
                destObj.value = srcObj.varType
                destObj.varType = "string"
        else:
            sys.exit(Errors.nonExistingVariable())
        
    def LABEL(self, operand):
        self.actualIdx += 1
    
    def JUMP(self, operand):
        idx = label.labelIdx(self.labelList, operand[0][2])
        if idx == -1:
            sys.exit(Errors.semError())
        self.actualIdx = idx
    
    def JUMPIFEQ(self, operand):
        firstOper = self.typeWithValue(operand[1])
        secondOper = self.typeWithValue(operand[2])

        if secondOper[0] == firstOper[0]:
            if secondOper[1] == firstOper[1]:
                idx = label.labelIdx(self.labelList, operand[0][2])
                if idx == -1:
                    sys.exit(Errors.semError())
                self.actualIdx = idx
        elif secondOper[0] == "nil" or firstOper[0] == "nil":
            pass
        else:
            sys.exit(Errors.invalidOperands())

    def JUMPIFNEQ(self, operand):
        firstOper = self.typeWithValue(operand[1])
        secondOper = self.typeWithValue(operand[2])
        idx = label.labelIdx(self.labelList, operand[0][2])
        if idx == -1:
            sys.exit(Errors.semError())

        if secondOper[0] == firstOper[0]:
            if secondOper[1] != firstOper[1]:
                self.actualIdx = idx
        elif secondOper[0] == "nil" or firstOper[0] == "nil":
            self.actualIdx = idx
        else:
            sys.exit(Errors.invalidOperands())

    def EXIT(self, operand):
        self.actualIdx += 1
        firstOper = self.typeWithValue(operand[0])
        if firstOper[0] == "int":
            if firstOper[1] >= 0 and firstOper[1] <=49:
                sys.exit(firstOper[1])
            else:
                sys.exit(Errors.badValueOperand())
        else:
            sys.exit(Errors.invalidOperands())

    def DPRINT(self, operand):
        self.actualIdx += 1

        firstOper = self.typeWithValue(operand[0])
        if firstOper[0] == "nil":
            print("nil", file=sys.stderr)
        elif firstOper[0] == "bool":
            if firstOper[1] == True:
                print("true", file=sys.stderr)
            else:
                print("false", file=sys.stderr)
        elif firstOper[0] == "string":
            if firstOper[1] == None:
                print("")
            outPut = firstOper[1]
            outPut = re.sub(r"\\([0-9]{3})", lambda x: chr(int(x[1])), outPut)
            print(outPut)
        else:
            print(str(firstOper[0]), file=sys.stderr)

    def BREAK(self, operand):
        self.actualIdx += 1
        print("LF:")
        for el in self.localFrame:
            print(el.name, el.value, el.varType)
        print("GF:")
        for el in self.gloablFrame:
            print(el.name, el.value, el.varType)
        print("TF:")
        for el in self.temporaryFrame:
            print(el.name, el.value, el.varType)
        print("Instruction order:", self.actualIdx)
        print("Labels:")
        for el in self.labelList:
            print(el.name, "indx:", el.idx)

#interpret
def interpret(instrList, inputFile):
    programIPP21 = program(instrList)
    if inputFile:
        programIPP21.setInputFile(inputFile)
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
           
            if (instruction[operandNumber][1] == "int") and re.match(tint, instruction[operandNumber][2]):
                pass
            elif (instruction[operandNumber][1] == "bool") and re.match(tbool, instruction[operandNumber][2]):
                pass
            elif (instruction[operandNumber][1] == "nil") and re.match(tnil, instruction[operandNumber][2]):
                pass
            elif (instruction[operandNumber][1] == "string") and (instruction[operandNumber][2] != None) and re.match(tstring, instruction[operandNumber][2]):
                pass
            elif (instruction[operandNumber][1] == "var") and re.match(var, instruction[operandNumber][2]):
                pass
            elif (instruction[operandNumber][1] == "string") and (instruction[operandNumber][2] == None):
                pass
            else:
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
        if not(x[0].isdigit()) or int(x[0]) <= 0:
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

    interpret(instrList, inputFile)
    sys.exit(0)

#calling main function
if __name__ == "__main__":
    main()

"""
end of file interpret.py
"""