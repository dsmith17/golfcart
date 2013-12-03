<?php

function print_array($array)
{
            echo "<div style=\"font-family: 'Courier New', Courier, monospace; font-size: 12px;\">\n";
                    print_array_recursive($array, '');
                    echo "</div>\n";
}

function print_array_recursive($array, $prefix)
{
            foreach ($array as $k=>$v)
                        {
                                            if (is_array($v))
                                                                {
                                                                                            echo $prefix.$k.' =&gt; '."<br>\n";
                                                                                                                    print_array_recursive($v, $prefix."&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;");
                                                                                                            }
                                                            else
                                                                                {
                                                                                                            echo $prefix.$k.' =&gt; '.$v."<br>\n";
                                                                                                                            }
                                                    }
}

?>
