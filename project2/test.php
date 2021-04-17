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

//Class with errors exit codes
abstract class Errors {
    const ERROR_PATH_OR_FILE = 41;
    const INVALID_ARGUMENTS = 10;
    const INVALID_PATH = 11;
    const ERROR_OPEN_FILE = 12;
}

//Class for generating output HTML
class HTMLGen {
    public $HTMLHead = "<p style=\"text-align: center;\">&nbsp;</p>
    <p style=\"margin-bottom: 0in; text-align: center;\"><strong>Test.php mode:</strong>";
    public $totalTest = "";
    public $HTMLOut = "";
    public $HTMLBody = "";

    public function __construct() {
        global $intOnly, $parseOnly;
        if ($intOnly) {
            $this->HTMLHead .= "interpret-only</p>";
        } elseif ($parseOnly) {
            $this->HTMLHead .= "parse-only</p>";
        } else {
            $this->HTMLHead .= "both</p>";
        }
    }

    //Generates final output HTML then print it
    public function printHTML() {
        $this->HTMLOut = $this->HTMLHead . $this->totalTest . $this->HTMLBody;
        $this->HTMLOut .= "</tbody>
                            </table>
                            <p style=\"margin-bottom: 0in; text-align: center;\">&nbsp;</p>";
        echo $this->HTMLOut;
    }

    //Generates header with total count test and passed/failed tests
    public function genTotalTest($testCounter, $passed, $failed) {
        $this->totalTest = "<p style=\"margin-bottom: 0in; text-align: center;\">&nbsp;</p>
        <p style=\"margin-bottom: 0in; text-align: center;\"><span style=\"font-size: medium;\">Total tests count: </span><span style=\"font-size: medium;\"><strong>" . strval($testCounter) ."</strong></span></p>
        <table style=\"margin-left: auto; margin-right: auto;\" width=\"1024\" cellspacing=\"0\" cellpadding=\"7\">
        <tbody>
        <tr valign=\"TOP\">
        <td style=\"border: 1.00pt solid #000001; padding: 0.07in;\" bgcolor=\"#ffffff\" width=\"286\" height=\"84\">
        <p style=\"margin-bottom: 0in; background: #ffffff; border: none; padding: 0in; page-break-inside: auto; widows: 0; orphans: 0; page-break-after: auto;\" align=\"CENTER\"><span style=\"color: #38761d;\"><span style=\"font-size: large;\">Passed</span></span></p>
        <p style=\"background: #ffffff; border: none; padding: 0in; page-break-inside: auto; widows: 0; orphans: 0; page-break-after: auto;\" align=\"CENTER\"><span style=\"font-size: x-large;\"><strong>" . strval($passed) . "</strong></span></p>
        </td>
        <td style=\"border: 1.00pt solid #000001; padding: 0.07in;\" bgcolor=\"#ffffff\" width=\"286\">
        <p style=\"margin-bottom: 0in; background: #ffffff; border: none; padding: 0in; page-break-inside: auto; widows: 0; orphans: 0; page-break-after: auto;\" align=\"CENTER\"><span style=\"color: #cc0000;\"><span style=\"font-size: large;\">Failed</span></span></p>
        <p style=\"background: #ffffff; border: none; padding: 0in; page-break-inside: auto; widows: 0; orphans: 0; page-break-after: auto;\" align=\"CENTER\"><span style=\"font-size: x-large;\"><strong>" . strval($failed) . "</strong></span></p>
        </td>
        </tr>
        </tbody>
        </table>
        <p style=\"margin-bottom: 0in; text-align: center;\">&nbsp;</p>
        <p style=\"margin-bottom: 0in; text-align: center;\">&nbsp;</p>
        <table style=\"height: 184px; margin-left: auto; margin-right: auto;\" width=\"1024\" cellspacing=\"0\" cellpadding=\"7\">
        <tbody>
        <tr style=\"height: 44px;\" valign=\"TOP\">
        <td style=\"border: 1pt solid #000001; padding: 0.07in; height: 44px; width: 316.906px;\" bgcolor=\"#ffffff\">
        <p style=\"background: #ffffff; border: none; padding: 0in; page-break-inside: auto; widows: 0; orphans: 0; page-break-after: auto;\" align=\"LEFT\">TestName</p>
        </td>
        <td style=\"border: 1pt solid #000001; padding: 0.07in; height: 44px; width: 88.9062px;\" bgcolor=\"#ffffff\">
        <p style=\"widows: 0; orphans: 0;\" align=\"CENTER\">Result</p>
        </td>
        <td style=\"border: 1pt solid #000001; padding: 0.07in; height: 44px; width: 179.906px;\" bgcolor=\"#ffffff\">
        <p style=\"widows: 0; orphans: 0;\" align=\"CENTER\">Expected exit value</p>
        </td>
        <td style=\"border: 1pt solid #000001; padding: 0.07in; height: 44px; width: 177.906px;\" bgcolor=\"#ffffff\">
        <p style=\"widows: 0; orphans: 0;\" align=\"CENTER\">Exit value</p>
        </td>
        <td style=\"border: 1pt solid #000001; padding: 0.07in; height: 44px; width: 177.906px;\" bgcolor=\"#ffffff\">
        <p style=\"widows: 0; orphans: 0;\" align=\"CENTER\">Output</p>
        </td>
        </tr>";
    }

