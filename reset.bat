@echo off
echo Are you sure you will reset? 
pause
rm -r docs
rm -r tags
mkdir docs
mkdir tags
rm overall.pickle
echo Done. 
pause
