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
    def __init__(self, helm_charts_paths: List[str], values_file_path: str):
        # Keep paths as strings to preserve relative path format
        self.helm_charts_paths = helm_charts_paths
        self.values_file_path = values_file_path
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
        Get all Helm chart files in the specified directories.
        
        Returns:
            List of Path objects for Helm chart files
        """
        helm_files = []
        
        for helm_charts_path_str in self.helm_charts_paths:
            helm_charts_path = Path(helm_charts_path_str)
            try:
                for root, dirs, files in os.walk(helm_charts_path):
                    for file in files:
                        file_path = Path(root) / file
                        if file_path.suffix.lower() in self.helm_file_extensions:
                            helm_files.append(file_path)
            except Exception as e:
                logger.error(f"Error traversing helm charts directory {helm_charts_path}: {e}")
        
        return helm_files

    @staticmethod
    def parse_bom_file(bom_file_path: str) -> List[str]:
        """
        Parse a BOM file and extract Helm chart paths from spec.workloadList.
        
        Args:
            bom_file_path: Path to the BOM YAML file
            
        Returns:
            List of Helm chart paths found in the BOM file
        """
        chart_paths = []
        
        try:
            with open(bom_file_path, 'r', encoding='utf-8') as file:
                bom_data = yaml.safe_load(file)
            
            # Navigate to spec.workloadList
            if 'spec' in bom_data and 'workloadList' in bom_data['spec']:
                workload_list = bom_data['spec']['workloadList']
                
                for workload in workload_list:
                    # Look for helm.chartPath in each workload
                    if 'helm' in workload and 'chartPath' in workload['helm']:
                        chart_path = workload['helm']['chartPath']
                        chart_paths.append(chart_path)
                        logger.info(f"Found Helm chart path in BOM: {chart_path}")
                
            if not chart_paths:
                logger.warning("No Helm chart paths found in BOM file")
                
        except FileNotFoundError:
            logger.error(f"BOM file not found: {bom_file_path}")
        except yaml.YAMLError as e:
            logger.error(f"Error parsing BOM YAML file {bom_file_path}: {e}")
        except Exception as e:
            logger.error(f"Error reading BOM file {bom_file_path}: {e}")
            
        return chart_paths
    
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
            # Find which base path this file belongs to and create relative path
            relative_path = None
            for base_path_str in self.helm_charts_paths:
                base_path = Path(base_path_str)
                try:
                    relative_path = file_path.relative_to(base_path)
                    # Combine base path string with relative path for display
                    display_path = f"{base_path_str}/{relative_path}".replace('\\', '/')
                    break
                except ValueError:
                    continue
            
            # If we couldn't find a relative path, use the full path
            if relative_path is None:
                display_path = str(file_path).replace('\\', '/')
            else:
                display_path = str(relative_path).replace('\\', '/')
                
            variables = self.extract_variables_from_file(file_path)
            
            if variables:
                logger.info(f"Processing file: {display_path} ({len(variables)} variables found)")
                
                for variable in sorted(variables):
                    exists = self.check_variable_exists(variable)
                    report.append((display_path, variable, exists))
                    total_variables += 1
        
        logger.info(f"Total variables processed: {total_variables}")
        return report
    
    def print_report(self):
        """Print the complete report with formatted output."""
        logger.info("=" * 80)
        logger.info("HELM VARIABLE REFERENCE CHECKER REPORT")
        logger.info("=" * 80)
        logger.info(f"Helm Charts Paths: {', '.join(self.helm_charts_paths)}")
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
    
    # Create mutually exclusive group for chart path options
    path_group = parser.add_mutually_exclusive_group(required=True)
    path_group.add_argument(
        '--helm-charts-path',
        help='Path to the directory containing Helm charts'
    )
    path_group.add_argument(
        '--bom-file',
        help='Path to BOM file containing workloadList with helm.chartPath entries'
    )
    
    parser.add_argument(
        '--values-file',
        required=True,
        help='Path to the values YAML file (e.g., values-dev.yaml)'
    )
    
    args = parser.parse_args()
    
    # Determine chart paths based on input method
    chart_paths = []
    
    if args.helm_charts_path:
        # Single chart path provided
        helm_charts_path = Path(args.helm_charts_path)
        if not helm_charts_path.exists():
            logger.error(f"Helm charts directory does not exist: {helm_charts_path}")
            return 1
        if not helm_charts_path.is_dir():
            logger.error(f"Helm charts path is not a directory: {helm_charts_path}")
            return 1
        # Keep the original path as provided (relative if given as relative)
        chart_paths = [args.helm_charts_path]
        
    elif args.bom_file:
        # BOM file provided - extract chart paths
        bom_file_path = Path(args.bom_file)
        if not bom_file_path.exists():
            logger.error(f"BOM file does not exist: {bom_file_path}")
            return 1
        if not bom_file_path.is_file():
            logger.error(f"BOM path is not a file: {bom_file_path}")
            return 1
            
        chart_paths = HelmVariableChecker.parse_bom_file(str(bom_file_path))
        if not chart_paths:
            logger.error("No valid Helm chart paths found in BOM file")
            return 1
            
        # Validate all chart paths from BOM
        for chart_path in chart_paths:
            path_obj = Path(chart_path)
            if not path_obj.exists():
                logger.error(f"Helm charts directory from BOM does not exist: {chart_path}")
                return 1
            if not path_obj.is_dir():
                logger.error(f"Helm charts path from BOM is not a directory: {chart_path}")
                return 1
    
    # Validate values file
    values_file_path = Path(args.values_file)
    if not values_file_path.exists():
        logger.error(f"Values file does not exist: {args.values_file}")
        return 1
    if not values_file_path.is_file():
        logger.error(f"Values path is not a file: {args.values_file}")
        return 1
    
    # Create checker and run report (keeping original relative path)
    checker = HelmVariableChecker(chart_paths, args.values_file)
    checker.print_report()
    
    return 0


if __name__ == "__main__":
    exit(main())