    //addes passed test
    public function addFailedTest($directory, $retVaule, $exptRetValue, $output) {
        $this->HTMLBody .= "<tr style=\"height: 52px;\" valign=\"TOP\">
        <td style=\"border: 1pt solid #000001; padding: 0.07in; height: 52px; width: 316.906px;\" bgcolor=\"#ffffff\">
        <p style=\"background: #ffffff; border: none; padding: 0in; page-break-inside: auto; widows: 0; orphans: 0; page-break-after: auto;\" align=\"LEFT\">" . $directory . "</p>
        </td>
        <td style=\"border: 1pt solid #000001; padding: 0.07in; height: 52px; width: 88.9062px;\" bgcolor=\"#ffffff\">
        <p style=\"widows: 0; orphans: 0;\" align=\"CENTER\"><span style=\"color: #cc0000;\">Failed</span></p>
        </td>
        <td style=\"border: 1pt solid #000001; padding: 0.07in; height: 52px; width: 179.906px;\" bgcolor=\"#ffffff\">
        <p style=\"widows: 0; orphans: 0;\" align=\"CENTER\">" . strval($exptRetValue) . "</p>
        </td>
        <td style=\"border: 1pt solid #000001; padding: 0.07in; height: 52px; width: 177.906px;\" bgcolor=\"#ffffff\">
        <p style=\"widows: 0; orphans: 0;\" align=\"CENTER\">" . strval($retVaule) . "</p>
        </td>
        <td style=\"border: 1pt solid #000001; padding: 0.07in; height: 52px; width: 177.906px;\" bgcolor=\"#ffffff\">";
        
        if ($output) { 
            $this->HTMLBody .= "<h1 class=\"western\" style=\"font-size: 20px; margin-top: 0in; background: #ffffff; page-break-inside: auto; widows: 0; orphans: 0; page-break-after: auto;\" align=\"CENTER\"><a name=\"_vpl2p4qqnh69\"></a> <span style=\"color: #cc0000;\">✘</span></h1>
            </td>
            </tr>";
        } else { 
            $this->HTMLBody .= "<p style=\"background: #ffffff; border: none; padding: 0in; page-break-inside: auto; widows: 0; orphans: 0; page-break-after: auto;\" align=\"CENTER\"><strong>-</strong></p>";
        }
    }

    //addes failed test
    public function addPassedTest($directory, $retVaule, $exptRetValue, $output) {
        $this->HTMLBody .= "<tr style=\"height: 52px;\" valign=\"TOP\">
        <td style=\"border: 1pt solid #000001; padding: 0.07in; height: 52px; width: 316.906px;\" bgcolor=\"#ffffff\">
        <p style=\"background: #ffffff; border: none; padding: 0in; page-break-inside: auto; widows: 0; orphans: 0; page-break-after: auto;\" align=\"LEFT\">". $directory ."</p>
        </td>
        <td style=\"border: 1pt solid #000001; padding: 0.07in; height: 52px; width: 88.9062px;\" bgcolor=\"#ffffff\">
        <p style=\"widows: 0; orphans: 0;\" align=\"CENTER\"><span style=\"color: #38761d;\">Passed</span></p>
        </td>
        <td style=\"border: 1pt solid #000001; padding: 0.07in; height: 52px; width: 179.906px;\" bgcolor=\"#ffffff\">
        <p style=\"widows: 0; orphans: 0;\" align=\"CENTER\"><span style=\"color: #000000;\">" . strval($exptRetValue) . "</span></p>
        </td>
        <td style=\"border: 1pt solid #000001; padding: 0.07in; height: 52px; width: 177.906px;\" bgcolor=\"#ffffff\">
        <p style=\"widows: 0; orphans: 0;\" align=\"CENTER\"><span style=\"color: #000000;\">" . strval($retVaule) . "</span></p>
        </td>
        <td style=\"border: 1pt solid #000001; padding: 0.07in; height: 52px; width: 177.906px;\" bgcolor=\"#ffffff\">";

        if ($output) {
            $this->HTMLBody .= "<p style=\"widows: 0; orphans: 0; font-size: 23px;\" align=\"CENTER\"><span style=\"color: #6aa84f;\"><span style=\"background: #ffffff;\">✔</span></span></p>
            </td>
            </tr>";
        } else {
            $this->HTMLBody .= "<p style=\"background: #ffffff; border: none; padding: 0in; page-break-inside: auto; widows: 0; orphans: 0; page-break-after: auto;\" align=\"CENTER\"><strong>-</strong></p>
            </td>
            </tr>";
        }
    }
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

