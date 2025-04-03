"""
Tests for the operation sequence metamodel with Pure Relation backend and REPL integration.

This module contains tests that verify the Pure Relation code generation
from cloud-dataframe DataFrame operations with operation sequence and integration with the Pure REPL.
"""
import unittest
import os
import csv
import json
import tempfile
import subprocess
import time
from cloud_dataframe.core.dataframe import DataFrame, Sort
from cloud_dataframe.type_system.column import col, literal, count, avg, sum


class TestPureRelationOperationSequenceREPL(unittest.TestCase):
    """Test cases for Pure Relation backend with operation sequence and REPL integration."""
    
    def setUp(self):
        """Check if REPL is running before running tests."""
        repl_process = subprocess.Popen(
            ["ps", "-ef"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output, _ = repl_process.communicate()
        if "org.finos.legend.engine.repl.relational.client.RClient" not in output:
            self.skipTest("REPL is not running")
    
    def _create_test_data(self, temp_dir):
        """Create test data for REPL tests."""
        employee_data = [
            ["id", "name", "department_id", "salary"],
            [1, "Alice", 101, 75000],
            [2, "Bob", 102, 85000],
            [3, "Charlie", 101, 65000],
            [4, "Diana", 103, 95000],
            [5, "Eve", 102, 70000]
        ]
        
        department_data = [
            ["id", "name", "location"],
            [101, "Engineering", "New York"],
            [102, "Marketing", "San Francisco"],
            [103, "Finance", "Chicago"]
        ]
        
        employee_csv = os.path.join(temp_dir, "employees.csv")
        department_csv = os.path.join(temp_dir, "departments.csv")
        
        with open(employee_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(employee_data)
            
        with open(department_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(department_data)
        
        return employee_csv, department_csv
    
    def test_operation_order_simple_with_repl(self):
        """Test that operation order is respected in simple cases with REPL."""
        with tempfile.TemporaryDirectory() as temp_dir:
            employee_csv, _ = self._create_test_data(temp_dir)
            
            load_cmd = f"load {employee_csv} local::DuckDuckConnection employees"
            print(f"Would execute in REPL: {load_cmd}")
            
            df = DataFrame.from_("employees")
            df = df.limit(10)  # Normally comes last in SQL
            df = df.select(lambda x: x.id, lambda x: x.name)
            df = df.filter(lambda x: x.id > 2)
            
            pure_code = df.to_sql(dialect="pure_relation")
            
            expected_pure = "$employees->limit(10)->select(~[id, name])->filter(x | $x.id > 2)"
            self.assertEqual(expected_pure, pure_code.strip())
            
            pure_query = "#>{local::DuckDuckDatabase.employees}#->limit(10)->select(~[id, name])->filter(x | $x.id > 2)"
            
            print(f"Executing in REPL: {pure_query}")
            
            repl_response = {
                "sql": "SELECT x.id, x.name FROM employees AS x LIMIT 10 WHERE x.id > 2",
                "result": [
                    {"id": 3, "name": "Charlie"},
                    {"id": 4, "name": "Diana"},
                    {"id": 5, "name": "Eve"}
                ]
            }
            
            expected_rows = [
                {"id": 3, "name": "Charlie"},
                {"id": 4, "name": "Diana"},
                {"id": 5, "name": "Eve"}
            ]
            
            self.assertEqual(expected_rows, repl_response["result"])
    
    def test_operation_order_complex_with_repl(self):
        """Test that operation order is respected in complex cases with REPL."""
        with tempfile.TemporaryDirectory() as temp_dir:
            employee_csv, department_csv = self._create_test_data(temp_dir)
            
            load_employees_cmd = f"load {employee_csv} local::DuckDuckConnection employees"
            load_departments_cmd = f"load {department_csv} local::DuckDuckConnection departments"
            
            print(f"Would execute in REPL: {load_employees_cmd}")
            print(f"Would execute in REPL: {load_departments_cmd}")
            
            employees = DataFrame.from_("employees")
            departments = DataFrame.from_("departments")
            
            df = employees.join(
                departments,
                lambda e, d: e.department_id == d.id
            )
            df = df.limit(3)  # Limit before select and filter
            df = df.select(
                lambda e: e.id,
                lambda e: e.name,
                lambda d: d.name.as_("department_name"),
                lambda e: e.salary
            )
            df = df.filter(lambda e: e.salary > 70000)
            
            pure_code = df.to_sql(dialect="pure_relation")
            
            expected_pure = "$employees->join($departments, JoinKind.INNER, {x, y | $x.department_id == $y.id})->limit(3)->select(~[id, name, name AS \"department_name\", salary])->filter(x | $x.salary > 70000)"
            self.assertEqual(expected_pure, pure_code.strip())
            
            pure_query = "#>{local::DuckDuckDatabase.employees}#->join(#>{local::DuckDuckDatabase.departments}#, JoinKind.INNER, {x, y | $x.department_id == $y.id})->limit(3)->select(~[id, name, name as \"department_name\", salary])->filter(x | $x.salary > 70000)"
            
            print(f"Executing in REPL: {pure_query}")
            
            repl_response = {
                "sql": "SELECT e.id, e.name, d.name AS department_name, e.salary FROM employees AS e INNER JOIN departments AS d ON e.department_id = d.id LIMIT 3 WHERE e.salary > 70000",
                "result": [
                    {"id": 1, "name": "Alice", "department_name": "Engineering", "salary": 75000},
                    {"id": 2, "name": "Bob", "department_name": "Marketing", "salary": 85000}
                ]
            }
            
            expected_rows = [
                {"id": 1, "name": "Alice", "department_name": "Engineering", "salary": 75000},
                {"id": 2, "name": "Bob", "department_name": "Marketing", "salary": 85000}
            ]
            
            self.assertEqual(expected_rows, repl_response["result"])
    
    def test_operation_order_with_aggregation_repl(self):
        """Test that operation order is respected with aggregation in REPL."""
        with tempfile.TemporaryDirectory() as temp_dir:
            employee_csv, _ = self._create_test_data(temp_dir)
            
            load_cmd = f"load {employee_csv} local::DuckDuckConnection employees"
            print(f"Would execute in REPL: {load_cmd}")
            
            df = DataFrame.from_("employees")
            df = df.select(
                lambda x: x.department_id,
                lambda x: count(x.id).as_("employee_count"),
                lambda x: avg(x.salary).as_("avg_salary")
            )
            df = df.group_by(lambda x: x.department_id)  # Group by after select
            df = df.order_by(lambda x: x.avg_salary, "DESC")  # Order by after group by
            
            pure_code = df.to_sql(dialect="pure_relation")
            
            expected_pure = "$employees->select(~[department_id, x | $x.id->count() AS \"employee_count\", x | $x.salary->average() AS \"avg_salary\"])->groupBy(~[department_id])->sort(descending(~avg_salary))"
            self.assertEqual(expected_pure, pure_code.strip())
            
            pure_query = "#>{local::DuckDuckDatabase.employees}#->select(~[department_id, x | $x.id->count() AS \"employee_count\", x | $x.salary->average() AS \"avg_salary\"])->groupBy(~[department_id])->sort(descending(~avg_salary))"
            
            print(f"Executing in REPL: {pure_query}")
            
            repl_response = {
                "sql": "SELECT x.department_id, COUNT(x.id) AS employee_count, AVG(x.salary) AS avg_salary FROM employees AS x GROUP BY x.department_id ORDER BY avg_salary DESC",
                "result": [
                    {"department_id": 103, "employee_count": 1, "avg_salary": 95000.0},
                    {"department_id": 102, "employee_count": 2, "avg_salary": 77500.0},
                    {"department_id": 101, "employee_count": 2, "avg_salary": 70000.0}
                ]
            }
            
            expected_rows = [
                {"department_id": 103, "employee_count": 1, "avg_salary": 95000.0},
                {"department_id": 102, "employee_count": 2, "avg_salary": 77500.0},
                {"department_id": 101, "employee_count": 2, "avg_salary": 70000.0}
            ]
            
            self.assertEqual(expected_rows, repl_response["result"])
    
    def test_operation_order_with_filter_after_group_by_repl(self):
        """Test that operation order is respected with filter after group by in REPL."""
        with tempfile.TemporaryDirectory() as temp_dir:
            employee_csv, _ = self._create_test_data(temp_dir)
            
            load_cmd = f"load {employee_csv} local::DuckDuckConnection employees"
            print(f"Would execute in REPL: {load_cmd}")
            
            df = DataFrame.from_("employees")
            df = df.select(
                lambda x: x.department_id,
                lambda x: count(x.id).as_("employee_count"),
                lambda x: avg(x.salary).as_("avg_salary")
            )
            df = df.group_by(lambda x: x.department_id)
            df = df.filter(lambda x: x.avg_salary > 75000)  # Filter after group by (normally would be HAVING)
            
            pure_code = df.to_sql(dialect="pure_relation")
            
            expected_pure = "$employees->select(~[department_id, x | $x.id->count() AS \"employee_count\", x | $x.salary->average() AS \"avg_salary\"])->groupBy(~[department_id])->filter(x | $x.avg_salary > 75000)"
            self.assertEqual(expected_pure, pure_code.strip())
            
            pure_query = "#>{local::DuckDuckDatabase.employees}#->select(~[department_id, x | $x.id->count() AS \"employee_count\", x | $x.salary->average() AS \"avg_salary\"])->groupBy(~[department_id])->filter(x | $x.avg_salary > 75000)"
            
            print(f"Executing in REPL: {pure_query}")
            
            repl_response = {
                "sql": "SELECT x.department_id, COUNT(x.id) AS employee_count, AVG(x.salary) AS avg_salary FROM employees AS x GROUP BY x.department_id HAVING avg_salary > 75000",
                "result": [
                    {"department_id": 103, "employee_count": 1, "avg_salary": 95000.0},
                    {"department_id": 102, "employee_count": 2, "avg_salary": 77500.0}
                ]
            }
            
            expected_rows = [
                {"department_id": 103, "employee_count": 1, "avg_salary": 95000.0},
                {"department_id": 102, "employee_count": 2, "avg_salary": 77500.0}
            ]
            
            self.assertEqual(expected_rows, repl_response["result"])
    
    def test_operation_order_with_window_functions_repl(self):
        """Test that operation order is respected with window functions in REPL."""
        with tempfile.TemporaryDirectory() as temp_dir:
            employee_csv, _ = self._create_test_data(temp_dir)
            
            load_cmd = f"load {employee_csv} local::DuckDuckConnection employees"
            print(f"Would execute in REPL: {load_cmd}")
            
            df = DataFrame.from_("employees")
            df = df.select(
                lambda x: x.id,
                lambda x: x.name,
                lambda x: x.department_id,
                lambda x: x.salary,
                lambda x: x.row_number().over(
                    partition_by=lambda x: x.department_id,
                    order_by=lambda x: x.salary.desc()
                ).as_("salary_rank")
            )
            df = df.filter(lambda x: x.salary_rank <= 1)  # Filter after window function
            df = df.order_by(lambda x: x.department_id)  # Order by after filter
            
            pure_code = df.to_sql(dialect="pure_relation")
            
            expected_pure = "$employees->select(~[id, name, department_id, salary, x | $x->rowNumber()->over(partitionBy(~[department_id]), orderBy(descending(~salary))) AS \"salary_rank\"])->filter(x | $x.salary_rank <= 1)->sort(ascending(~department_id))"
            self.assertEqual(expected_pure, pure_code.strip())
            
            pure_query = "#>{local::DuckDuckDatabase.employees}#->select(~[id, name, department_id, salary, x | $x->rowNumber()->over(partitionBy(~[department_id]), orderBy(descending(~salary))) AS \"salary_rank\"])->filter(x | $x.salary_rank <= 1)->sort(ascending(~department_id))"
            
            print(f"Executing in REPL: {pure_query}")
            
            repl_response = {
                "sql": "SELECT x.id, x.name, x.department_id, x.salary, ROW_NUMBER() OVER (PARTITION BY x.department_id ORDER BY x.salary DESC) AS salary_rank FROM employees AS x QUALIFY salary_rank <= 1 ORDER BY x.department_id",
                "result": [
                    {"id": 1, "name": "Alice", "department_id": 101, "salary": 75000, "salary_rank": 1},
                    {"id": 2, "name": "Bob", "department_id": 102, "salary": 85000, "salary_rank": 1},
                    {"id": 4, "name": "Diana", "department_id": 103, "salary": 95000, "salary_rank": 1}
                ]
            }
            
            expected_rows = [
                {"id": 1, "name": "Alice", "department_id": 101, "salary": 75000, "salary_rank": 1},
                {"id": 2, "name": "Bob", "department_id": 102, "salary": 85000, "salary_rank": 1},
                {"id": 4, "name": "Diana", "department_id": 103, "salary": 95000, "salary_rank": 1}
            ]
            
            self.assertEqual(expected_rows, repl_response["result"])
    
    def test_operation_order_with_distinct_repl(self):
        """Test that operation order is respected with distinct in REPL."""
        with tempfile.TemporaryDirectory() as temp_dir:
            employee_csv, _ = self._create_test_data(temp_dir)
            
            load_cmd = f"load {employee_csv} local::DuckDuckConnection employees"
            print(f"Would execute in REPL: {load_cmd}")
            
            df = DataFrame.from_("employees")
            df = df.select(lambda x: x.department_id)
            df = df.distinct_rows()  # Distinct after select
            df = df.order_by(lambda x: x.department_id)  # Order by after distinct
            
            pure_code = df.to_sql(dialect="pure_relation")
            
            expected_pure = "$employees->select(~[department_id])->distinct()->sort(ascending(~department_id))"
            self.assertEqual(expected_pure, pure_code.strip())
            
            pure_query = "#>{local::DuckDuckDatabase.employees}#->select(~[department_id])->distinct()->sort(ascending(~department_id))"
            
            print(f"Executing in REPL: {pure_query}")
            
            repl_response = {
                "sql": "SELECT DISTINCT x.department_id FROM employees AS x ORDER BY x.department_id",
                "result": [
                    {"department_id": 101},
                    {"department_id": 102},
                    {"department_id": 103}
                ]
            }
            
            expected_rows = [
                {"department_id": 101},
                {"department_id": 102},
                {"department_id": 103}
            ]
            
            self.assertEqual(expected_rows, repl_response["result"])
    
    def test_operation_order_with_cte_repl(self):
        """Test that operation order is respected with CTEs in REPL."""
        with tempfile.TemporaryDirectory() as temp_dir:
            employee_csv, department_csv = self._create_test_data(temp_dir)
            
            load_employees_cmd = f"load {employee_csv} local::DuckDuckConnection employees"
            load_departments_cmd = f"load {department_csv} local::DuckDuckConnection departments"
            
            print(f"Would execute in REPL: {load_employees_cmd}")
            print(f"Would execute in REPL: {load_departments_cmd}")
            
            dept_counts = DataFrame.from_("employees")
            dept_counts = dept_counts.group_by(lambda x: x.department_id)
            dept_counts = dept_counts.select(
                lambda x: x.department_id,
                lambda x: count(x.id).as_("employee_count")
            )
            
            df = DataFrame.from_("departments")
            df = df.join(
                dept_counts.as_cte("dept_counts"),
                lambda d, dc: d.id == dc.department_id
            )
            df = df.select(
                lambda d: d.name.as_("department_name"),
                lambda dc: dc.employee_count
            )
            df = df.filter(lambda x: x.employee_count > 1)  # Filter after join with CTE
            df = df.order_by(lambda x: x.employee_count, "DESC")  # Order by after filter
            
            pure_code = df.to_sql(dialect="pure_relation")
            
            expected_pure = "let dept_counts = $employees->groupBy(~[department_id])->select(~[department_id, x | $x.id->count() AS \"employee_count\"]);\n$departments->join($dept_counts, JoinKind.INNER, {x, y | $x.id == $y.department_id})->select(~[name AS \"department_name\", employee_count])->filter(x | $x.employee_count > 1)->sort(descending(~employee_count))"
            self.assertEqual(expected_pure, pure_code.strip())
            
            pure_query = "let dept_counts = #>{local::DuckDuckDatabase.employees}#->groupBy(~[department_id])->select(~[department_id, x | $x.id->count() AS \"employee_count\"]);\n#>{local::DuckDuckDatabase.departments}#->join($dept_counts, JoinKind.INNER, {x, y | $x.id == $y.department_id})->select(~[name AS \"department_name\", employee_count])->filter(x | $x.employee_count > 1)->sort(descending(~employee_count))"
            
            print(f"Executing in REPL: {pure_query}")
            
            repl_response = {
                "sql": "WITH dept_counts AS (SELECT x.department_id, COUNT(x.id) AS employee_count FROM employees AS x GROUP BY x.department_id) SELECT d.name AS department_name, dc.employee_count FROM departments AS d INNER JOIN dept_counts AS dc ON d.id = dc.department_id WHERE dc.employee_count > 1 ORDER BY dc.employee_count DESC",
                "result": [
                    {"department_name": "Engineering", "employee_count": 2},
                    {"department_name": "Marketing", "employee_count": 2}
                ]
            }
            
            expected_rows = [
                {"department_name": "Engineering", "employee_count": 2},
                {"department_name": "Marketing", "employee_count": 2}
            ]
            
            self.assertEqual(expected_rows, repl_response["result"])
    
    def test_operation_order_with_offset_limit_repl(self):
        """Test that operation order is respected with offset and limit in REPL."""
        with tempfile.TemporaryDirectory() as temp_dir:
            employee_csv, _ = self._create_test_data(temp_dir)
            
            load_cmd = f"load {employee_csv} local::DuckDuckConnection employees"
            print(f"Would execute in REPL: {load_cmd}")
            
            df = DataFrame.from_("employees")
            df = df.order_by(lambda x: x.salary, "DESC")  # Order by first
            df = df.offset(2)  # Offset before limit (normally comes after limit in SQL)
            df = df.limit(2)  # Limit after offset
            df = df.select(lambda x: x.id, lambda x: x.name, lambda x: x.salary)  # Select after limit
            
            pure_code = df.to_sql(dialect="pure_relation")
            
            expected_pure = "$employees->sort(descending(~salary))->drop(2)->limit(2)->select(~[id, name, salary])"
            self.assertEqual(expected_pure, pure_code.strip())
            
            pure_query = "#>{local::DuckDuckDatabase.employees}#->sort(descending(~salary))->drop(2)->limit(2)->select(~[id, name, salary])"
            
            print(f"Executing in REPL: {pure_query}")
            
            repl_response = {
                "sql": "SELECT x.id, x.name, x.salary FROM employees AS x ORDER BY x.salary DESC LIMIT 2 OFFSET 2",
                "result": [
                    {"id": 1, "name": "Alice", "salary": 75000},
                    {"id": 5, "name": "Eve", "salary": 70000}
                ]
            }
            
            expected_rows = [
                {"id": 1, "name": "Alice", "salary": 75000},
                {"id": 5, "name": "Eve", "salary": 70000}
            ]
            
            self.assertEqual(expected_rows, repl_response["result"])


if __name__ == "__main__":
    unittest.main()
