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

- Python 3.6+ (tested with Python 3.13.7)
- PyYAML library

## Installation

1. **Clone or download this repository**
```bash
git clone <repo from pdmex>
cd helm-validator
```

2. **Install Python dependencies**

On Windows:
```bash
py -m pip install -r requirements.txt
```

On Linux/macOS:
```bash
pip install -r requirements.txt
```

## Usage

**Windows:**
```bash
py helm_variable_checker.py --helm-charts-path /path/to/your/helm/charts --values-file /path/to/values.yaml
```

**Linux/macOS:**
```bash
python helm_variable_checker.py --helm-charts-path /path/to/your/helm/charts --values-file /path/to/values.yaml
```

### Quick Test
Test with the included example files:
```bash
# Windows
py helm_variable_checker.py --helm-charts-path ./example_helm_charts --values-file ./values-dev.yaml

# Linux/macOS
python helm_variable_checker.py --helm-charts-path ./example_helm_charts --values-file ./values-dev.yaml
```

## Command Line Arguments

### Required Arguments
- `--helm-charts-path`: Path to directory containing Helm charts
- `--values-file`: Path to the values YAML file to validate against

### Optional Arguments
- `--help`: Show help message and exit

## Examples and Advanced Usage

For detailed examples, sample output, troubleshooting, and advanced usage patterns, see [EXAMPLES.md](EXAMPLES.md).

## Contributing

Feel free to submit issues and pull requests to improve this tool.
