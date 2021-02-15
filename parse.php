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
        
        if (!$headerFlag && $str == ".IPPcode21") {
            echo "kek";
            $headerFlag = true;
        } else {
            echo "err\n";
            exit(Errors::ERROR_CODE_HEAD);
        }
        $str = "";
    }
}
/*
end of file parse.php
*/
?>