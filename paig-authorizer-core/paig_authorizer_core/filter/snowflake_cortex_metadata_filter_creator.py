from paig_authorizer_core.filter.base_metadata_filter_criteria_creator import BaseMetadataFilterCriteriaCreator


class SnowflakeCortexMetadataFilterCreator(BaseMetadataFilterCriteriaCreator):
    """
    Creates metadata filter criteria specifically for Snowflake Cortex.
    Overrides the prepare_metadata_value method to handle Snowflake Cortex specific formatting.
    """

    def prepare_metadata_value(self, metadata_value: str) -> str:
        """
        Prepares the metadata value for filtering in Snowflake Cortex.
        
        In Snowflake Cortex, string values should not be quoted.

        Args:
            metadata_value (str): The metadata value.

        Returns:
            str: The prepared metadata value suitable for Snowflake Cortex filtering.
        """
        if self.is_integer(metadata_value) or self.is_float(metadata_value):
            return metadata_value
        elif self.is_boolean(metadata_value):
            return metadata_value.upper()
        else:
            # For Snowflake Cortex, do not add quotes to string values
            return metadata_value 