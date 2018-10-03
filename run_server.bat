@echo off

E:

cd E:\pyObj\ore4

set a=%time%

echo Start time: %a%

echo start run.py

start pythonw run.py

set b=%time%

echo End time: %b%

exit