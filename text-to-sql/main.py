#!/usr/bin/env python
"""
Main Text-to-SQL Pipeline
Orchestrates the full question-to-SQL-execution workflow
"""

import csv
import json
import os
import sys
import logging
from typing import List, Dict, Any
from pathlib import Path

from database import DatabaseConnection
from sql_generator import SQLGenerator
from executor import QueryExecutor

# Setup logging
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TextToSQLPipeline:
    """Main pipeline orchestrating the entire workflow."""
    
    def __init__(self):
        """Initialize pipeline components."""
        logger.info("Initializing Text-to-SQL Pipeline...")
        
        # Initialize database connection
        self.db = DatabaseConnection()
        if not self.db.connect():
            logger.error("Failed to connect to database")
            sys.exit(1)
        
        # Initialize SQL generator
        try:
            self.generator = SQLGenerator()
        except ValueError as e:
            logger.error(f"Failed to initialize generator: {e}")
            sys.exit(1)
        
        # Initialize executor
        self.executor = QueryExecutor(self.db, self.generator)
        
        # Get database schema
        logger.info("Fetching database schema...")
        self.schemas = self.db.get_all_schemas()
        self.schema_context = self._build_schema_context()
    
    def _build_schema_context(self) -> str:
        """
        Build schema context string for LLM.
        
        Returns:
            Formatted schema context
        """
        lines = ["Database Schema:"]
        
        for table_name, columns in self.schemas.items():
            col_str = ", ".join([f"{col} ({type_})" for col, type_ in columns.items()])
            lines.append(f"- {table_name}: {col_str}")
        
        return "\n".join(lines)
    
    def process_decomposition(self, decomposition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single decomposition through the pipeline.
        
        Args:
            decomposition: Structured query decomposition
            
        Returns:
            Execution result
        """
        
        question = decomposition.get("question", "Unknown")
        
        logger.info(f"Processing: {question[:60]}...")
        
        # Execute through full pipeline
        result = self.executor.execute(
            question,
            decomposition,
            self.schema_context
        )
        
        return result
    
    def process_csv(self, csv_path: str, output_path: str = "sql_results.csv"):
        """
        Process all decompositions from CSV file.
        
        Args:
            csv_path: Path to decompositions CSV
            output_path: Output CSV path
        """
        
        logger.info(f"Reading decompositions from: {csv_path}")
        
        if not os.path.exists(csv_path):
            logger.error(f"File not found: {csv_path}")
            return
        
        # Read decompositions
        decompositions = []
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Parse JSON fields
                    decomp = {
                        "question": row.get("question", ""),
                        "intent": row.get("intent", ""),
                        "tables": json.loads(row.get("tables", "[]")),
                        "columns": json.loads(row.get("columns", "[]")),
                        "filters": json.loads(row.get("filters", "[]")),
                        "joins": json.loads(row.get("joins", "[]")),
                        "aggregate": row.get("aggregate", ""),
                        "order_by": json.loads(row.get("order_by", "[]")),
                        "notes": row.get("notes", ""),
                        "error": row.get("error", "")
                    }
                    decompositions.append(decomp)
        
        except Exception as e:
            logger.error(f"Error reading CSV: {e}")
            return
        
        logger.info(f"Loaded {len(decompositions)} decompositions")
        
        # Process each decomposition
        results = []
        for i, decomp in enumerate(decompositions, 1):
            
            # Skip if decomposition had errors
            if decomp.get("error"):
                logger.warning(f"[{i}] Skipping due to decomposition error: {decomp['error'][:50]}")
                result = {
                    "question": decomp["question"],
                    "sql": "",
                    "result": [],
                    "status": "skipped_decomp_error",
                    "error": decomp["error"],
                    "column_names": [],
                    "row_count": 0
                }
                results.append(result)
                continue
            
            try:
                print(f"[{i}/{len(decompositions)}] {decomp['question'][:50]}...")
                result = self.process_decomposition(decomp)
                results.append(result)
            
            except Exception as e:
                logger.exception(f"Error processing decomposition {i}")
                result = {
                    "question": decomp["question"],
                    "sql": "",
                    "result": [],
                    "status": "exception",
                    "error": str(e),
                    "column_names": [],
                    "row_count": 0
                }
                results.append(result)
        
        # Write results to CSV
        self._write_results_csv(results, output_path)
        
        # Print statistics
        self._print_stats(results)
    
    def _write_results_csv(self, results: List[Dict[str, Any]], output_path: str):
        """
        Write results to CSV file.
        
        Args:
            results: List of execution results
            output_path: Output file path
        """
        
        try:
            fieldnames = [
                'question', 'status', 'sql', 'row_count', 'error', 'column_names'
            ]
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in results:
                    writer.writerow({
                        'question': result.get('question', ''),
                        'status': result.get('status', ''),
                        'sql': result.get('sql', ''),
                        'row_count': result.get('row_count', 0),
                        'error': result.get('error', ''),
                        'column_names': json.dumps(result.get('column_names', []))
                    })
            
            logger.info(f"Results saved to: {output_path}")
        
        except Exception as e:
            logger.error(f"Error writing results CSV: {e}")
    
    def _print_stats(self, results: List[Dict[str, Any]]):
        """
        Print execution statistics.
        
        Args:
            results: List of execution results
        """
        
        stats = {
            "total": len(results),
            "success": 0,
            "success_on_retry": 0,
            "failed": 0,
            "total_rows": 0
        }
        
        for result in results:
            status = result.get('status', '')
            if status == 'success':
                stats['success'] += 1
            elif status == 'success_on_retry':
                stats['success_on_retry'] += 1
            else:
                stats['failed'] += 1
            
            stats['total_rows'] += result.get('row_count', 0)
        
        print("\n" + "=" * 80)
        print("PIPELINE EXECUTION STATISTICS")
        print("=" * 80)
        print(f"Total Queries:        {stats['total']}")
        print(f"Successful:           {stats['success']} ({100*stats['success']//stats['total']}%)")
        print(f"Success on Retry:     {stats['success_on_retry']}")
        print(f"Failed:               {stats['failed']}")
        print(f"Total Rows Retrieved: {stats['total_rows']}")
        print("=" * 80)
    
    def cleanup(self):
        """Cleanup resources."""
        self.db.disconnect()
        logger.info("Pipeline cleanup complete")


def main(input_file=None, output_file=None):
    """
    Main entry point.
    
    Args:
        input_file: Path to input CSV (optional, can pass as command-line arg)
        output_file: Path to output CSV (optional, defaults to sql_results.csv)
    """
    
    # Support command-line arguments
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    # Set defaults
    if not input_file:
        input_file = "../week3/query_decompositions.csv"
    
    if not output_file:
        output_file = "sql_results.csv"
    
    print(f"Input file:  {input_file}")
    print(f"Output file: {output_file}")
    print()
    
    # Initialize pipeline
    pipeline = TextToSQLPipeline()
    
    # Check if input file exists
    if not os.path.exists(input_file):
        # Try alternative paths
        alt_paths = [
            "test_decomp.csv",
            "query_decompositions.csv",
            f"e:\\AI Fellow\\customer-api-app\\text-to-sql\\{os.path.basename(input_file)}",
        ]
        
        found = False
        for alt_path in alt_paths:
            if os.path.exists(alt_path):
                input_file = alt_path
                found = True
                logger.info(f"Found input file at: {alt_path}")
                break
        
        if not found:
            print(f"Error: Could not find decompositions file")
            print(f"Tried: {input_file}")
            for alt in alt_paths:
                print(f"  - {alt}")
            pipeline.cleanup()
            return
    
    # Process CSV
    pipeline.process_csv(input_file, output_file)
    
    # Cleanup
    pipeline.cleanup()
    
    print(f"\nResults saved to: {output_file}")
    print(f"Logs saved to: logs/")


if __name__ == "__main__":
    main("test_decomp.csv","test_result.csv")
