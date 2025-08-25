# Helm Variable Reference Checker - Examples and Advanced Usage

This document contains detailed examples, sample outputs, troubleshooting guides, and advanced usage patterns for the Helm Variable Reference Checker.

## Complete Example Walkthrough

### Step 1: Test the Installation
First, verify everything is working with the included example files:

```bash
# Windows
py helm_variable_checker.py --helm-charts-path ./example_helm_charts --values-file ./values-dev.yaml

# Linux/macOS
python helm_variable_checker.py --helm-charts-path ./example_helm_charts --values-file ./values-dev.yaml
```

### Step 2: Sample Output
When all variables are found, you'll see output like this:

```
2025-08-25 11:11:33,969 - INFO - ================================================================================
2025-08-25 11:11:33,970 - INFO - HELM VARIABLE REFERENCE CHECKER REPORT
2025-08-25 11:11:33,971 - INFO - ================================================================================
2025-08-25 11:11:33,971 - INFO - Helm Charts Path: example_helm_charts
2025-08-25 11:11:33,972 - INFO - Values File: values-dev.yaml
2025-08-25 11:11:33,972 - INFO - ================================================================================
2025-08-25 11:11:33,979 - INFO - Successfully loaded values file: values-dev.yaml
2025-08-25 11:11:33,982 - INFO - Found 2 Helm chart files to process
2025-08-25 11:11:33,983 - INFO - Processing file: templates\deployment.yaml (8 variables found)
2025-08-25 11:11:33,985 - INFO - Processing file: templates\service.yaml (4 variables found)
2025-08-25 11:11:33,986 - INFO - Total variables processed: 12

2025-08-25 11:11:33,987 - INFO - 
File: templates\deployment.yaml
2025-08-25 11:11:33,987 - INFO - ----------------------------------------
2025-08-25 11:11:33,988 - INFO -   ✓ .Values.AppName
2025-08-25 11:11:33,989 - INFO -   ✓ .Values.Image.Repository
2025-08-25 11:11:33,989 - INFO -   ✓ .Values.Image.Tag
2025-08-25 11:11:33,990 - INFO -   ✓ .Values.PG.R1.DBName
2025-08-25 11:11:33,990 - INFO -   ✓ .Values.PG.R1.Host
2025-08-25 11:11:33,991 - INFO -   ✓ .Values.PG.R1.Username
2025-08-25 11:11:33,991 - INFO -   ✓ .Values.ReplicaCount
2025-08-25 11:11:33,992 - INFO -   ✓ .Values.Service.Port

2025-08-25 11:11:33,993 - INFO - 
File: templates\service.yaml
2025-08-25 11:11:33,993 - INFO - ----------------------------------------
2025-08-25 11:11:33,994 - INFO -   ✓ .Values.AppName
2025-08-25 11:11:33,994 - INFO -   ✓ .Values.Service.Port
2025-08-25 11:11:33,995 - INFO -   ✓ .Values.Service.TargetPort
2025-08-25 11:11:33,995 - INFO -   ✓ .Values.Service.Type
2025-08-25 11:11:33,996 - INFO - ================================================================================
2025-08-25 11:11:33,996 - INFO - SUMMARY: 12/12 variables found in values file
2025-08-25 11:11:33,997 - INFO - All variables are present in the values file!
2025-08-25 11:11:33,997 - INFO - ================================================================================
```

### Step 3: Understanding the Results
- **✓** indicates the variable was found in the values file
- **✗** would indicate a missing variable
- The summary shows total found vs missing variables
- Exit code 0 means all variables were found, non-zero means some were missing

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

## Using with Your Own Helm Charts

### Directory Structure Example
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
├── values-prod.yaml
└── helm_variable_checker.py
```

### Commands for Your Project

**Check development values:**
```bash
# Windows
py helm_variable_checker.py --helm-charts-path ./helm-charts --values-file ./values-dev.yaml

# Linux/macOS
python helm_variable_checker.py --helm-charts-path ./helm-charts --values-file ./values-dev.yaml
```

**Check production values:**
```bash
# Windows
py helm_variable_checker.py --helm-charts-path ./helm-charts --values-file ./values-prod.yaml

