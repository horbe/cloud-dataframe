# Pure Relation Operation Sequence REPL Test Cases

## Test Cases to Implement

1. [x] Basic operation sequence with REPL
   - Test simple operations (select, filter, limit) in non-standard order
   - Verify generated Pure code matches expected format
   - Simulate REPL execution and result validation

2. [x] Complex operation sequence with REPL
   - Test join, select, filter, limit in non-standard order
   - Verify generated Pure code matches expected format
   - Simulate REPL execution and result validation

3. [x] Aggregation operation sequence with REPL
   - Test select with aggregation functions, group by, order by in non-standard order
   - Verify generated Pure code matches expected format
   - Simulate REPL execution and result validation

4. [x] Filter after group by with REPL
   - Test select with aggregation, group by, filter in non-standard order
   - Verify generated Pure code matches expected format
   - Simulate REPL execution and result validation

5. [x] Window functions with REPL
   - Test select with window functions, filter, order by in non-standard order
   - Verify generated Pure code matches expected format
   - Simulate REPL execution and result validation

6. [x] Distinct operation sequence with REPL
   - Test select, distinct, order by in non-standard order
   - Verify generated Pure code matches expected format
   - Simulate REPL execution and result validation

7. [x] CTE operation sequence with REPL
   - Test CTE creation and usage in non-standard operation order
   - Verify generated Pure code matches expected format
   - Simulate REPL execution and result validation

8. [x] Offset and limit operation sequence with REPL
   - Test offset before limit in non-standard order
   - Verify generated Pure code matches expected format
   - Simulate REPL execution and result validation

## Implementation Notes

- All tests should create test data in a temporary directory
- Tests should simulate REPL execution and result validation
- Each test should verify that operation order is respected in the generated Pure code
- Tests should follow the pattern in test_sql_respects_operation_order_pure_relation
