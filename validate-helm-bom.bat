@echo off
REM Helm Variable Reference Checker with BOM - Windows Batch Script
REM Usage: validate-helm-bom.bat [bom-file] [values-file]
REM Example: validate-helm-bom.bat ./example-bom.yaml ./values-dev.yaml

if "%~1"=="" (
    echo Usage: validate-helm-bom.bat [bom-file] [values-file]
    echo Example: validate-helm-bom.bat ./example-bom.yaml ./values-dev.yaml
    echo.
    echo For single chart usage, use validate-helm.bat instead
    exit /b 1
)

if "%~2"=="" (
    echo Usage: validate-helm-bom.bat [bom-file] [values-file]
    echo Example: validate-helm-bom.bat ./example-bom.yaml ./values-dev.yaml
    echo.
    echo Missing values file parameter
    exit /b 1
)

echo Running Helm Variable Checker with BOM...
echo BOM File: %~1
echo Values File: %~2
echo.

py helm_variable_checker.py --bom-file "%~1" --values-file "%~2"

if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Validation failed! Some variables are missing.
    exit /b %ERRORLEVEL%
) else (
    echo.
    echo SUCCESS: All variables validated!
    exit /b 0
)
