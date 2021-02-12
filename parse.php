<?php
/*
    Project IPP 2021, parser.
    Author: Yehor Pohrebniak
    Login: xpohre00
    Date: 11.02.2021
*/

//for displays errors codes with exit
ini_set('display_errors', 'stderr');

abstract class Errors {
    const INVALID_ARGUMENTS = 10;
    const ERROR_CODE_HEAD = 21;
    const ERROR_OPCODE = 22; 
    const _ERROR_LEXICAL_SYNT = 23; 
}

// Arguments process
$longopt = array("help");
$options = getopt(NULL, $longopt);
//var_dump($options);

//Arguments check
if ( (array_key_exists("help", $options) && $argc > 2) ||
    (empty($options) && $argc > 1) ) {
    exit(Errors::INVALID_ARGUMENTS);
}



/*
end of file parse.php
*/
?>