echo off
echo msgbox "%1" >%temp%\tmp.vbs
cscript /nologo %temp%\tmp.vbs
del %temp%\tmp.vbs