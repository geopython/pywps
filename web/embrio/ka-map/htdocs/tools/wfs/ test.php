<?php

dl('php_mapscript.so');
echo phpinfo();
die;
$expURL="(^|[ \t\r\n])((ftp|http|https):(([A-Za-z0-9$_.+!*(),;/?:@&~=-])|%[A-Fa-f0-9]{2}){2,}(#([a-zA-Z0-9][a-zA-Z0-9$_.+!*(),;/?:@&~=%-]*))?([A-Za-z0-9$_+!*();/?:~-]))";

echo  ereg($exp,"http://sticazzi.com" );

?>