<?php
/*

IPP project part 2 VUT FIT 2021. test.php
Author: Yehor Pohrebniak
Login: xpohre00
Date: 06.04.2021

*/
ini_set("display_errors", "stderr");

//Help message(--help)
const helpText = "Script for automatic testing for aplication interpret.py, parse.php " .
                 "Returns HTML code for generating results of testing\n" . 
                 "Usage: php test.php [OPTINOS]\n";

//Global varnings
$directory = getcwd();
$parsefile = getcwd() . "/parse.php";
$intfile = getcwd() . "/interpret.py";
$parseOnly = false;
$intOnly = false;
$recursive = false;
$jexamxml = "/pub/courses/ipp/jexamxml/jexamxml.jar";
$jexamcfg = "/pub/courses/ipp/jexamxml/options";


abstract class Errors {
    const ERROR_PATH_OR_FILE = 41;
    const INVALID_ARGUMENTS = 10;
    const INVALID_PATH = 11;
    const ERROR_OPEN_FILE = 12;
}

// Function for parsing arguments
function argParse($argc) {
    $longopt = array(
        "help",
        "directory:",
        "recursive",
        "parse-script:",
        "int-script:",
        "parse-only",
        "int-only",
        "jexamxml:",
        "jexamcfg:"
    );

    $options = getopt(NULL, $longopt);
    $expectedargc = 1;  //need check if all arguments were correct

    if ((array_key_exists("help", $options))) {
        if ($argc == 2) {
            echo helpText;
            exit(0);
        } else {
            exit(Errors::INVALID_ARGUMENTS);
        }
    } elseif ((array_key_exists("parse-only", $options) 
              && (array_key_exists("int-script", $options) || array_key_exists("int-only", $options))
              || (array_key_exists("int-only", $options) 
              && (array_key_exists("parse-only", $options) || array_key_exists("parse-script", $options))))) {
        exit(Errors::INVALID_ARGUMENTS);
    } else {
        foreach ($options as $opt => $path) {

            $expectedargc++;    
            
            switch ($opt) {
                case "directory":
                    global $directory;
                    
                    if (!realpath($path)) {
                        exit(Errors::INVALID_PATH);
                    }
                    
                    $directory = $path;
                    break;

                case "recursive":
                    global $recursive;
                    $recursive = true;
                    break;

                case "parse-script":
                    if (!is_file($path)) {
                        exit(Errors::INVALID_PATH);
                    }

                    global $parsefile;
                    $parsefile = $path;
                    break;

                case "int-script":
                    if (!is_file($path)) {
                        exit(Errors::INVALID_PATH);
                    }

                    global $intfile;
                    $intfile = $path;
                    break;

                case "parse-only":
                    global $parseOnly;
                    $parseOnly = true;
                    break;

                case "int-only":
                    global $intOnly;
                    $intOnly = true;
                    break;

                case "jexamxml":
                    if (!is_file($path)) {
                        exit(Errors::INVALID_PATH);
                    }

                    global $jexamxml;
                    $jexamxml = $path;
                    break;

                case "jexamcfg":
                    if (!is_file($path)) {
                        exit(Errors::INVALID_PATH);
                    }

                    global $jexamcfg;
                    $jexamcfg = $path;

                    break;

                default:
                    exit(Errors::INVALID_ARGUMENTS);
            }
        }
        if ($expectedargc != $argc) {
            exit(Errors::INVALID_ARGUMENTS);
        }
    }
}

function RecDirectories($directory, &$res = array()) {
    $files = scandir($directory);

    foreach($files as $a => $file) {
        $dir = realpath($directory . "/" . $file);
        
        if (!is_dir($dir)) {
            $res[] = $dir;
        } elseif ($file != "." && $file != '..') {
            RecDirectories($dir, $res);
            $res[] = $dir; 
        }
    }

    return $res;
}

