"""
Tests for the operation sequence metamodel with Pure Relation backend.
"""
import unittest
from cloud_dataframe.core.dataframe import DataFrame, Sort
from cloud_dataframe.type_system.column import col, literal, count, avg, sum


class TestPureRelationOperationSequence(unittest.TestCase):
    """Test cases for Pure Relation backend with operation sequence."""
    
    def test_operation_order_simple(self):
        """Test that operation order is respected in simple cases."""
        df = DataFrame.from_("employees")
        df = df.limit(10)  # Normally comes last in SQL
        df = df.select(lambda x: x.id, lambda x: x.name)
        df = df.filter(lambda x: x.id > 5)
        
        code = df.to_sql(dialect="pure_relation")
        
        expected = "$employees->limit(10)->select(~[id, name])->filter(x | $x.id > 5)"
        self.assertEqual(expected, code.strip())
    
    def test_operation_order_complex(self):
        """Test that operation order is respected in complex cases."""
        df = DataFrame.from_("employees")
        df = df.limit(20)
        df = df.select(lambda x: x.id, lambda x: x.name, lambda x: x.department_id, lambda x: x.salary)
        df = df.filter(lambda x: x.salary > 50000)
        df = df.group_by(lambda x: x.department_id)
        df = df.order_by(lambda x: x.salary, "DESC")
        
        code = df.to_sql(dialect="pure_relation")
        
        expected = "$employees->limit(20)->select(~[id, name, department_id, salary])->filter(x | $x.salary > 50000)->groupBy(~[department_id])->sort(descending(~salary))"
        self.assertEqual(expected, code.strip())
    
    def test_operation_order_with_join(self):
        """Test that operation order is respected with joins."""
        employees = DataFrame.from_("employees")
        departments = DataFrame.from_("departments")
        
        df = employees.join(
            departments, 
            lambda e, d: e.department_id == d.id
        )
        df = df.limit(5)  # Limit before select
        df = df.select(lambda x: x.name, lambda x: x.department_name)
        df = df.filter(lambda x: x.salary > 60000)
        
        code = df.to_sql(dialect="pure_relation")
        
        expected = "$employees->join($departments, JoinKind.INNER, {x, y | $x.department_id == $y.id})->limit(5)->select(~[name, department_name])->filter(x | $x.salary > 60000)"
        self.assertEqual(expected, code.strip())
    
    def test_operation_order_with_aggregation(self):
        """Test that operation order is respected with aggregation."""
        df = DataFrame.from_("employees")
        df = df.select(lambda x: x.department_id, lambda x: count(x.id).as_("employee_count"))
        df = df.group_by(lambda x: x.department_id)  # Group by after select
        df = df.having(lambda x: x.employee_count > 5)  # Having after group by
        df = df.order_by(lambda x: x.employee_count, "DESC")
        
        code = df.to_sql(dialect="pure_relation")
        
        expected = "$employees->select(~[department_id, x | $x.id->count() AS \"employee_count\"])->groupBy(~[department_id])->having(x | $x.employee_count > 5)->sort(descending(~employee_count))"
        self.assertEqual(expected, code.strip())
    
    def test_operation_order_with_window_functions(self):
        """Test that operation order is respected with window functions."""
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
        df = df.filter(lambda x: x.salary_rank <= 2)  # Filter after window function
        
        code = df.to_sql(dialect="pure_relation")
        
        expected = "$employees->select(~[id, name, department_id, salary, x | $x->rowNumber()->over(partitionBy(~[department_id]), orderBy(descending(~salary))) AS \"salary_rank\"])->filter(x | $x.salary_rank <= 2)"
        self.assertEqual(expected, code.strip())
    
    def test_operation_order_with_distinct(self):
        """Test that operation order is respected with distinct."""
        df = DataFrame.from_("employees")
        df = df.select(lambda x: x.department_id)
        df = df.distinct_rows()  # Distinct after select
        df = df.order_by(lambda x: x.department_id)  # Order by after distinct
        
        code = df.to_sql(dialect="pure_relation")
        
        expected = "$employees->select(~[department_id])->distinct()->sort(ascending(~department_id))"
        self.assertEqual(expected, code.strip())
    
    def test_operation_order_with_ctes(self):
        """Test that operation order is respected with CTEs."""
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
            lambda d: d.name,
            lambda dc: dc.employee_count
        )
        df = df.filter(lambda x: x.employee_count > 3)  # Filter after join with CTE
        
        code = df.to_sql(dialect="pure_relation")
        
        expected = "let dept_counts = $employees->groupBy(~[department_id])->select(~[department_id, x | $x.id->count() AS \"employee_count\"]);\n$departments->join($dept_counts, JoinKind.INNER, {x, y | $x.id == $y.department_id})->select(~[name, employee_count])->filter(x | $x.employee_count > 3)"
        self.assertEqual(expected, code.strip())
    
    def test_operation_order_with_offset(self):
        """Test that operation order is respected with offset."""
        df = DataFrame.from_("employees")
        df = df.order_by(lambda x: x.salary, "DESC")
        df = df.offset(5)  # Offset before limit
        df = df.limit(10)
        
        code = df.to_sql(dialect="pure_relation")
        
        expected = "$employees->sort(descending(~salary))->drop(5)->limit(10)"
        self.assertEqual(expected, code.strip())
    
    def test_operation_order_with_qualify(self):
        """Test that operation order is respected with qualify."""
        df = DataFrame.from_("employees")
        df = df.select(
            lambda x: x.id,
            lambda x: x.name,
            lambda x: x.department_id,
            lambda x: x.salary
        )
        df = df.qualify(lambda x: x.row_number().over(
            partition_by=lambda x: x.department_id,
            order_by=lambda x: x.salary.desc()
        ) <= 2)
        df = df.filter(lambda x: x.salary > 50000)  # Filter after qualify
        
        code = df.to_sql(dialect="pure_relation")
        
        expected = "$employees->select(~[id, name, department_id, salary])->filter(x | $x->rowNumber()->over(partitionBy(~[department_id]), orderBy(descending(~salary))) <= 2)->filter(x | $x.salary > 50000)"
        self.assertEqual(expected, code.strip())
