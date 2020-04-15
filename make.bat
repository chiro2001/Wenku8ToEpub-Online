@echo off
pyinstaller wk8local.py
md dist\wk8local\static
copy /Y static\* dist\wk8local\static\
md dist\wk8local\templates
copy /Y templates\* dist\wk8local\templates\
copy dmzj_novel_data_full.json dist\wk8local\
copy dmzj_novel_data.json dist\wk8local\
