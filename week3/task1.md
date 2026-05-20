Exact Match
Compare the generated SQL text to a reference SQL query character by character. This is too strict though. There are a million ways to write the same correct query. Different join styles, different aliases, different ordering. Exact match punishes creativity.

Query Results
Run both the generated query and the reference query on the same database. Compare the outputs. This is way better than exact match. But it still has issues. On a tiny database, a wrong query might accidentally return the right result.

Can It Handle Paraphrasing?
"Show me our top customers" and "who are our biggest buyers" should generate similar queries. Test this by rewording the same question five different ways and seeing if the agent stays consistent.

Does It Fail Gracefully?
What happens when you ask something that can't be answered? Either the data doesn't exist or the question is too vague. A good agent should say "I don't have information about that" instead of making something up. This is hard to test automatically though.

Does It Make Up Fake Columns?
A common failure is when the agent invents table or column names that don't exist in your schema. You can catch this by parsing the generated SQL and checking every table and column name against your actual database schema.

Is It Fast Enough?
If your agent takes 15 seconds per query and costs a dollar in API calls, it might be correct but unusable in practice.