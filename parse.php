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
    const _ERROR_LEXICAL_SYNT = 23; 
}

class patterns {
    private const
        comment = "\s*(#(.)*)?$/",
        tbool = "bool@(true|false)",
        tnil = "nil@nil",
        tint = "int@\-?[0-9]+",
        tstring = "string@(|(\\\\\d{3})|[^#\\\\\"\s])+",
        var1 = "\s+(GF|TF|LF)@(\_|\?|\-|\\$|\&|\%|\\*|\!|[A-z])+(\_|\?|\-|\\$|\&|\%|\\*|\!|[A-z]|[0-9])*",
        symb = "\s+((" . self::var1 . ")|(" . self::tbool . ")|(" . self::tnil . ")|(" . self::tstring . ")|(" . self::tint . "))",
        label = "\s+(\_|\?|\-|\\$|\&|\%|\\*|\!|[A-z])+(\_|\?|\-|\\$|\&|\%|\\*|\!|[A-z]|[0-9])*";

    private const instructions = [
        "(?i)MOVE(?-i)" => ["var", "symb"],
        "(?i)CREATEFRAME(?-i)" => [],
        "(?i)PUSHFRAME(?-i)" => [],
        "(?i)POPFRAME(?-i)" => [],
        "(?i)DEFVAR(?-i)" => ["var"],
        "(?i)CALL(?-i)" => ["label"],
        "(?i)RETURN(?-i)" => [],
    ];

    public function parser($string) {
        
        foreach(self::instructions as $instruction => $oprts) {
            $pattern = "";
            $pattern = "/^" . $instruction;
            
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
                    default:
                        break;
                }
            }

            $pattern .= self::comment;
    
            if(preg_match($pattern, $string)) {
                return true;
            }
        }
        return false;
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
        } else if (!$headerFlag) {
            exit(Errors::ERROR_CODE_HEAD);
        }

        
        if(patterns::parser($str)){
            echo "line succ\n";
        } else {
            echo "line notsucc\n", $str;
        }
        //Clear string
        $str = "";
    }
}
/*
end of file parse.php
*/
?>