import copy
from .metric_collector import get_metric_client
import os
import uuid
from pathlib import Path


class ProductTelemetryEvent:
    _curr_user_id = None
    USER_ID_PATH = str(Path.home() / ".cache" / "paig_client" / "telemetry_user_id")
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

        # File access may fail due to permissions or other reasons. We don't want to
        # crash so we catch all exceptions.
        try:
            if not os.path.exists(self.USER_ID_PATH):
                os.makedirs(os.path.dirname(self.USER_ID_PATH), exist_ok=True)
                with open(self.USER_ID_PATH, "w") as f:
                    new_user_id = str(uuid.uuid4())
                    f.write(new_user_id)
                self._curr_user_id = new_user_id
            else:
                with open(self.USER_ID_PATH, "r") as f:
                    self._curr_user_id = f.read()
        except Exception:
            self._curr_user_id = self.UNKNOWN_USER_ID
        return self._curr_user_id


class PaigClientSetupEvent(ProductTelemetryEvent):
    def __init__(self, data: dict):
        super().__init__(data=data)
        self.name = "paig_client_setup_event"