//src, in, out, rc
function test() {
    $testcounter = 0;
    $passed = 0;
    $failed = 0;
    global $intOnly;
    global $parseOnly;
    global $recursive;
    global $parsefile;
    global $intfile;
    global $directory;

    if (!realpath($directory)) {
        exit(Errors::INVALID_PATH);
    } else {
        if ($recursive) {
            $files = RecDirectories($directory);
        } else {
            $files = array();
            foreach(glob($directory . "/*.src") as $file) {
                array_push($files, $file);
            }
        }
    }
    
    if (($intOnly) && (!file_exists($intfile))) {
        exit(Errors::INVALID_PATH);
    }
    if (($parseOnly) && (!file_exists($parsefile))) {
        exit(Errors::INVALID_PATH);
    }

    #test just for interpret
    foreach ($files as $key => $testFile) {
        if (preg_match("/.src$/", $testFile)) { //If files ends with .src
            $testcounter++;
            $rcFile = substr($testFile, 0, -3) . "rc";  //File with exit code
            $outFile = substr($testFile, 0, -3) . "out";    //File with output
            $inFile = substr($testFile, 0, -3) . "in";
            $expRetCode = 0;

            if (file_exists($rcFile)) {
                $tempFile = fopen($rcFile, "r") or exit(Errors::ERROR_OPEN_FILE);
                $expRetCode = fgets($tempFile);
                $expRetCode = intval($expRetCode);
                fclose($tempFile);
            } else {
                $tempFile = fopen($rcFile, "w") or exit(Errors::ERROR_OPEN_FILE);
                fwrite($tempFile, $expRetCode);
                fclose($tempFile);
            }

            if (!file_exists($outFile)) {
                $tempFile = fopen($outFile, "w") or exit(Errors::ERROR_OPEN_FILE);
                fclose($tempFile);
            }

            if (!file_exists($inFile)) {
                $tempFile = fopen($inFile, "w") or exit(Errors::ERROR_OPEN_FILE);
                fclose($tempFile);
            }

            $retCode = NULL;
            $output = NULL;
                
            if ($parseOnly){
                exec("php7.4 " . $parsefile . " <" . $testFile . " >temp.out1", $output, $retCode);
            } elseif ($intOnly) {
                exec("python3.8 " . $intfile . " --input=" . $inFile . " <" . $testFile . " >temp.out2", $output, $retCode);
            } else { 
                exec("php7.4 " . $parsefile . " <" . $testFile . " >temp.out1", $output, $retCode);
                if ($retCode == 0) {
                    exec("python3.8 " . $intfile . " --input=" . $inFile . " <temp.out1" . " >temp.out2", $output, $retCode);
                }
            }

            if ($retCode == $expRetCode) {
                if ($retCode == 0 && !$parseOnly) {
                    exec("diff -q temp.out2 " . $outFile, $result, $retDiff);
                        
                    if ($retDiff == 0) {
                        $passed++;
                        #HTMLGEN
                    } else {
                        $failed++;
                        #HTMLGEN   
                        echo("Failed in " . $testFile);
                        echo("\n");
                        echo("DIFF ERROR: ");
                        echo("\n");
                        exit(0);                    
                    }


                } elseif($retCode == 0) {
                    exec("java -jar " . $jexamxml . " temp.out1 " . $outFile, $result, $retDiff);

                    if ($retDiff == 0) {
                        $passed++;
                        #HTMLGEN
                    } else {
                        $failed++;
                        #htmlGen;
                    }
                } else {
                    
                    #htmlgen
                    $passed++;
                }
            } else {
                $failed++;
                echo("Failed in " . $testFile);
                echo("\n");
                echo("RetValue is: ". $retCode);
                echo("\n");

                echo("Expected RetValue is: ". $expRetCode);
                echo("\n");
                exit(0);
                #HTMLGEN here
            }
            if ($parseOnly) {
                unlink("temp.out1");
            } elseif ($intOnly) {
                unlink("temp.out2");
            } else {
                #unlink("temp.out2");
                #unlink("temp.out1");
            }
        }   
    }
    echo "Passed test:" . $passed ."\n";
    echo "Failed test:" . $failed ."\n";
    echo "Count test:" . $testcounter . "\n";

}

argParse($argc);
echo "Arg ok\n";
test();
echo "success\n"


/*
end of file test.php
*/
?>