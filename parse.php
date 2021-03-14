<?php
/*
    Project IPP 2021, parser.
    Author: Yehor Pohrebniak
    Login: xpohre00
    Date: 11.02.2021
*/

//for displays errors codes with exit
ini_set("display_errors", "stderr");

//Help message(--help)
const HelpText = "Script with type of filtr, will read program code implemented IPPcode21 from the standart input."
                  ."Controls lexical and syntatic rightness and writes to output XML representation of program.\n"
                  ."Usage parse.php [OPTIONS] <inputfile.IPPcode21\n";

//Codes for error exits
abstract class Errors {
    const INVALID_ARGUMENTS = 10;
    const ERROR_CODE_HEAD = 21;
    const ERROR_OPCODE = 22; 
    const ERROR_LEXICAL_SYNT = 23; 
}

//Function convert string to XML format(changes some symbols to XML format)
function convertStringToXML($string) {
    $string = str_replace(array("&"), array("&amp;"), $string);
    $searchSymb = array("\"", ">", "<", "'");
    $replaceSymb = array("&quot;", "&gt;", "&lt;", "&apos;");
    return str_replace($searchSymb, $replaceSymb, $string);
}

//class with patterns and method to check input line / generate output
class patterns {
    private const
        comment = "\s*(#(.)*)?$/",
        tbool = "\s+bool@(true|false)",
        tnil = "\s+nil@nil",
        tint = "\s+int@(\-|\+)?[0-9]+",
        tstring = "\s+string@(|(\\\\\d{3})|[^#\\\\\"\s])+",
        var1 = "\s+(GF|TF|LF)@(\_|\?|\-|\\$|\&|\%|\*|\!|[A-Z]|[a-z])+(\_|\?|\-|\\$|\&|\%|\*|\!|[A-z]|[0-9])*",
        symb = "((" . self::var1 . ")|(" . self::tbool . ")|(" . self::tnil . ")|(" . self::tstring . ")|(" . self::tint . "))",
        label = "\s+(\_|\?|\-|\\$|\&|\%|\*|\!|[A-Z]|[a-z])+(\_|\?|\-|\\$|\&|\%|\*|\!|[A-Z]|[a-z]|[0-9])*",
        type = "\s+(int|string|bool)";

    //array of instructions and theirs operands
    private const instructions = [
        "(?i)MOVE(?-i)" => ["var", "symb"],
        "(?i)CREATEFRAME(?-i)" => [],
        "(?i)PUSHFRAME(?-i)" => [],
        "(?i)POPFRAME(?-i)" => [],
        "(?i)DEFVAR(?-i)" => ["var"],
        "(?i)CALL(?-i)" => ["label"],
        "(?i)RETURN(?-i)" => [],
        "(?i)PUSHS(?-i)" => ["symb"],
        "(?i)POPS(?-i)" => ["var"],
        "(?i)ADD(?-i)" => ["var", "symb", "symb"],
        "(?i)SUB(?-i)" => ["var", "symb", "symb"],
        "(?i)MUL(?-i)" => ["var", "symb", "symb"],
        "(?i)IDIV(?-i)" => ["var", "symb", "symb"],
        "(?i)LT(?-i)" => ["var", "symb", "symb"],
        "(?i)EQ(?-i)" => ["var", "symb", "symb"],
        "(?i)GT(?-i)" => ["var", "symb", "symb"],
        "(?i)AND(?-i)" => ["var", "symb", "symb"],
        "(?i)OR(?-i)" => ["var", "symb", "symb"],
        "(?i)NOT(?-i)" => ["var", "symb"],
        "(?i)INT2CHAR(?-i)" => ["var", "symb"],
        "(?i)STRI2INT(?-i)" => ["var", "symb", "symb"],
        "(?i)READ(?-i)" => ["var", "type"],
        "(?i)WRITE(?-i)" => ["symb"],
        "(?i)CONCAT(?-i)" => ["var", "symb", "symb"],
        "(?i)STRLEN(?-i)" => ["var", "symb"],
        "(?i)GETCHAR(?-i)" => ["var", "symb", "symb"],
        "(?i)SETCHAR(?-i)" => ["var", "symb", "symb"],
        "(?i)TYPE(?-i)" => ["var", "symb"],
        "(?i)LABEL(?-i)" => ["label"],
        "(?i)JUMP(?-i)" => ["label"],
        "(?i)JUMPIFEQ(?-i)" => ["label", "symb", "symb"],
        "(?i)JUMPIFNEQ(?-i)" => ["label", "symb", "symb"],
        "(?i)EXIT(?-i)" => ["symb"],
        "(?i)DPRINT(?-i)" => ["symb"],
        "(?i)BREAK(?-i)" => [],
    ];

