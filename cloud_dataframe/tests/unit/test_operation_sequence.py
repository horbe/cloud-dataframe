"""
Tests for the operation sequence metamodel.
"""
import unittest
from cloud_dataframe.core.dataframe import DataFrame
from cloud_dataframe.core.operations import (
    Operation, FromTableOperation, SelectOperation, FilterOperation,
    GroupByOperation, HavingOperation, QualifyOperation, OrderByOperation, 
    LimitOperation, OffsetOperation, DistinctOperation, JoinOperation
)


class TestOperationSequence(unittest.TestCase):
    """Test cases for the operation sequence metamodel."""
    
    def test_basic_operation_sequence(self):
        """Test that operations are properly sequenced."""
        df = DataFrame.from_("employees")
        
        df = df.filter(lambda x: x.salary > 50000)
        df = df.select(lambda x: x.id, lambda x: x.name, lambda x: x.salary)
        df = df.order_by(lambda x: x.salary)
        df = df.limit(10)
        
        operations = df.get_operation_sequence_list()
        
        self.assertEqual(5, len(operations))
        self.assertIsInstance(operations[0], FromTableOperation)
        self.assertIsInstance(operations[1], FilterOperation)
        self.assertIsInstance(operations[2], SelectOperation)
        self.assertIsInstance(operations[3], OrderByOperation)
        self.assertIsInstance(operations[4], LimitOperation)
        
        self.assertIsNone(operations[0].previous_operation)
        self.assertEqual(operations[0], operations[1].previous_operation)
        self.assertEqual(operations[1], operations[2].previous_operation)
        self.assertEqual(operations[2], operations[3].previous_operation)
        self.assertEqual(operations[3], operations[4].previous_operation)
    
    def test_complex_operation_sequence(self):
        """Test a more complex operation sequence with group by and having."""
        df = DataFrame.from_("employees")
        
        df = df.filter(lambda x: x.department_id.is_not_null())
        df = df.group_by(lambda x: x.department_id)
        df = df.having(lambda x: x.salary.avg() > 60000)
        df = df.select(lambda x: x.department_id, lambda x: x.salary.avg().as_("avg_salary"))
        df = df.order_by(lambda x: x.avg_salary, "DESC")
        
        operations = df.get_operation_sequence_list()
        
        self.assertEqual(6, len(operations))
        self.assertIsInstance(operations[0], FromTableOperation)
        self.assertIsInstance(operations[1], FilterOperation)
        self.assertIsInstance(operations[2], GroupByOperation)
        self.assertIsInstance(operations[3], HavingOperation)
        self.assertIsInstance(operations[4], SelectOperation)
        self.assertIsInstance(operations[5], OrderByOperation)
    
    def test_join_operation_sequence(self):
        """Test operation sequence with joins."""
        employees = DataFrame.from_("employees")
        departments = DataFrame.from_("departments")
        
        df = employees.join(
            departments, 
            lambda e, d: e.department_id == d.id
        )
        
        df = df.select(lambda x: x.name, lambda x: x.department_name)
        df = df.filter(lambda x: x.salary > 50000)
        
        operations = df.get_operation_sequence_list()
        
        self.assertEqual(4, len(operations))
        self.assertIsInstance(operations[0], FromTableOperation)  # employees
        self.assertIsInstance(operations[1], JoinOperation)
        self.assertIsInstance(operations[2], SelectOperation)
        self.assertIsInstance(operations[3], FilterOperation)
    
    def test_distinct_operation_sequence(self):
        """Test operation sequence with distinct."""
        df = DataFrame.from_("employees")
        
        df = df.select(lambda x: x.department_id)
        df = df.distinct_rows()
        
        operations = df.get_operation_sequence_list()
        
        self.assertEqual(3, len(operations))
        self.assertIsInstance(operations[0], FromTableOperation)
        self.assertIsInstance(operations[1], SelectOperation)
        self.assertIsInstance(operations[2], DistinctOperation)
    
    def test_qualify_operation_sequence(self):
        """Test operation sequence with qualify."""
        df = DataFrame.from_("employees")
        
        df = df.select(lambda x: x.id, lambda x: x.name, lambda x: x.department_id, lambda x: x.salary)
        df = df.qualify(lambda x: x.row_number().over(
            partition_by=lambda x: x.department_id,
            order_by=lambda x: x.salary.desc()
        ) <= 3)
        
        operations = df.get_operation_sequence_list()
        
        self.assertEqual(3, len(operations))
        self.assertIsInstance(operations[0], FromTableOperation)
        self.assertIsInstance(operations[1], SelectOperation)
        self.assertIsInstance(operations[2], QualifyOperation)
    
    def test_sql_respects_operation_order_duckdb(self):
        """Test that DuckDB SQL generation respects operation order."""
        df = DataFrame.from_("employees")
        df = df.limit(10)  # Normally comes last in SQL
        df = df.select(lambda x: x.id, lambda x: x.name)
        df = df.filter(lambda x: x.id > 5)  # Normally comes before GROUP BY
        df = df.group_by(lambda x: x.department_id)
        
        sql = df.to_sql(dialect="duckdb")
        
        expected_sql = """SELECT x.id, x.name
FROM employees AS x
LIMIT 10
WHERE x.id > 5
GROUP BY x.department_id"""
        
        self.assertEqual(sql.strip(), expected_sql.strip(), 
                         "SQL should respect the exact operation order as defined in the DataFrame operations")
    
    def test_sql_respects_operation_order_pure_relation(self):
        """Test that Pure Relation code generation respects operation order."""
        df = DataFrame.from_("employees")
        df = df.limit(10)  # Normally comes last in SQL
        df = df.select(lambda x: x.id, lambda x: x.name)
        df = df.filter(lambda x: x.id > 5)
        
        code = df.to_sql(dialect="pure_relation")
        
        expected_code = "$employees->limit(10)->select(~[id, name])->filter(x | $x.id > 5)"
        
        self.assertEqual(code.strip(), expected_code.strip(),
                         "Pure Relation code should respect the exact operation order as defined in the DataFrame operations")
