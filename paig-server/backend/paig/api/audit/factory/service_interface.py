from abc import ABC, abstractmethod


class DataServiceInterface(ABC):

    @abstractmethod
    async def create_access_audit(self, access_audit_params):
        """
        Create access audit
        Attributes:
            access_audit_params dict (BaseAccessAuditView): Access audit params dict
        Returns:
            AccessAuditModel: Access audit object
        """
        pass


    @abstractmethod
    async def get_access_audits(self, include_filters, exclude_filters, page, size, sort, min_time, max_time):
        """
        Get access audits with filters
        Attributes:
            include_filters (includeQuery): Filter by includeQuery params
            exclude_filters (excludeQuery): Filter by excludeQuery params
            page (int): Page number to retrieve
            size (int): Number of items per page
            sort (str): Sort options
            min_time (int): from epoch time
            max_time (int): to epoch time
        Returns:
            List[BaseAccessAuditView]: List of access audits in pageable format
        """
        pass

    @abstractmethod
    async def get_usage_counts(self, filters, min_value, max_value):
        """
        Get usage counts group by result
        Attributes:
            filters (includeQuery): Filter by includeQuery params
            min_value (int): from epoch time
            max_value (int): to epoch time
        Returns:
            dict : Usage counts group by result
        """
        pass

    @abstractmethod
    async def get_trait_counts_by_application(self, filters, min_value, max_value):
        """
        Get trait counts group by trait and application
        Attributes:
            filters (includeQuery): Filter by includeQuery params
            min_value (int): from epoch time
            max_value (int): to epoch time
        Returns:
            dict : Trait counts group by trait and application
        """
        pass

    @abstractmethod
    async def get_access_data_counts(self, filters, min_value, max_value, interval):
        """
        Get access data counts group by result and interval
        Attributes:
            filters (includeQuery): Filter by includeQuery params
            min_value (int): from epoch time
            max_value (int): to epoch time
            interval (str): The interval('year', 'month', 'week', 'day', 'hour')
        Returns:
            dict : Access data counts group by result and interval
        """
        pass

    @abstractmethod
    async def get_user_id_counts(self, size):
        """
        Get user id counts
        Attributes:
            size (int): Number of items
        Returns:
            dict : User id counts
        """
        pass

    @abstractmethod
    async def get_app_name_counts(self, size):
        """
        Get app name counts
        Attributes:
            size (int): Number of items
        Returns:
            dict : App name counts
        """
        pass

    @abstractmethod
    async def get_app_name_by_user_id(self, filters, min_value, max_value):
        """
        Get app name counts group by app name and user id
        Attributes:
            filters (includeQuery): Filter by includeQuery params
            min_value (int): from epoch time
            max_value (int): to epoch time
        Returns:
            dict : App name counts group by app name and user id
        """
        pass

    @abstractmethod
    async def get_top_users_count(self, filters, size, min_time, max_time):
        """
        Get top users count
        Attributes:
            filters (includeQuery): Filter by includeQuery params
            min_time (int): from epoch time
            max_time (int): to epoch time
            size (int): Number of items
        Returns:
            dict : Top users count
        """
        pass

    @abstractmethod
    async def get_unique_user_id_count(self, filters, min_time, max_time):
        """
        Get unique user id count
        Attributes:
            filters (includeQuery): Filter by includeQuery params
            min_time (int): from epoch time
            max_time (int): to epoch time
        Returns:
            dict : Unique user id count
        """
        pass

    @abstractmethod
    async def get_unique_trait_count(self, filters, min_time, max_time):
        """
        Get unique trait count
        Attributes:
            filters (includeQuery): Filter by includeQuery params
            min_time (int): from epoch time
            max_time (int): to epoch time
        Returns:
            dict : Unique trait count
        """
        pass

    @abstractmethod
    async def get_activity_trend_counts(self, includeQuery, fromTime, toTime, interval):
        """
        Get access data counts group by result and interval
        Attributes:
            filters (includeQuery): Filter by includeQuery params
            min_value (int): from epoch time
            max_value (int): to epoch time
            interval (str): The interval('year', 'month', 'week', 'day', 'hour')
        Returns:
            dict : Access audits activity trend by all users
        """
        pass