    //If help in args
    if ((array_key_exists("help", $options))) {
        if ($argc == 2) {
            echo helpText;
            exit(0);
        } else {
            exit(Errors::INVALID_ARGUMENTS);
        }
    } elseif ((array_key_exists("parse-only", $options) //Parse only must be without intonly/int script etc.
              && (array_key_exists("int-script", $options) || array_key_exists("int-only", $options))
              || (array_key_exists("int-only", $options) 
              && (array_key_exists("parse-only", $options) || array_key_exists("parse-script", $options))))) {
        exit(Errors::INVALID_ARGUMENTS);
    } else {    //If not hep
        foreach ($options as $opt => $path) {

            $expectedargc++;    
            
            //Sets flags for each program argument
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

//Function returns list of all files in directory(recursive)
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

    //Checks if directory is exists, generates array $files with all files in directory
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
    
    //Flag/files checks
    if (($intOnly) && (!file_exists($intfile))) {
        exit(Errors::INVALID_PATH);
    }elseif (($parseOnly) && (!file_exists($parsefile))) {
        exit(Errors::INVALID_PATH);
    }elseif (!$parseOnly && !$intOnly && (!file_exists($parsefile) || !file_exists($intfile))) {
        exit(Errors::INVALID_PATH);
    }

    //Generating object for HTML output
    $HtmlGen = new HTMLGen();
    #tests
    foreach ($files as $key => $testFile) {
        if (preg_match("/.src$/", $testFile)) { //If files ends with .src
            $testcounter++;
            $rcFile = substr($testFile, 0, -3) . "rc";  //File with exit code
            $outFile = substr($testFile, 0, -3) . "out";    //File with output
            $inFile = substr($testFile, 0, -3) . "in";
            $expRetCode = 0;

            //Checking if file rc, out, in is exists, if not generates files
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
                
            if ($parseOnly) {
                exec("php7.4 " . $parsefile . " <" . $testFile . " >temp.out1", $output, $retCode);
            } elseif ($intOnly) {
                exec("python3.8 " . $intfile . " --input=" . $inFile . " <" . $testFile . " >temp.out2", $output, $retCode);
            } else { 
                exec("php7.4 " . $parsefile . " <" . $testFile . " >temp.out1", $output, $retCode);
                if ($retCode == 0) {
                    exec("python3.8 " . $intfile . " --input=" . $inFile . " <temp.out1" . " >temp.out2", $output, $retCode);
                } //TODO?
            }

            //If exit code is ok
            if ($retCode == $expRetCode) {
                if ($retCode == 0 && !$parseOnly) { //compare outputs with diff
                    exec("diff -q temp.out2 " . $outFile, $result, $retDiff);
                        
                    if ($retDiff == 0) {
                        $passed++;
                        $HtmlGen->addPassedTest($testFile, $retCode, $expRetCode, true);
                    } else {
                        $failed++;
                        $HtmlGen->addFailedTest($testFile, $retCode, $expRetCode, true);   
                    }


                } elseif($retCode == 0) {   //compare outputs with jexam script
                    exec("java -jar " . $jexamxml . " temp.out1 " . $outFile, $result, $retDiff);

                    if ($retDiff == 0) {
                        $passed++;
                        $HtmlGen->addPassedTest($testFile, $retCode, $expRetCode, true);   
                    } else {
                        $failed++;
                        $HtmlGen->addFailedTest($testFile, $retCode, $expRetCode, true);   
                    }
                } else {
                    
                    $HtmlGen->addPassedTest($testFile, $retCode, $expRetCode, false); 
                    $passed++;
                }
            } else {
                $failed++;
                $HtmlGen->addFailedTest($testFile, $retCode, $expRetCode, false);   
            }

            if ($parseOnly) {
                unlink("temp.out1");
            } elseif ($intOnly) {
                unlink("temp.out2");
            } else {
                unlink("temp.out2");
                unlink("temp.out1");
            }
        }   
    }
    $HtmlGen->genTotalTest($testcounter, $passed, $failed);
    $HtmlGen->printHtml();
}

argParse($argc);
test();


/*
end of file test.php
*/
?>