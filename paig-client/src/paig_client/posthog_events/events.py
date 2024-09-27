import copy
from .metric_collector import get_metric_client
from paig_client.util import get_system_unique_id


class ProductTelemetryEvent:
    _curr_user_id = None
    UNKNOWN_USER_ID = "UNKNOWN"

    def __init__(self, name: str = "", data: dict = None):
        super().__init__()
        self.metric_client = get_metric_client()
        self.metric_client.initialize()
        self.name = name
        self.properties = dict()
        self.properties = copy.deepcopy(self.metric_client.get_data())
        if data:
            self.properties.update(data)

    @property
    def user_id(self) -> str:
        if self._curr_user_id:
            return self._curr_user_id
        try:
            self._curr_user_id = get_system_unique_id()
        except Exception:
            self._curr_user_id = self.UNKNOWN_USER_ID
        return self._curr_user_id


class PaigClientSetupEvent(ProductTelemetryEvent):
    def __init__(self, data: dict):
        super().__init__(data=data)
        self.name = "paig_client_setup_event"
