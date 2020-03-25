@echo off
pyinstaller wk8local.py
md dist\wk8local\static
copy /Y static\* dist\wk8local\static\
md dist\wk8local\templates
copy /Y templates\* dist\wk8local\templates\
