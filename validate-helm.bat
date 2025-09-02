@echo off
REM Helm Variable Reference Checker - Windows Batch Script
REM Usage: validate-helm.bat [chart-path] [values-file]
REM Example: validate-helm.bat ./example_helm_charts ./values-dev.yaml

if "%~1"=="" (
    echo Usage: validate-helm.bat [chart-path] [values-file]
    echo Example: validate-helm.bat ./example_helm_charts ./values-dev.yaml
    echo.
    echo For BOM file usage, use validate-helm-bom.bat instead
    exit /b 1
)

if "%~2"=="" (
    echo Usage: validate-helm.bat [chart-path] [values-file]
    echo Example: validate-helm.bat ./example_helm_charts ./values-dev.yaml
    echo.
    echo Missing values file parameter
    exit /b 1
)

echo Running Helm Variable Checker...
echo Chart Path: %~1
echo Values File: %~2
echo.

py helm_variable_checker.py --helm-charts-path "%~1" --values-file "%~2"

if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Validation failed! Some variables are missing.
    exit /b %ERRORLEVEL%
) else (
    echo.
    echo SUCCESS: All variables validated!
    exit /b 0
)
