from django.db.backends.oracle.base import DatabaseWrapper as OracleDatabaseWrapper
from django.db.backends.oracle.features import DatabaseFeatures as OracleDatabaseFeatures


class DatabaseFeatures(OracleDatabaseFeatures):
    # Allow Oracle 12.2+ (Django normally requires 19+)
    minimum_database_version = (12, 2)


class DatabaseWrapper(OracleDatabaseWrapper):
    features_class = DatabaseFeatures
