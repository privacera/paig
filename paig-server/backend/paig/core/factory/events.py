import copy
from core.factory.metrics_collector import get_metric_client


class ProductTelemetryEvent:
    def __init__(self, name: str = "", data: dict = None):
        super().__init__()
        self.metric_client = get_metric_client()
        self.name = name
        self.properties = dict()
        self.properties = copy.deepcopy(self.metric_client.get_data())
        self.user_id = self.properties.get('installation_id')
        if data:
            for key, value in data.items():
                self.properties[key] = value


class ScheduledEvent(ProductTelemetryEvent):
    def __init__(
            self,
            data: dict
    ) -> None:
        super().__init__(data=data)
        self.name = "scheduled_event"


class CreateAIApplicationEvent(ProductTelemetryEvent):
    def __init__(self):
        super().__init__()
        self.name = "create_ai_application_event"


class UpdateAIApplicationEvent(ProductTelemetryEvent):
    def __init__(self):
        super().__init__()
        self.name = "update_ai_application_event"


class DeleteAIApplicationEvent(ProductTelemetryEvent):
    def __init__(self):
        super().__init__()
        self.name = "delete_ai_application_event"


class CreateVectorDBEvent(ProductTelemetryEvent):
    def __init__(self, vector_db_type: str):
        super().__init__(data={"vector_db_type": vector_db_type})
        self.name = "create_vector_db_event"


class UpdateVectorDBEvent(ProductTelemetryEvent):
    def __init__(self, vector_db_type: str):
        super().__init__(data={"vector_db_type": vector_db_type})
        self.name = "update_vector_db_event"


class DeleteVectorDBEvent(ProductTelemetryEvent):
    def __init__(self, vector_db_type: str):
        super().__init__(data={"vector_db_type": vector_db_type})
        self.name = "delete_vector_db_event"


class CreateAIApplicationPolicyEvent(ProductTelemetryEvent):
    def __init__(
            self,
            tags: list,
            prompt: str,
            reply: str
    ):
        super().__init__(data={"tags": tags, "prompt": prompt, "reply": reply})
        self.name = "create_ai_app_policy_event"


class UpdateAIApplicationPolicyEvent(ProductTelemetryEvent):
    def __init__(
            self,
            tags: list,
            prompt: str,
            reply: str
    ):
        super().__init__(data={"tags": tags, "prompt": prompt, "reply": reply})
        self.name = "update_ai_app_policy_event"


class DeleteAIApplicationPolicyEvent(ProductTelemetryEvent):
    def __init__(
            self,
            tags: list,
            prompt: str,
            reply: str
    ):
        super().__init__(data={"tags": tags, "prompt": prompt, "reply": reply})
        self.name = "delete_ai_app_policy_event"


class DownloadAIApplicationConfigEvent(ProductTelemetryEvent):
    def __init__(self):
        super().__init__()
        self.name = "download_ai_app_config_event"
