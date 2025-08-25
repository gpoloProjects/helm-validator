#!/usr/bin/env python3
"""
Helm Chart Variable Reference Checker

This script traverses through Helm chart files and checks if variable references
exist in the values file. It outputs the results as log statements.

Usage:
    python helm_variable_checker.py --helm-charts-path /path/to/charts --values-file /path/to/values-dev.yaml
"""

import os
import re
import yaml
import argparse
import logging
from pathlib import Path
from typing import Set, Dict, Any, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HelmVariableChecker:
    def __init__(self, helm_charts_path: str, values_file_path: str):
        self.helm_charts_path = Path(helm_charts_path)
        self.values_file_path = Path(values_file_path)
        self.values_data = {}
        self.helm_file_extensions = {'.yaml', '.yml', '.tpl'}
        
        # Regex pattern to match Helm template variables
        # Matches patterns like {{ .Values.PG.R1.DBName }}, {{ .Values.AppName | quote }}
        self.variable_pattern = re.compile(r'\{\{\s*\.Values\.([^}\s|]+)(?:\s*\|\s*[^}]+)?\s*\}\}')
    
    def load_values_file(self) -> bool:
        """Load and parse the values YAML file."""
        try:
            with open(self.values_file_path, 'r', encoding='utf-8') as file:
                self.values_data = yaml.safe_load(file) or {}
            logger.info(f"Successfully loaded values file: {self.values_file_path}")
            return True
        except FileNotFoundError:
            logger.error(f"Values file not found: {self.values_file_path}")
            return False
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file {self.values_file_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error reading values file {self.values_file_path}: {e}")
            return False
    
    def check_variable_exists(self, variable_path: str) -> bool:
        """
        Check if a variable path exists in the values data.
        
        Args:
            variable_path: Dot-separated path like 'PG.R1.DBName' or 'AppName'
        
        Returns:
            True if the variable exists, False otherwise
        """
        parts = variable_path.split('.')
        current = self.values_data
        
        try:
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return False
            return True
        except (TypeError, KeyError):
            return False
    
    def extract_variables_from_file(self, file_path: Path) -> Set[str]:
        """
        Extract all Helm variable references from a file.
        
        Args:
            file_path: Path to the Helm chart file
        
        Returns:
            Set of variable paths found in the file
        """
        variables = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # Find all variable references
            matches = self.variable_pattern.findall(content)
            variables.update(matches)
            
        except Exception as e:
            logger.warning(f"Error reading file {file_path}: {e}")
        
        return variables
    
    def get_helm_chart_files(self) -> List[Path]:
        """
        Get all Helm chart files in the specified directory.
        
        Returns:
            List of Path objects for Helm chart files
        """
        helm_files = []
        
        try:
            for root, dirs, files in os.walk(self.helm_charts_path):
                for file in files:
                    file_path = Path(root) / file
                    if file_path.suffix.lower() in self.helm_file_extensions:
                        helm_files.append(file_path)
        except Exception as e:
            logger.error(f"Error traversing helm charts directory {self.helm_charts_path}: {e}")
        
        return helm_files
    
    def generate_report(self) -> List[Tuple[str, str, bool]]:
        """
        Generate a report of all variable references and their existence status.
        
        Returns:
            List of tuples containing (filename, variable_reference, exists)
        """
        if not self.load_values_file():
            return []
        
        helm_files = self.get_helm_chart_files()
        logger.info(f"Found {len(helm_files)} Helm chart files to process")
        
        report = []
        total_variables = 0
        
        for file_path in helm_files:
            relative_path = file_path.relative_to(self.helm_charts_path)
            variables = self.extract_variables_from_file(file_path)
            
            if variables:
                logger.info(f"Processing file: {relative_path} ({len(variables)} variables found)")
                
                for variable in sorted(variables):
                    exists = self.check_variable_exists(variable)
                    report.append((str(relative_path), variable, exists))
                    total_variables += 1
        
        logger.info(f"Total variables processed: {total_variables}")
        return report
    
    def print_report(self):
        """Print the complete report with formatted output."""
        logger.info("=" * 80)
        logger.info("HELM VARIABLE REFERENCE CHECKER REPORT")
        logger.info("=" * 80)
        logger.info(f"Helm Charts Path: {self.helm_charts_path}")
        logger.info(f"Values File: {self.values_file_path}")
        logger.info("=" * 80)
        
        report = self.generate_report()
        
        if not report:
            logger.warning("No variable references found or unable to process files")
            return
        
        # Group by file for better readability
        files_dict = {}
        for filename, variable, exists in report:
            if filename not in files_dict:
                files_dict[filename] = []
            files_dict[filename].append((variable, exists))
        
        missing_count = 0
        total_count = len(report)
        
        for filename in sorted(files_dict.keys()):
            logger.info(f"\nFile: {filename}")
            logger.info("-" * 40)
            
            for variable, exists in sorted(files_dict[filename]):
                status = "✓" if exists else "✗"
                if not exists:
                    missing_count += 1
                
                logger.info(f"  {status} .Values.{variable}")
        
        logger.info("=" * 80)
        logger.info(f"SUMMARY: {total_count - missing_count}/{total_count} variables found in values file")
        if missing_count > 0:
            logger.warning(f"{missing_count} variables are missing from {self.values_file_path}")
        else:
            logger.info("All variables are present in the values file!")
        logger.info("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Check Helm chart variable references against values file"
    )
    parser.add_argument(
        '--helm-charts-path',
        required=True,
        help='Path to the directory containing Helm charts'
    )
    parser.add_argument(
        '--values-file',
        required=True,
        help='Path to the values YAML file (e.g., values-dev.yaml)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate paths
    helm_charts_path = Path(args.helm_charts_path)
    values_file_path = Path(args.values_file)
    
    if not helm_charts_path.exists():
        logger.error(f"Helm charts directory does not exist: {helm_charts_path}")
        return 1
    
    if not helm_charts_path.is_dir():
        logger.error(f"Helm charts path is not a directory: {helm_charts_path}")
        return 1
    
    if not values_file_path.exists():
        logger.error(f"Values file does not exist: {values_file_path}")
        return 1
    
    if not values_file_path.is_file():
        logger.error(f"Values path is not a file: {values_file_path}")
        return 1
    
    # Create checker and run report
    checker = HelmVariableChecker(str(helm_charts_path), str(values_file_path))
    checker.print_report()
    
    return 0


if __name__ == "__main__":
    exit(main())
