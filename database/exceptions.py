class DatabaseException(Exception):
    """Base exception for database errors."""
    pass


class MissingCredentials(DatabaseException):
    """Exception raised when database credentials are missing."""
    pass