    //method to check line of input IPPcode21. Retuns 0 if string is successful
    public static function parser($string, $order) {
        $ErrorInstrFlag = true; //Flag for invalid instruction error

        //Loop for generating all impossible patterns
        foreach(self::instructions as $instruction => $oprts) {
            $pattern = "";
            $pattern = "/^\s*" . $instruction;
            $patternInstr = $pattern . "(\s+|$)/";
            
            //Checks if opcode is exists, if not then it returns an error 22 later
            if(preg_match($patternInstr, $string)){
                $ErrorInstrFlag = false;
            }

            //Generating pattern in format OPCODE <var> <symb>.... etc
            foreach($oprts as $oprt) {
                switch($oprt){
                    case "var":
                        $pattern .= self::var1;
                        break;
                    case "symb":
                        $pattern .= self::symb;
                        break;
                    case "label":
                        $pattern .= self::label;
                        break;
                    case "type":
                        $pattern .= self::type;
                    default:
                        break;
                }
            }

            //Adding a comment to pattern
            $pattern .= self::comment;
            
            //If string is successful
            if(preg_match($pattern, $string)) {
                //Splits input string on parts between whitespaces
                $splitted = explode(" ", trim($string, "\n"));
                //Variable for xml output
                $XMLout = "\t<instruction order=\"" . $order . "\" opcode=\"" . strtoupper($splitted[0]) . "\">\n" ;
                $argCount = 0;
                
                //Generating XMLout
                foreach($splitted as $argument) {
                    if($argCount == 0) {
                        $argCount++;
                        continue;
                    }

                    //Generating for type "var"
                    if (preg_match("/^" . substr(self::var1, 3) . "(#(.)*)?$/", $argument)) {
                        //If string is with comment on the end without spaces
                        if (strpos($argument, "#") != false) {
                            $XMLout .= "\t\t<arg" . $argCount . " type=\"var\">" . convertStringToXML(substr(trim($argument, "\n"), 0, strpos($argument, "#"))) . "</arg" . $argCount .">\n";
                        } else {
                            $XMLout .= "\t\t<arg" . $argCount . " type=\"var\">" . convertStringToXML(trim($argument, "\n")) . "</arg" . $argCount .">\n";
                        }
                        
                        $argCount++;
                    
                    //Generating for type "string"
                    } elseif (preg_match("/^" . substr(self::tstring, 3) . "(#(.)*)?$/", $argument)) {
                        
                        if (strpos($argument, "#") != false) {
                            $XMLout .= "\t\t<arg" . $argCount . " type=\"string\">" . convertStringToXML(substr(trim($argument, "\n"), 7, strpos($argument, "#") - 7)) . "</arg" . $argCount .">\n";
                        } else {
                            $XMLout .= "\t\t<arg" . $argCount . " type=\"string\">" . convertStringToXML(substr(trim($argument, "\n"), 7)) . "</arg" . $argCount .">\n";
                        }
                        
                        $argCount++;
                    
                    //If string is a comment
                    } elseif ((preg_match("/^#(.)*$/", $argument))) {
                        break;
                    
                    //Generating for type "nil"
                    } elseif (preg_match("/^" . substr(self::tnil, 3) . "(#(.)*)?$/", $argument)) { //TODO
                        $XMLout .= "\t\t<arg" . $argCount . " type=\"nil\">" . "nil" . "</arg" . $argCount .">\n";
                        $argCount++;

                    //Generating for type "type"
                    } elseif (preg_match("/^" . substr(self::type, 3) . "(#(.)*)?$/", $argument)) {

                        if (strpos($argument, "#") != false) {
                            $XMLout .= "\t\t<arg" . $argCount . " type=\"type\">" . substr(trim($argument, "\n"), 0, strpos($argument, "#")) . "</arg" . $argCount .">\n";
                        } else {
                            $XMLout .= "\t\t<arg" . $argCount . " type=\"type\">" . trim($argument, "\n") . "</arg" . $argCount .">\n";
                        }
                        
                        $argCount++;

                    //Generating for type "int"
                    } elseif(preg_match("/^" . substr(self::tint, 3) . "(#(.)*)?$/", $argument)) {
                        
                        if (strpos($argument, "#") != false) {
                            $XMLout .= "\t\t<arg" . $argCount . " type=\"int\">" . substr(trim($argument, "\n"), 4, strpos($argument, "#") - 4) . "</arg" . $argCount .">\n";
                        } else {
                            $XMLout .= "\t\t<arg" . $argCount . " type=\"int\">" . substr(trim($argument, "\n"), 4) . "</arg" . $argCount .">\n";
                        }
                        
                        $argCount++;

                    //Generating for type "bool"
                    } elseif (preg_match("/^" . substr(self::tbool, 3) . "(#(.)*)?$/", $argument)) {

                        if (strpos($argument, "#") != false) {
                            $XMLout .= "\t\t<arg" . $argCount . " type=\"bool\">" . substr(trim($argument, "\n"), 5, strpos($argument, "#") - 5) . "</arg" . $argCount .">\n";
                        } else {
                            $XMLout .= "\t\t<arg" . $argCount . " type=\"bool\">" . substr(trim($argument, "\n"), 5) . "</arg" . $argCount .">\n";
                        }

                        $argCount++;
                    
                    //Generating for type "label"
                    } elseif (preg_match("/^" . substr(self::label, 3) . "(#(.)*)?$/", $argument)) {
                        
                        if (strpos($argument, "#") != false) {
                            $XMLout .= "\t\t<arg" . $argCount . " type=\"label\">" . substr(trim($argument, "\n"), 0, strpos($argument, "#")) . "</arg" . $argCount .">\n";
                        } else {
                            $XMLout .= "\t\t<arg" . $argCount . " type=\"label\">" . trim($argument, "\n") . "</arg" . $argCount .">\n";
                        }

                        $argCount++;
                    }
                }
                
                $XMLout .= "\t</instruction>\n";
                echo $XMLout;
                return 0;
            }

        }

        if($ErrorInstrFlag) {
            return Errors::ERROR_OPCODE;
        } else {
            return Errors::ERROR_LEXICAL_SYNT;
        }
    }
}

