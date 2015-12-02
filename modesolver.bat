@ECHO OFF
SETLOCAL
SET PYTHONPATH=%CD%;%PYTHONPATH%
pythonw fibermodesgui\modesolverapp.py
ENDLOCAL
