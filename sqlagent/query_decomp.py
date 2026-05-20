"""
Query Decomposition Module

This module uses Groq API to break down natural language questions into
structured SQL query components (intent, tables, columns, filters, joins).
"""

import json
import os
from typing import Dict, Any, Optional
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class QueryDecomposer:
    """Decomposes natural language queries into structured components."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize Groq client.
        
        Args:
            api_key: Groq API key (if None, uses GROQ_API_KEY env var)
            model: Model to use for decomposition
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found. Set it in .env or pass as argument.")
        
        self.client = Groq(api_key=self.api_key)
        self.model = model
    
    def decompose_query(self, question: str, schema_context: Optional[str] = None) -> Dict[str, Any]:
        """
        Decompose a natural language question into structured SQL components.
        
        Args:
            question: Natural language question
            schema_context: Optional database schema context for better decomposition
            
        Returns:
            Dictionary with decomposed query components:
            - intent: What is being asked
            - tables: Tables involved
            - columns: Specific columns needed
            - filters: Conditions/WHERE clauses
            - joins: Required joins
            - aggregate: Any aggregation functions needed
            - order_by: Any ordering requirements
        """
        
        # Build the prompt
        system_prompt = """You are a SQL query expert that breaks down natural language questions 
into structured SQL query components. 

For each question, provide a JSON response with these exact fields:
{
    "intent": "What is being asked (e.g., count, retrieve, find, list, calculate)",
    "tables": ["list", "of", "table", "names"],
    "columns": ["specific", "columns", "needed"],
    "filters": [{"column": "name", "condition": "condition", "value": "value"}],
    "joins": [{"table1": "name", "table2": "name", "on": "join_condition"}],
    "aggregate": "COUNT, SUM, AVG, MAX, MIN, or null",
    "order_by": [{"column": "name", "direction": "ASC or DESC"}],
    "notes": "Any additional context or clarifications"
}

Be concise and accurate. Return only valid JSON."""
        
        user_prompt = f"""Decompose this question into SQL components:

Question: {question}"""
        
        if schema_context:
            user_prompt += f"\n\nDatabase Schema Context:\n{schema_context}"
        
        user_prompt += "\n\nRespond with ONLY valid JSON, no additional text."
        
        try:
            # Call Groq API using correct method structure
            message = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1024
            )
            
            # Extract response - Groq uses choices[0].message.content
            response_text = message.choices[0].message.content
            
            # Parse JSON response
            decomposition = json.loads(response_text)
            return decomposition
            
        except json.JSONDecodeError as e:
            return {
                "error": "Failed to parse API response as JSON",
                "raw_response": response_text,
                "details": str(e)
            }
        except Exception as e:
            return {
                "error": f"Failed to decompose query: {str(e)}",
                "details": str(e)
            }
    
    def decompose_multiple(self, questions: list, schema_context: Optional[str] = None) -> list:
        """
        Decompose multiple questions at once.
        
        Args:
            questions: List of natural language questions
            schema_context: Optional database schema context
            
        Returns:
            List of decomposed query components
        """
        results = []
        for question in questions:
            decomposition = self.decompose_query(question, schema_context)
            results.append({
                "question": question,
                "decomposition": decomposition
            })
        return results
    
    def format_decomposition(self, decomposition: Dict[str, Any]) -> str:
        """
        Format decomposition for display.
        
        Args:
            decomposition: Decomposed query components
            
        Returns:
            Formatted string representation
        """
        if "error" in decomposition:
            return f"Error: {decomposition['error']}\nDetails: {decomposition.get('details', 'N/A')}"
        
        output = []
        output.append("Query Decomposition:")
        output.append("-" * 50)
        output.append(f"Intent: {decomposition.get('intent', 'N/A')}")
        output.append(f"Tables: {', '.join(decomposition.get('tables', []))}")
        output.append(f"Columns: {', '.join(decomposition.get('columns', []))}")
        
        if decomposition.get('filters'):
            output.append("\nFilters:")
            for f in decomposition['filters']:
                output.append(f"  - {f.get('column')}: {f.get('condition')} {f.get('value')}")
        
        if decomposition.get('joins'):
            output.append("\nJoins:")
            for j in decomposition['joins']:
                output.append(f"  - {j.get('table1')} → {j.get('table2')} on {j.get('on')}")
        
        if decomposition.get('aggregate'):
            output.append(f"\nAggregation: {decomposition['aggregate']}")
        
        if decomposition.get('order_by'):
            output.append("\nOrder By:")
            for o in decomposition['order_by']:
                output.append(f"  - {o.get('column')} {o.get('direction')}")
        
        if decomposition.get('notes'):
            output.append(f"\nNotes: {decomposition['notes']}")
        
        return "\n".join(output)


# Example usage
if __name__ == "__main__":
    # Sample database schema for context
    schema = """
    Tables:
    - customers: customerNumber, customerName, country, city, state, contactFirstName, contactLastName
    - orders: orderNumber, orderDate, requiredDate, shippedDate, status, customerNumber
    - orderdetails: orderNumber, productCode, quantityOrdered, priceEach
    - products: productCode, productName, productLine, quantityInStock
    """
    
    # Initialize decomposer
    decomposer = QueryDecomposer()
    
    # Test questions
    test_questions = [
        "How many customers are from the USA?",
        "Which products have the highest quantity in stock?",
        "What are the total sales by country for the year 2024?",
    ]
    
    print("Query Decomposition Examples")
    print("=" * 60)
    
    for question in test_questions:
        print(f"\nQuestion: {question}")
        print("-" * 60)
        
        decomposition = decomposer.decompose_query(question, schema)
        formatted = decomposer.format_decomposition(decomposition)
        print(formatted)
        print()
