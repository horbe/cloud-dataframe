"""
Operation metamodel for cloud-dataframe.

This module defines the base classes for operations that can be applied to dataframes.
Operations form a linked list, with each operation pointing to its predecessor,
allowing the operation sequence to be properly tracked.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, List, Optional, Union, Generic, TypeVar, Type, Dict

from ..type_system.column import Column, ColumnReference, Expression, LiteralExpression
from ..type_system.schema import TableSchema


@dataclass
class Operation(ABC):
    """
    Base class for all operations that can be applied to a dataframe.
    
    Each operation points to its predecessor, forming a linked list of operations
    that captures the sequence in which they were applied.
    """
    
    @abstractmethod
    def clone_with_previous(self, previous_operation: Optional[Operation]) -> Operation:
        """
        Create a copy of this operation with a new previous operation.
        
        Args:
            previous_operation: The operation that should precede this one
            
        Returns:
            A new operation instance with the specified previous operation
        """
        pass


@dataclass
class SourceOperation(Operation):
    """Base class for operations that define a data source."""
    pass


@dataclass
class FromTableOperation(SourceOperation):
    """Operation that defines a table source."""
    table_name: str
    previous_operation: Optional[Operation] = None
    schema: Optional[str] = None
    alias: Optional[str] = None
    table_schema: Optional[TableSchema] = None
    
    def clone_with_previous(self, previous_operation: Optional[Operation]) -> Operation:
        return FromTableOperation(
            table_name=self.table_name,
            previous_operation=previous_operation,
            schema=self.schema,
            alias=self.alias,
            table_schema=self.table_schema
        )


@dataclass
class DataOperation(Operation):
    """Base class for operations that manipulate data (non-source operations)."""
    pass


@dataclass
class SelectOperation(DataOperation):
    """Operation that selects columns."""
    columns: List[Column] = field(default_factory=list)
    previous_operation: Optional[Operation] = None
    
    def clone_with_previous(self, previous_operation: Optional[Operation]) -> Operation:
        return SelectOperation(
            columns=self.columns.copy(),
            previous_operation=previous_operation
        )


@dataclass
class FilterOperation(DataOperation):
    """Operation that filters rows."""
    condition: Expression
    previous_operation: Optional[Operation] = None
    
    def clone_with_previous(self, previous_operation: Optional[Operation]) -> Operation:
        return FilterOperation(
            condition=self.condition,
            previous_operation=previous_operation
        )


@dataclass
class GroupByOperation(DataOperation):
    """Operation that groups rows."""
    columns: List[Expression] = field(default_factory=list)
    previous_operation: Optional[Operation] = None
    
    def clone_with_previous(self, previous_operation: Optional[Operation]) -> Operation:
        return GroupByOperation(
            columns=self.columns.copy(),
            previous_operation=previous_operation
        )


@dataclass
class HavingOperation(DataOperation):
    """Operation that filters grouped rows."""
    condition: Expression
    previous_operation: Optional[Operation] = None
    
    def clone_with_previous(self, previous_operation: Optional[Operation]) -> Operation:
        return HavingOperation(
            condition=self.condition,
            previous_operation=previous_operation
        )


@dataclass
class QualifyOperation(DataOperation):
    """Operation that filters based on window function results."""
    condition: Expression
    previous_operation: Optional[Operation] = None
    
    def clone_with_previous(self, previous_operation: Optional[Operation]) -> Operation:
        return QualifyOperation(
            condition=self.condition,
            previous_operation=previous_operation
        )


@dataclass
class OrderByOperation(DataOperation):
    """Operation that orders rows."""
    clauses: List = field(default_factory=list)
    previous_operation: Optional[Operation] = None
    
    def clone_with_previous(self, previous_operation: Optional[Operation]) -> Operation:
        return OrderByOperation(
            clauses=self.clauses.copy(),
            previous_operation=previous_operation
        )


@dataclass
class LimitOperation(DataOperation):
    """Operation that limits the number of rows."""
    limit: int
    previous_operation: Optional[Operation] = None
    
    def clone_with_previous(self, previous_operation: Optional[Operation]) -> Operation:
        return LimitOperation(
            limit=self.limit,
            previous_operation=previous_operation
        )


@dataclass
class OffsetOperation(DataOperation):
    """Operation that skips a number of rows."""
    offset: int
    previous_operation: Optional[Operation] = None
    
    def clone_with_previous(self, previous_operation: Optional[Operation]) -> Operation:
        return OffsetOperation(
            offset=self.offset,
            previous_operation=previous_operation
        )


@dataclass
class DistinctOperation(DataOperation):
    """Operation that removes duplicate rows."""
    previous_operation: Optional[Operation] = None
    
    def clone_with_previous(self, previous_operation: Optional[Operation]) -> Operation:
        return DistinctOperation(
            previous_operation=previous_operation
        )


@dataclass
class JoinOperation(SourceOperation):
    """Operation that joins two data sources."""
    left: Operation
    right: Operation
    condition: Expression
    join_type: str
    previous_operation: Optional[Operation] = None
    left_alias: Optional[str] = None
    right_alias: Optional[str] = None
    
    def clone_with_previous(self, previous_operation: Optional[Operation]) -> Operation:
        return JoinOperation(
            left=self.left,
            right=self.right,
            condition=self.condition,
            join_type=self.join_type,
            previous_operation=previous_operation,
            left_alias=self.left_alias,
            right_alias=self.right_alias
        )


@dataclass
class SubqueryOperation(SourceOperation):
    """Operation that defines a subquery source."""
    dataframe: Any  # Avoid circular import with DataFrame
    alias: str
    previous_operation: Optional[Operation] = None
    
    def clone_with_previous(self, previous_operation: Optional[Operation]) -> Operation:
        return SubqueryOperation(
            dataframe=self.dataframe,
            alias=self.alias,
            previous_operation=previous_operation
        )
