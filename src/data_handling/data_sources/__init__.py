"""Data sources package initialization."""

from .base import DataSource
from .cpis import CPISDataSource, CPISDataFrame
from .ds import DSDataSource
from .fed import FEDDataSource
from .wfe import WFEDataSource
from .wb import WBDataSource

__all__ = [
    "DataSource",
    "CPISDataSource",
    "DSDataSource",
    "FEDDataSource",
    "WFEDataSource",
    "WBDataSource",
    "CPISDataFrame",
]