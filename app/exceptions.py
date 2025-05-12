"""
Custom exception classes for the TriloDocs application.
"""


class TriloDocsError(Exception):
    """
    Base exception for all TriloDocs errors.
    """
    pass


class TableDataError(TriloDocsError):
    """
    Raised when a table contains text-based entries in cells where numeric
    values are expected.
    """
    def __init__(
            self,
            message="Error: Some cells in your table contain non-numeric data. "
                    "Make sure all fields that should be numbers contain only "
                    "digits."
    ):
        super().__init__(message)
