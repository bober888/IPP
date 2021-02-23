<?php
/*
    Project IPP 2021, parser.
    Author: Yehor Pohrebniak
    Login: xpohre00
    Date: 11.02.2021
*/

//for displays errors codes with exit
ini_set('display_errors', 'stderr');

//Help message(--help)
const HelpText = "Script with type of filtr, will read program code implemented IPPcode21 from the standart input."
                  ."Controls lexical and syntatic rightness and writes to output XML representation of program.\n";

abstract class Errors {
    const INVALID_ARGUMENTS = 10;
    const ERROR_CODE_HEAD = 21;
    const ERROR_OPCODE = 22; 
    const ERROR_LEXICAL_SYNT = 23; 
}

class patterns {
    private const
        comment = "\s*(#(.)*)?$/",
        tbool = "\s+bool@(true|false)",
        tnil = "\s+nil@nil",
        tint = "\s+int@\-?[0-9]+",
        tstring = "\s+string@(|(\\\\\d{3})|[^#\\\\\"\s])+",
        var1 = "\s+(GF|TF|LF)@(\_|\?|\-|\\$|\&|\%|\\*|\!|[A-z])+(\_|\?|\-|\\$|\&|\%|\\*|\!|[A-z]|[0-9])*",
        symb = "((" . self::var1 . ")|(" . self::tbool . ")|(" . self::tnil . ")|(" . self::tstring . ")|(" . self::tint . "))",
        label = "\s+(\_|\?|\-|\\$|\&|\%|\\*|\!|[A-z])+(\_|\?|\-|\\$|\&|\%|\\*|\!|[A-z]|[0-9])*",
        type = "\s+(int|string|bool)";

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
        "(?i)NOT(?-i)" => ["var", "symb", "symb"],
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

    public static function parser($string) {
        $ErrorInstrFlag = true; //Flag for invalid instruction error

        foreach(self::instructions as $instruction => $oprts) {
            $pattern = "";
            $pattern = "/^" . $instruction;
            $patternInstr = $pattern . "/";
            
            if(preg_match($patternInstr, $string)){
                $ErrorInstrFlag = false;
            }

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

            $pattern .= self::comment;
            
            if(preg_match($pattern, $string)) {
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
//var_dump($options);

//Arguments check
if ( (array_key_exists("help", $options) && $argc > 2) ||
    (empty($options) && $argc > 1) ) {
        exit(Errors::INVALID_ARGUMENTS);
}


if ( (array_key_exists("help", $options)) ) {
    echo HelpText;
    exit(0);
}

//string for parsing
$str = "";
//flag for header line
$headerFlag = false;

//reading the input
while ($c = fgets(STDIN)) {
    $str .= $c;

    if ($c = "\n") {
        
        //Checks header
        if (!$headerFlag && preg_match("/^.IPPcode21\s*$/", $str)) {
            $headerFlag = true;
            $str = "";
            continue;
        } else if (!$headerFlag && preg_match("/^\s*#(.)*$/", $str)) { //if first line is comment
            $str = "";
            continue;
        } else if (!$headerFlag) {
            exit(Errors::ERROR_CODE_HEAD);
        }

        //If line is command
        if (preg_match("/^\s*#(.)*$/", $str)) {
            echo "comment\n";
            $str = "";
            continue;    
        }
        
        //Check if string correct, if not program exit
        if(patterns::parser($str) == 0) {
            echo "line succ\n";
        } else {
            print $str;
            exit(patterns::parser($str));
        }
        //Clear string
        $str = "";
    }
}
/*
end of file parse.php
*/
?>