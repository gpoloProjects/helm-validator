# Helm Variable Reference Checker

This Python script traverses through Helm chart files and checks if variable references exist in your values file. It provides detailed logging output showing which variables are found/missing.

## Features

- **Recursive Directory Traversal**: Searches through all subdirectories for Helm chart files
- **Multiple File Types**: Supports `.yaml`, `.yml`, and `.tpl` files
- **Regex Pattern Matching**: Finds Helm template variables like `{{ .Values.PG.R1.DBName }}` and `{{ .Values.AppName | quote }}`
- **Values File Validation**: Checks if each variable path exists in your values YAML file
- **Detailed Reporting**: Shows filename, variable reference, and existence status with ✓ or ✗
- **Summary Statistics**: Provides count of found vs missing variables

## Prerequisites

- Python 3.6+
- PyYAML library

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

Or install PyYAML directly:
```bash
pip install PyYAML>=6.0
```

## Usage

Basic usage:
```bash
python helm_variable_checker.py --helm-charts-path /path/to/your/helm/charts --values-file /path/to/values-dev.yaml
```

With verbose logging:
```bash
python helm_variable_checker.py --helm-charts-path /path/to/your/helm/charts --values-file /path/to/values-dev.yaml --verbose
```

## Example

Using the provided example files:
```bash
python helm_variable_checker.py --helm-charts-path ./example_helm_charts --values-file ./values-dev.yaml
```

## Sample Output

```
2025-08-25 12:30:15,123 - INFO - ================================================================================
2025-08-25 12:30:15,124 - INFO - HELM VARIABLE REFERENCE CHECKER REPORT
2025-08-25 12:30:15,124 - INFO - ================================================================================
2025-08-25 12:30:15,124 - INFO - Helm Charts Path: /path/to/charts
2025-08-25 12:30:15,124 - INFO - Values File: /path/to/values-dev.yaml
2025-08-25 12:30:15,124 - INFO - ================================================================================
2025-08-25 12:30:15,125 - INFO - Successfully loaded values file: /path/to/values-dev.yaml
2025-08-25 12:30:15,126 - INFO - Found 2 Helm chart files to process
2025-08-25 12:30:15,127 - INFO - Processing file: templates/deployment.yaml (6 variables found)
2025-08-25 12:30:15,128 - INFO - Processing file: templates/service.yaml (4 variables found)
2025-08-25 12:30:15,129 - INFO - Total variables processed: 10

2025-08-25 12:30:15,129 - INFO - 
File: templates/deployment.yaml
2025-08-25 12:30:15,129 - INFO - ----------------------------------------
2025-08-25 12:30:15,130 - INFO -   ✓ .Values.AppName
2025-08-25 12:30:15,130 - INFO -   ✓ .Values.Image.Repository
2025-08-25 12:30:15,131 - INFO -   ✓ .Values.Image.Tag
2025-08-25 12:30:15,131 - INFO -   ✓ .Values.PG.R1.DBName
2025-08-25 12:30:15,132 - INFO -   ✓ .Values.PG.R1.Host
2025-08-25 12:30:15,132 - INFO -   ✓ .Values.ReplicaCount

2025-08-25 12:30:15,133 - INFO - 
File: templates/service.yaml
2025-08-25 12:30:15,133 - INFO - ----------------------------------------
2025-08-25 12:30:15,134 - INFO -   ✓ .Values.AppName
2025-08-25 12:30:15,134 - INFO -   ✓ .Values.Service.Port
2025-08-25 12:30:15,135 - INFO -   ✓ .Values.Service.TargetPort
2025-08-25 12:30:15,135 - INFO -   ✓ .Values.Service.Type
2025-08-25 12:30:15,136 - INFO - ================================================================================
2025-08-25 12:30:15,136 - INFO - SUMMARY: 10/10 variables found in values file
2025-08-25 12:30:15,137 - INFO - All variables are present in the values file!
2025-08-25 12:30:15,137 - INFO - ================================================================================
```

## Script Features

### Variable Pattern Recognition
The script uses a regex pattern to find Helm template variables:
- `{{ .Values.AppName }}` - Simple variable reference
- `{{ .Values.PG.R1.DBName | quote }}` - Variable with pipe functions
- `{{ .Values.Image.Repository }}` - Nested object references

### Supported File Extensions
- `.yaml` - Standard YAML files
- `.yml` - Alternative YAML extension
- `.tpl` - Helm template files

### Values File Structure
The script supports nested YAML structures. For example:
```yaml
AppName: my-app
Database:
  Host: localhost
  Port: 5432
  Credentials:
    Username: user
    Password: pass
```

This allows checking variables like:
- `.Values.AppName`
- `.Values.Database.Host`
- `.Values.Database.Credentials.Username`

## Error Handling

The script includes comprehensive error handling for:
- Missing files or directories
- Invalid YAML syntax
- File permission issues
- Malformed variable references

## Command Line Arguments

- `--helm-charts-path`: **Required** - Path to directory containing Helm charts
- `--values-file`: **Required** - Path to the values YAML file
- `--verbose`: Optional - Enable verbose logging for debugging

## Example Directory Structure

```
your-project/
├── helm-charts/
│   ├── templates/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   │   └── ingress.yaml
│   └── values.yaml
├── values-dev.yaml
└── helm_variable_checker.py
```

Run with:
```bash
python helm_variable_checker.py --helm-charts-path ./helm-charts --values-file ./values-dev.yaml
```
