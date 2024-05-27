@ECHO OFF
python --version
IF %ERRORLEVEL% NEQ 0 ( 
   echo MSGBOX "Install Python first" > msgbox.vbs
   call msgbox.vbs
   del  msgbox.vbs /f /q
   exit
)
python -m pip --version
IF %ERRORLEVEL% NEQ 0 (
   python -m ensurepip --upgrade pip
)

pip list>package_list.txt
set /A bea=0
set /A mat=0
for /f %%i in (package_list.txt) do (
	if %%i EQU beautifulsoup4 set /A bea=1
	if %%i EQU matplotlib set /A mat=1
)
if %bea% NEQ 1 pip install beautifulsoup4
if %mat% NEQ 1 pip install matplotlib
del package_list.txt
python log_plot.py
