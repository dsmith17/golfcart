<?php
include "debug.php";
include "interface.php";

session_start();

//print_array($_SESSION);
//print_array($_POST);

if(isset($_SESSION['writes']))
{
}
else
{
    $_SESSION['writes'] = 0;
}

function writeFile($cmd)
{
    $comFile = "data/comFile.txt" or die("can't make file");
	$file = fopen($comFile,'w');
	fwrite($file,$cmd);
	fclose($file);
}

function get_file($filename)
{
	$new_filename = "data/script.txt";
	if(!move_uploaded_file($_FILES['THE_SCRIPT']['tmp_name'], $new_filename))
	{
		echo "The file did not upload!";
	}
	else
	{
          echo $new_filename ." was uploaded";
	}
}

function writeLog($cmd)
{
//     $data = new DateTime();
    date_default_timezone_set("America/New_York");
    $data = date("n-j-y g:i:s");
    $comLog = "data/comLog.txt";// or die("can't make log");
    $file = fopen($comLog, 'a');
//     fwrite($file,"\n".$data->format("n-j-y g:i:s")."\n".$cmd);
    fwrite($file,"\n".$data."\n".$cmd) or die("can't make log");
    fclose($file);
}

function getParms()
{
    $comFile = "data/statusFile.txt";
    $file = fopen($comFile,'r') or die("can't make file");
    flock($file, LOCK_EX);
    $data = fscanf($file, "%s = %s");
    while (!feof($file))
    {
        echo "$data[0] =  $data[1] <br>\n";
        writeLog("$data[0] = $data[1] \n");
        $data = fscanf($file, "%s = %s");
    }
    flock($file, LOCK_UN);
    fclose($file);
}
//echo "right before the isset if statement<br>\n";
// echo "post clickme is: " . $_POST['clickme']."<br>\n";
if (isset($_POST['clickme']))
{
     interface_header();
     getParms();
     writeLog($_POST['clickme'] . "\n");
     switch($_POST['clickme'])
     {
          case "left":
               $_SESSION['writes'] = $_SESSION['writes'] + 1;
               writeFile($_SESSION['writes'] . " left");
          break;
          case "right":
               $_SESSION['writes'] = $_SESSION['writes'] + 1;
               writeFile($_SESSION['writes'] . " right");
          break;
          case "up":
               $_SESSION['writes'] = $_SESSION['writes'] + 1;
               writeFile($_SESSION['writes'] . " up");
          break;
          case "down":
               $_SESSION['writes'] = $_SESSION['writes'] + 1;
               writeFile($_SESSION['writes'] . " down");
          break;
          case "stop":
               $_SESSION['writes'] = $_SESSION['writes'] + 1;
               writeFile($_SESSION['writes'] . " stop");
          break;
          case "reset":
               //echo "resetting<br>\n";
               $_SESSION['writes'] = 0;
               writeFile($_SESSION['writes'] . " reset");
          break;
          case "change_direction":
               $_SESSION['writes'] = $_SESSION['writes'] + 1;
               writeFile($_SESSION['writes'] . " change_direction");
          break;
          case "steer_mode":
               $_SESSION['writes'] = $_SESSION['writes'] + 1;
               writeFile($_SESSION['writes'] . " steer_mode");
          break;
          case "upload":
     // 			echo "uploaded a file";
     // 			print_array($_FILES);
               if(isset($_FILES) && $_FILES['THE_SCRIPT']['name'] != "" )
               {
                    get_file($_FILES['THE_SCRIPT']['name']);
               }
          break;
          case "script":
               $_SESSION['writes'] = $_SESSION['writes'] + 1;
               writeFile($_SESSION['writes'] . " script");		
          break;

          default:
     }
    interface_controls();
}
else
{
    interface_header();
    getParms();
    interface_controls();
}
//print_array($_SESSION);
//controls();
//print_array($_POST);
/*
 * [Wed Jun 19 14:37:17 2013] [error] [client 157.182.181.96] PHP Warning:  fopen(data/statusFile.txt): failed to open stream: Permission denied in /home/student1/public_html/index.php on line 47
[Wed Jun 19 14:37:17 2013] [error] [client 157.182.181.96] File does not exist: /var/www/favicon.ico
[Wed Jun 19 14:37:19 2013] [error] [client 157.182.181.96] PHP Warning:  fopen(data/statusFile.txt): failed to open stream: Permission denied in /home/student1/public_html/index.php on line 47
[Wed Jun 19 14:37:19 2013] [error] [client 157.182.181.96] File does not exist: /var/www/favicon.ico
[Wed Jun 19 14:37:20 2013] [error] [client 157.182.181.96] PHP Warning:  fopen(data/statusFile.txt): failed to open stream: Permission denied in /home/student1/public_html/index.php on line 47
[Wed Jun 19 14:37:20 2013] [error] [client 157.182.181.96] File does not exist: /var/www/favicon.ico
[Wed Jun 19 14:37:20 2013] [error] [client 157.182.181.96] PHP Warning:  fopen(data/statusFile.txt): failed to open stream: Permission denied in /home/student1/public_html/index.php on line 47
[Wed Jun 19 14:37:20 2013] [error] [client 157.182.181.96] File does not exist: /var/www/favicon.ico
[Wed Jun 19 14:37:20 2013] [error] [client 157.182.181.96] PHP Warning:  fopen(data/statusFile.txt): failed to open stream: Permission denied in /home/student1/public_html/index.php on line 47
[Wed Jun 19 14:37:20 2013] [error] [client 157.182.181.96] File does not exist: /var/www/favicon.ico
*/

?>

