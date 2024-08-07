from sqlalchemy import String, TypeDecorator


class CommaSeparatedList(TypeDecorator):
    """
    Custom SQLAlchemy type decorator for storing lists as comma-separated strings in the database.

    Args:
        length (int, optional): Maximum length of the stored string. Defaults to 255.
    """
    impl = String

    def __init__(self, length=255, *args, **kwargs):
        """
        Initialize the CommaSeparatedList type decorator.

        Args:
            length (int, optional): Maximum length of the stored string. Defaults to 255.
            *args: Additional positional arguments for TypeDecorator.
            **kwargs: Additional keyword arguments for TypeDecorator.
        """
        self.length = length
        super().__init__(*args, **kwargs)

    def load_dialect_impl(self, dialect):
        """
        Load the dialect implementation for the CommaSeparatedList type decorator.

        Args:
            dialect: Dialect object for the database.

        Returns:
            TypeDecorator: Type descriptor for the CommaSeparatedList type.
        """
        return dialect.type_descriptor(String(self.length))

    def process_bind_param(self, value, dialect):
        """
        Convert a Python list into a comma-separated string for database storage.

        Args:
            value (list): Python list to be stored in the database.

        Returns:
            str: Comma-separated string representation of the list.
        """
        if isinstance(value, list):
            return ','.join(value)
        else:
            return value

    def process_result_value(self, value, dialect):
        """
        Convert a comma-separated string from the database into a Python list.

        Args:
            value (str): Comma-separated string retrieved from the database.

        Returns:
            list: Python list converted from the comma-separated string.
        """
        if value is None or value == '':
            return []
        return value.split(',')