// Arguments process
$options = getopt(NULL, array("help")); //test

//Arguments check
if ( (array_key_exists("help", $options) && $argc > 2) ||
    (empty($options) && $argc > 1) ) {
        echo "parse.php --help\n";
        exit(Errors::INVALID_ARGUMENTS);
}

//Help message out
if ( (array_key_exists("help", $options)) ) {
    echo HelpText;
    exit(0);
}

//string for parsing
$str = "";
//flag for header line
$headerFlag = false;

//Start output XML header
echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";

//variable for count instructions
$order = 1;

//reading the input
while ($str = fgets(STDIN)) {

    //Checks header
    if (!$headerFlag && preg_match("/^\s*.IPPcode21\s*(#(.)*)?$/i", $str)) {
        $headerFlag = true;
        echo "<program language=\"IPPcode21\">\n";
        continue;
    } elseif (!$headerFlag && preg_match("/^\s*#(.)*$/", $str)) { //if first line is comment
        continue;
    } elseif (preg_match("/^\s*$/", $str)) { //if line is made of whitespaces
        continue;
    }
    elseif (!$headerFlag) {
        exit(Errors::ERROR_CODE_HEAD);
    }

    //If line is command
    if (preg_match("/^\s*#(.)*$/", $str)) {
        //echo "comment\n";
        $str = "";
        continue;    
    }
        
    //Check if string correct, if not program exit
    if(patterns::parser($str, $order) == 0) {
       $order++;
    } else {
        exit(patterns::parser($str, $order));
    }    
}
echo "</program>";
if (!$headerFlag) {
    exit(Errors::ERROR_CODE_HEAD);
} else {
    exit(0);
}
/*
end of file parse.php
*/
?>