# Linux/macOS
python helm_variable_checker.py --helm-charts-path ./helm-charts --values-file ./values-prod.yaml
```

The tool always shows detailed output with all variables listed as found (✓) or missing (✗).

## Integration with CI/CD

### GitHub Actions Example
You can integrate this tool into your CI/CD pipeline to automatically validate Helm charts:

```yaml
name: Validate Helm Charts

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  validate-helm:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    
    - name: Install dependencies
      run: |
        pip install PyYAML>=6.0
    
    - name: Validate Development Values
      run: |
        python helm_variable_checker.py --helm-charts-path ./charts --values-file ./values-dev.yaml
        if [ $? -ne 0 ]; then
          echo "❌ Missing variables found in development values!"
          exit 1
        fi
        echo "✅ Development values validated successfully"
    
    - name: Validate Production Values
      run: |
        python helm_variable_checker.py --helm-charts-path ./charts --values-file ./values-prod.yaml
        if [ $? -ne 0 ]; then
          echo "❌ Missing variables found in production values!"
          exit 1
        fi
        echo "✅ Production values validated successfully"
```

### Jenkins Pipeline Example
```groovy
pipeline {
    agent any
    
    stages {
        stage('Validate Helm Charts') {
            steps {
                script {
                    // Install dependencies
                    sh 'pip install PyYAML>=6.0'
                    
                    // Validate charts
                    def exitCode = sh(
                        script: 'python helm_variable_checker.py --helm-charts-path ./charts --values-file ./values-prod.yaml',
                        returnStatus: true
                    )
                    
                    if (exitCode != 0) {
                        error("Helm chart validation failed - missing variables found!")
                    }
                }
            }
        }
    }
}
```

## Troubleshooting

### Python Command Not Found
If you get "python: command not found":

**Windows:** Use `py` instead of `python`
```bash
py helm_variable_checker.py --help
```

**Linux/macOS:** Try `python3` instead of `python`
```bash
python3 helm_variable_checker.py --help
```

### PyYAML Installation Issues
If PyYAML installation fails:

**Windows:**
```bash
py -m pip install --upgrade pip
py -m pip install PyYAML>=6.0
```

**Linux/macOS:**
```bash
pip3 install --upgrade pip
pip3 install PyYAML>=6.0
```

### File Path Issues
Always use forward slashes or double backslashes in paths:
```bash
# Good
py helm_variable_checker.py --helm-charts-path ./charts --values-file ./values.yaml

# Also good on Windows
py helm_variable_checker.py --helm-charts-path .\\charts --values-file .\\values.yaml
```

### Permission Errors
If you get permission errors, make sure:
1. The files exist and are readable
2. You have read permissions on the directories
3. The values file is a valid YAML file

### Common Error Messages and Solutions

**"Values file not found"**
- Check that the path to your values file is correct
- Ensure the file exists and has read permissions

**"Error parsing YAML file"**
- Validate your YAML syntax using a YAML validator
- Check for proper indentation and structure

**"No Helm chart files found"**
- Verify the helm-charts-path points to a directory containing `.yaml`, `.yml`, or `.tpl` files
- Check that the directory exists and contains template files

## Advanced Usage Patterns

### Batch Validation
Create a script to validate multiple environments:

```bash
#!/bin/bash
# validate-all-envs.sh

environments=("dev" "staging" "prod")

for env in "${environments[@]}"; do
    echo "Validating $env environment..."
    python helm_variable_checker.py \
        --helm-charts-path ./charts \
        --values-file ./values-$env.yaml
    
    if [ $? -ne 0 ]; then
        echo "❌ Validation failed for $env environment"
        exit 1
    fi
    echo "✅ $env environment validated"
    echo ""
done

echo "🎉 All environments validated successfully!"
```

### Integration with Make
Add validation to your Makefile:

```makefile
.PHONY: validate-helm

validate-helm:
	@echo "Validating Helm charts..."
	@python helm_variable_checker.py \
		--helm-charts-path ./charts \
		--values-file ./values-prod.yaml
	@echo "✅ Helm charts validated"

validate-all: validate-helm
	@echo "All validations passed!"
```

### Pre-commit Hook
Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Validate Helm charts before committing

echo "Running Helm variable validation..."
python helm_variable_checker.py --helm-charts-path ./charts --values-file ./values-dev.yaml

if [ $? -ne 0 ]; then
    echo "❌ Helm validation failed. Commit aborted."
    exit 1
fi

echo "✅ Helm validation passed."
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```
