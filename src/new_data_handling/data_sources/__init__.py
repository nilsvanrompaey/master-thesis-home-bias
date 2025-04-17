"""Data sources package initialization."""

from .base import DataSource
from .cpis import CPISDataSource, CPISDataFrame
from .ds import DSDataSource
from .fed import FEDDataSource
from .wfe import WFEDataSource
from .wb import WBDataSource
from .gdp import GDPDataSource, GDPDataFrame

__all__ = [
    # Template data source class
    "DataSource",

    # Data source classes
    "CPISDataSource",
    "DSDataSource",
    "FEDDataSource",
    "WFEDataSource",
    "WBDataSource",
    "GDPDataSource",

    # Dataframe classes
    "CPISDataFrame",
    "GDPDataFrame",
]