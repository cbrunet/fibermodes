@ECHO OFF
SETLOCAL
SET PYTHONPATH=%CD%;%PYTHONPATH%
pythonw fibermodesgui\modsolverapp.py
ENDLOCAL
