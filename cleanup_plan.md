# Cloud DataFrame Code Cleanup Plan

## High Priority (Critical Functionality Issues)

1. **Fix Type Errors in DataFrame Class**
   - Fix `extend` method type errors when handling Expression vs Column objects
   - Fix `filter` method issues with BinaryOperation vs FilterCondition
   - Fix `having` and `qualify` methods type errors with parameter handling
   - Ensure consistent type handling throughout the codebase

2. **Implement Missing Backend Features**
   - Add QUALIFY support to pure_relation backend
   - Add CTE (Common Table Expression) support to pure_relation backend
   - Add OFFSET support to pure_relation backend
   - Ensure consistent feature support across all backends

3. **Fix Attribute Access Issues**
   - Fix non-existent `column_alias` attribute access in DuckDB SQL generator
   - Ensure all attribute accesses are properly checked with hasattr()

## Medium Priority (Code Quality Improvements)

4. **Reduce Code Duplication**
   - Refactor similar code in `having` and `qualify` methods
   - Create helper functions for repeated type checking and conversion logic
   - Standardize error handling across similar methods

5. **Improve Type Hints**
   - Replace broad `Any` types with more specific types
   - Add proper return type annotations to all functions
   - Use Union types instead of Any where appropriate

6. **Enable Validation**
   - Implement the disabled `_validate_select_vs_groupby` function
   - Add proper validation for GROUP BY vs SELECT columns
   - Add validation for other SQL constraints

## Low Priority (Style and Documentation)

7. **Standardize Code Style**
   - Add linting configuration (.flake8, pyproject.toml)
   - Standardize docstring format across all files
   - Ensure consistent naming conventions

8. **Improve Documentation**
   - Add more detailed docstrings to complex methods
   - Add examples to docstrings where helpful
   - Update README with more detailed usage examples

9. **Add Development Tools**
   - Add dev dependencies for linting (flake8, pylint)
   - Add type checking with mypy
   - Add code formatting with black and isort

## Implementation Approach

1. **Start with Automated Fixes**
   - Install and configure linting tools
   - Run auto-fixers where possible

2. **Group Similar Issues**
   - Address type errors systematically
   - Fix backend feature implementations together

3. **Prioritize Critical Functionality**
   - Focus first on issues that affect core functionality
   - Ensure all tests pass after each change

4. **Document Exceptions**
   - Add comments for any necessary exceptions to style rules
   - Document complex logic that might appear unusual

5. **Add Tests**
   - Add tests for any fixed bugs
   - Ensure all features have proper test coverage
