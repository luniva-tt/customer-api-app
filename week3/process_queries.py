#!/usr/bin/env python
"""
Process SQL questions using Query Decomposer and save results to CSV.
"""

import csv
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main():
    """Process all questions from csv and create decomposition output."""
    
    # Input and output paths
    input_csv = "sql_questions_only.csv"
    output_csv = "query_decompositions.csv"
    
    if not os.path.exists(input_csv):
        print(f"Error: {input_csv} not found")
        return
    
    print(f"Reading questions from: {input_csv}")
    
    # Read questions
    questions = []
    try:
        with open(input_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            questions = [row['question'] for row in reader if row['question'].strip()]
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    print(f"Loaded {len(questions)} questions")
    print()
    
    # Check API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        print("Error: GROQ_API_KEY not configured")
        return
    
    # Initialize decomposer
    try:
        from week3.query_decomp import QueryDecomposer
        decomposer = QueryDecomposer()
        print("QueryDecomposer initialized successfully")
        print()
    except Exception as e:
        print(f"Error initializing decomposer: {e}")
        return
    
    # Database schema context
    schema = """
    Tables:
    - customers (customerNumber, customerName, country, city, state, postalCode, contactFirstName, contactLastName, phone, salesRepEmployeeNumber, creditLimit)
    - orders (orderNumber, orderDate, requiredDate, shippedDate, status, customerNumber)
    - orderdetails (orderNumber, productCode, quantityOrdered, priceEach)
    - products (productCode, productName, productLine, productScale, productVendor, productDescription, quantityInStock, buyPrice, MSRP)
    - productlines (productLine, textDescription, htmlDescription, image)
    - employees (employeeNumber, firstName, lastName, extension, email, officeCode, reportsTo, jobTitle)
    - offices (officeCode, city, phone, addressLine1, addressLine2, state, country, postalCode, territory)
    - payments (customerNumber, checkNumber, paymentDate, amount)
    """
    
    # Process questions
    results = []
    print("Processing queries...")
    print("=" * 80)
    
    for i, question in enumerate(questions, 1):
        try:
            print(f"[{i}/{len(questions)}] Decomposing: {question[:60]}...")
            
            # Decompose
            decomposition = decomposer.decompose_query(question, schema)
            
            # Format result
            result = {
                'question': question,
                'intent': decomposition.get('intent', ''),
                'tables': json.dumps(decomposition.get('tables', [])),
                'columns': json.dumps(decomposition.get('columns', [])),
                'filters': json.dumps(decomposition.get('filters', [])),
                'joins': json.dumps(decomposition.get('joins', [])),
                'aggregate': decomposition.get('aggregate', ''),
                'order_by': json.dumps(decomposition.get('order_by', [])),
                'notes': decomposition.get('notes', ''),
                'error': decomposition.get('error', '')
            }
            results.append(result)
            
            # Show status
            if decomposition.get('error'):
                print(f"  WARNING: Error: {decomposition['error']}")
            else:
                print(f"  SUCCESS")
                
        except Exception as e:
            print(f"  EXCEPTION: {e}")
            result = {
                'question': question,
                'intent': '',
                'tables': '',
                'columns': '',
                'filters': '',
                'joins': '',
                'aggregate': '',
                'order_by': '',
                'notes': '',
                'error': str(e)
            }
            results.append(result)
    
    print("=" * 80)
    print()
    
    # Write results to CSV
    try:
        fieldnames = [
            'question', 'intent', 'tables', 'columns', 'filters', 'joins',
            'aggregate', 'order_by', 'notes', 'error'
        ]
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"Results saved to: {output_csv}")
        print(f"   Total questions processed: {len(results)}")
        
        # Count successes and errors
        successes = sum(1 for r in results if not r['error'])
        errors = sum(1 for r in results if r['error'])
        
        print(f"   Successful decompositions: {successes}")
        print(f"   Errors: {errors}")
        
    except Exception as e:
        print(f"Error writing output CSV: {e}")
        return
    
    print()
    print("=" * 80)
    print("Processing Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()

