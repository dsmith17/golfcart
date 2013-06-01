<?php

$comFile = "data/statusFile.txt";
$file = fopen($comFile,'w') or die("can't make file");
flock($file, LOCK_EX);
foreach ($_GET as $key=>$value) 
{
    fwrite($file, "$key = " . urldecode($value) . "\n");
    #echo "$key = " . urldecode($value) . "<br>\n";
}
flock($file, LOCK_UN);
fclose($file);

$comFile = "data/comFile.txt";
$file = fopen($comFile, 'r') or die("can't open file");
flock($file, LOCK_EX);
$cmd = fgets($file);
flock($file, LOCK_UN);
fclose($file);

echo "$cmd\n";

?>
