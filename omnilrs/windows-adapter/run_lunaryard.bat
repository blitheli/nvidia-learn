@echo off
setlocal EnableExtensions
rem Draft only. Not run on Windows. Opens lunaryard_20m and does not start ROS 2.
if not defined ISAAC_PYTHON set "ISAAC_PYTHON=C:\isaacsim\python.bat"
if not defined OMNILRS_ROOT set "OMNILRS_ROOT=%~dp0..\upstream"
if not defined OMNI_KIT_ACCEPT_EULA set "OMNI_KIT_ACCEPT_EULA=YES"
if not exist "%ISAAC_PYTHON%" (
  echo [windows-adapter] ISAAC_PYTHON not found: %ISAAC_PYTHON%
  exit /b 1
)
call "%ISAAC_PYTHON%" "%~dp0visual_preview.py" --environment lunaryard_20m %*
exit /b %ERRORLEVEL%
