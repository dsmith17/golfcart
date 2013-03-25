<?php

session_start();

if(isset($_SESSION['writes']))
{
}
else
{
    $_SESSION['writes'] = 0;
}

function theform()
{
    echo "<link rel=\"SHORTCUT ICON\" href=\"bcl_icon.ico\"  type=\"image/x-icon\">\n";
    echo "<form name=\"controls\" method=\"GET\" action=\"".$_SERVER['PHP_SELF']."\">\n";
    echo "<input type=\"submit\" name=\"command\" value=\"left\"> \n";
    echo "<input type=\"submit\" name=\"command\" value=\"right\"> <br>\n";

    echo "<input type=\"submit\" name=\"command\" value=\"faster\"> \n";
    echo "<input type=\"submit\" name=\"command\" value=\"slower\"> \n";
    echo "<input type=\"submit\" name=\"command\" value=\"stop\"> <br>\n";

    echo "<input type=\"submit\" name=\"command\" value=\"reload\"> <br>\n";
    echo "<input type=\"submit\" name=\"command\" value=\"reset\"> <br>\n";
	echo "</form>\n";
	getParms();
}

function writeFile($cmd)
{
    $comFile = "data/commandFile.txt";
	$file = fopen($comFile,'w') or die("can't make file");
	fwrite($file,$cmd);
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
        $data = fscanf($file, "%s = %s");
    }
    flock($file, LOCK_UN);
    fclose($file);
}

if (isset($_GET['seq']))
{
    $_SESSION['writes'] = $_GET['seq'] - 1;
}

if (isset($_GET['command']))
{
	switch($_GET['command'])
	{
		case "left":
            $cmd = 'left';
            $_SESSION['writes'] = $_SESSION['writes'] + 1;
            writeFile($_SESSION['writes'] . " left");
		break;
		case "right":
            $cmd = 'right';
            $_SESSION['writes'] = $_SESSION['writes'] + 1;
            writeFile($_SESSION['writes'] . " right");
		break;
		case "faster":
            $cmd = 'up';
            $_SESSION['writes'] = $_SESSION['writes'] + 1;
            writeFile($_SESSION['writes'] . " up");
		break;
		case "slower":
            $cmd = 'down';
            $_SESSION['writes'] = $_SESSION['writes'] + 1;
            writeFile($_SESSION['writes'] . " down");
		break;
		case "stop":
            $cmd = 'stop';
            $_SESSION['writes'] = $_SESSION['writes'] + 1;
			writeFile($_SESSION['writes'] . " stop");
		break;
		case "reset":
            $cmd = 'reset';
            $_SESSION['writes'] = $_SESSION['writes'] + 1;
			writeFile($_SESSION['writes'] . " reset");
		break;

		default:
	}
}
theform();

?>
