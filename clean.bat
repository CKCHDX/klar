@echo off
setlocal

set "ROOT=%~dp0"

echo Cleaning KSE state and storage...

if exist "%ROOT%data\state" (
	rmdir /s /q "%ROOT%data\state"
)

if exist "%ROOT%data\storage" (
	rmdir /s /q "%ROOT%data\storage"
)

if exist "%ROOT%config\kse_config.yaml" (
	del /q "%ROOT%config\kse_config.yaml"
)

rem Ensure logs directory exists
if not exist "%ROOT%data\logs" (
	mkdir "%ROOT%data\logs"
)

echo Done.
endlocal
