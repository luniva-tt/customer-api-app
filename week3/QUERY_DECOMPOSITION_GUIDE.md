# Query Decomposition Guide

This guide explains how to use the Query Decomposition module to break down natural language questions into structured SQL components.

## Overview

The Query Decomposition system uses Groq API (powered by Mixtral 8x7b) to intelligently parse natural language queries and extract:
- **Intent**: What is being asked (count, retrieve, find, list)
- **Tables**: Which tables to query
- **Columns**: Specific columns needed
- **Filters**: WHERE clause conditions
- **Joins**: Required table relationships
- **Aggregate**: COUNT, SUM, AVG, MAX, MIN
- **Order By**: Sorting requirements

## Setup

### 1. Get Groq API Key

1. Visit: https://console.groq.com/keys
2. Create a new API key or copy your existing key
3. Keep it secure (don't commit to git)

### 2. Update `.env` File

Open `.env` and replace the placeholder:

```env
GROQ_API_KEY=your_actual_groq_api_key_here
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Key packages:**
- `groq==0.9.0` - Groq API client
- `python-dotenv==1.0.0` - Environment variable management
- `httpx==0.25.2` - HTTP client (compatible with groq)

## Usage

### Quick Test

Run the test script to verify everything is configured:

```bash
python test_decomp.py
```

### Basic Usage

```python
from query_decomp import QueryDecomposer

# Initialize decomposer
decomposer = QueryDecomposer()

# Define database schema (optional but recommended)
schema = """
Tables:
- customers: customerNumber, customerName, country, city
- orders: orderNumber, orderDate, customerNumber, status
"""

# Decompose a question
question = "How many customers are from the USA?"
decomposition = decomposer.decompose_query(question, schema)

# Display results
formatted = decomposer.format_decomposition(decomposition)
print(formatted)
```

### Output Example

```
Query Decomposition:
--------------------------------------------------
Intent: Count total customers
Tables: customers
Columns: customerNumber
Filters:
  - country: = USA

Joins: None
Notes: Simple count query with single table filter
```

### Decompose Multiple Queries

```python
questions = [
    "How many customers are from the USA?",
    "Which products have the highest quantity in stock?",
    "What are the total sales by country for the year 2024?"
]

results = decomposer.decompose_multiple(questions, schema)

for result in results:
    print(f"Question: {result['question']}")
    print(decomposer.format_decomposition(result['decomposition']))
    print()
```

## File Structure

- **`query_decomp.py`** - Main decomposition module
  - `QueryDecomposer` class with core decomposition logic
  - `decompose_query()` - Decompose single question
  - `decompose_multiple()` - Decompose multiple questions
  - `format_decomposition()` - Format results for display

- **`config.py`** - Configuration management
  - Pydantic-based settings
  - Database and API configuration

- **`test_decomp.py`** - Test/validation script
  - Verifies API key configuration
  - Tests basic decomposition
  - Provides helpful error messages

- **`.env`** - Environment variables
  - `GROQ_API_KEY` - Your Groq API key
  - Database configuration

## API Response Format

The decomposer returns a dictionary with this structure:

```json
{
    "intent": "Count total customers",
    "tables": ["customers"],
    "columns": ["customerNumber"],
    "filters": [
        {
            "column": "country",
            "condition": "=",
            "value": "USA"
        }
    ],
    "joins": [],
    "aggregate": "COUNT",
    "order_by": [],
    "notes": "Simple aggregation query"
}
```

## Error Handling

### Missing API Key

```
❌ Error: GROQ_API_KEY not found
```

**Fix:**
1. Get your key from https://console.groq.com/keys
2. Add to `.env`: `GROQ_API_KEY=your_key`

### Connection Error

```
Failed to decompose query: [error details]
```

**Fix:**
- Check your internet connection
- Verify API key is valid
- Check Groq status: https://status.groq.com

### JSON Parse Error

If the API response can't be parsed as JSON:
- The response may contain markdown or extra text
- Check the `raw_response` field in the returned dictionary

## Integration with SQL Generation

The decomposition output can be used as input to SQL query generation:

```python
decomposition = decomposer.decompose_query(question)

# Use decomposition to build SQL
# Example: Convert to WHERE clause
if decomposition.get('filters'):
    where_clause = " AND ".join([
        f"{f['column']} {f['condition']} '{f['value']}'"
        for f in decomposition['filters']
    ])
```

## Best Practices

1. **Provide Schema Context** - Include table definitions for better decomposition
2. **Ask Clear Questions** - Natural language questions produce better results
3. **Cache Results** - For repeated questions, store decomposition results
4. **Handle Errors** - Always check for 'error' key in response
5. **Monitor Costs** - Each API call counts toward your Groq usage

## Troubleshooting

### Issue: "proxies" error
**Solution:** Update to compatible versions (already done in requirements.txt)

### Issue: API returns empty fields
**Solution:** Provide better schema context or more detailed question

### Issue: Rate limiting
**Solution:** Add delays between requests or use async processing

## Next Steps

1. ✅ Configure `.env` with your API key
2. ✅ Run `test_decomp.py` to verify setup
3. ✅ Use in your application
4. 🚀 Integrate with SQL query builder

## Support

- Groq Documentation: https://console.groq.com/docs
- API Status: https://status.groq.com
- Available Models: See Groq console for latest models
