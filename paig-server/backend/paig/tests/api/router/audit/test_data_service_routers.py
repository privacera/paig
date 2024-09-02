import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from core.security.authentication import get_auth_user
from api.audit.RDS_service.db_operations.access_audit_repository import AccessAuditRepository
from api.audit.RDS_service.rds_service import RdsService



data_services_base_route = "data-service/api"
group_dict = {
    "status": 1,
    "name": "test",
    "description": "test first",
}


class TestDataServiceRouters:
    def setup_method(self):
        self.auth_user_obj = {
            "id": 1,
            "username": "test",
            "roles": ["USER"]
        }

    @pytest.fixture
    def access_audits_data(self):
        return {
            "app_key": "ac3e25c59bcaf7a149d91c7302b06ce7",
            "app_name": "PAIG Demo Test",
            "client_app_key": "*",
            "client_app_name": "",
            "client_host_name": "plugin-service-66fbb9c577-nl6zh",
            "client_ip": "10.208.2.90",
            "context": {},
            "event_id": "0310fb50-90a5-4a97-9421-ff1547cc5d33",
            "event_time": 1717223581000,
            "masked_traits": {},
            "messages": [
                {
                    "originalMessage": "dlM+u0vf2swToD8TAoXE79LVTI+Niw3JtoNNPZkshYoxvXLa/Akt/3ZPH6602ADAahAFGSSpMt/1WVXpEUbcfGPNRlqnTlLq40RQwmH8rdWag/2fje6T0dHTus7fUg1L6cpkC24g58sZBHZVLdy2BeCsT0bRfm40OJ0oM8e0rsk=",
                    "maskedMessage": "",
                    "analyzerResult": "[{\"entity_type\": \"PERSON\", \"start\": 28, \"end\": 42, \"score\": 0.85, \"analysis_explanation\": null, \"recognition_metadata\": {\"recognizer_name\": \"SpacyRecognizer\", \"recognizer_identifier\": \"SpacyRecognizer_140700819276240\"}, \"model_name\": \"\", \"scanner_name\": \"PIIScanner\"}]"
                }
            ],
            "no_of_tokens": 0,
            "paig_policy_ids": [
                "9910",
                "2090"
            ],
            "request_id": "7393962a-c585-43c0-8b63-55fb49341934",
            "request_type": "prompt",
            "result": "allowed",
            "tenant_id": "16990168240005",
            "thread_id": "1719926416712",
            "thread_sequence_number": 242,
            "traits": [
                "PERSON"
            ],
            "user_id": "Sally-Sales",
            "encryption_key_id": 9,
            "log_time": 0,
            "transaction_sequence_number": 0
        }

    def auth_user(self):
        return self.auth_user_obj

    @pytest.fixture
    def rds_service(self, db_session, set_context_session):
        access_audit_repo_mock = AccessAuditRepository()
        return RdsService(access_audit_repo_mock)

    @pytest.mark.asyncio
    async def test_get_access_audits(self, client: AsyncClient, app: FastAPI, rds_service, access_audits_data):
        app.dependency_overrides[get_auth_user] = self.auth_user
        response = await client.get(
            f"{data_services_base_route}/shield_audits/search?size=120&sort=eventTime,threadSequenceNumber,desc"
            f"&fromTime=1717223581000&toTime=1717223589999"
        )
        assert response.status_code == 200
        assert response.json()['content'] == []

        # Added access audit
        access_audits = await rds_service.create_access_audit(access_audits_data)
        assert access_audits.app_name == "PAIG Demo Test"

        # Get access audits
        response = await client.get(
            f"{data_services_base_route}/shield_audits/search?size=120&sort=eventTime,threadSequenceNumber,desc"
            f"&fromTime=1717223581000&toTime=1717223589999"
        )
        assert response.status_code == 200
        assert len(response.json()['content']) == 1
        assert response.json()['content'][0]['applicationName'] == "PAIG Demo Test"

        # Get access audits with search filter user_id and application name
        response = await client.get(
            f"{data_services_base_route}/shield_audits/search?size=120&sort=eventTime,threadSequenceNumber,desc"
            f"&fromTime=1717223581000&toTime=1717223589999"
            f"&includeQuery.userId=*sal*&includeQuery.applicationName=*demo*"
        )
        assert response.status_code == 200
        assert len(response.json()['content']) == 1
        assert response.json()['content'][0]['applicationName'] == "PAIG Demo Test"

        # Get access audits with search filter result and request type
        response = await client.get(
            f"{data_services_base_route}/shield_audits/search?size=120&sort=eventTime,threadSequenceNumber,desc"
            f"&fromTime=1717223581000&toTime=1717223589999"
            f"&includeQuery.requestType=prompt&includeQuery.result=allowed"
        )
        assert response.status_code == 200
        assert len(response.json()['content']) == 1
        assert response.json()['content'][0]['applicationName'] == "PAIG Demo Test"

        # Get access audits with search filter trait
        response = await client.get(
            f"{data_services_base_route}/shield_audits/search?size=120&sort=eventTime,threadSequenceNumber,desc"
            f"&fromTime=1717223581000&toTime=1717223589999"
            f"&includeQuery.trait=PERSON"
        )
        assert response.status_code == 200
        assert len(response.json()['content']) == 1
        assert response.json()['content'][0]['applicationName'] == "PAIG Demo Test"

        # Get access audits with search filter thread id
        response = await client.get(
            f"{data_services_base_route}/shield_audits/search?size=120&sort=eventTime,threadSequenceNumber,desc"
            f"&fromTime=1717223581000&toTime=1717223589999"
            f"&includeQuery.threadId=1719926416712"
        )
        assert response.status_code == 200
        assert len(response.json()['content']) == 1
        assert response.json()['content'][0]['applicationName'] == "PAIG Demo Test"



    @pytest.mark.asyncio
    async def test_get_usage_counts(self, client: AsyncClient, app: FastAPI, rds_service, access_audits_data):
        app.dependency_overrides[get_auth_user] = self.auth_user
        response = await client.get(
            f"{data_services_base_route}/shield_audits/usage_counts?groupBy=result"
            f"&fromTime=1717223581000&toTime=1717223589999"
        )
        assert response.status_code == 200
        assert response.json() == {"result": {}}

        # Added access audit
        access_audits = await rds_service.create_access_audit(access_audits_data)
        assert access_audits.app_name == "PAIG Demo Test"

        # Get Usage counts
        usage_counts_expected = {"result": {"allowed": {"count": 1}}}
        response = await client.get(
            f"{data_services_base_route}/shield_audits/usage_counts?groupBy=result"
            f"&fromTime=1717223581000&toTime=1717223589999"
        )
        assert response.status_code == 200
        assert response.json() == usage_counts_expected


    @pytest.mark.asyncio
    async def test_get_trait_counts_by_application(self, client: AsyncClient, app: FastAPI, rds_service, access_audits_data):
        app.dependency_overrides[get_auth_user] = self.auth_user
        response = await client.get(
            f"{data_services_base_route}/shield_audits/trait_counts?groupBy=traits,applicationName"
            f"&fromTime=1717223581000&toTime=1717223589999"
        )
        assert response.status_code == 200
        assert response.json() == {"traits": {}}

        # Added access audit
        access_audits = await rds_service.create_access_audit(access_audits_data)
        assert access_audits.app_name == "PAIG Demo Test"

        # Get Trait counts by application
        trait_counts_expected = {"traits":
                                        {"PERSON":
                                             {"count": 1,
                                              "applicationName": {
                                                  "PAIG Demo Test": {"count": 1}
                                              }
                                              }
                                         }
                                 }
        response = await client.get(
            f"{data_services_base_route}/shield_audits/trait_counts?groupBy=traits,applicationName"
            f"&fromTime=1717223581000&toTime=1717223589999"
        )
        assert response.status_code == 200
        assert response.json() == trait_counts_expected


    @pytest.mark.asyncio
    async def test_built_in_reports_api_routes(self, client: AsyncClient, app: FastAPI, rds_service, access_audits_data):
        app.dependency_overrides[get_auth_user] = self.auth_user

        # Added access audit
        access_audits = await rds_service.create_access_audit(access_audits_data)
        assert access_audits.app_name == "PAIG Demo Test"

        # Get User id counts
        user_id_counts_expected = {"userId": {"Sally-Sales": {"count": 1}}}
        response = await client.get(
            f"{data_services_base_route}/shield_audits/user_id_counts?size=100"
        )
        assert response.status_code == 200
        assert response.json() == user_id_counts_expected

        # Get App name counts
        response = await client.get(
            f"{data_services_base_route}/shield_audits/app_name_counts?size=100"
        )

        assert response.status_code == 200
        assert response.json() == {"applicationName": {"PAIG Demo Test": {"count": 1}}}

        # Get App name by user id
        app_name_by_user_id_expected = {'applicationName': {'PAIG Demo Test': {'count': 1, 'userId': {'count': 1}}}}
        response = await client.get(
            f"{data_services_base_route}/shield_audits/app_by_user_counts?fromTime=1717223581000&toTime=1717223589999"
        )
        assert response.status_code == 200
        assert response.json() == app_name_by_user_id_expected

        # Get Top users by id
        response = await client.get(
            f"{data_services_base_route}/shield_audits/top_users_count?size=10&fromTime=1717223581000&toTime=1717223589999"
        )
        assert response.status_code == 200
        assert response.json() == {"userId": {"Sally-Sales": {"count": 1}}}

        # Get Unique user id count
        response = await client.get(
            f"{data_services_base_route}/shield_audits/uniq_user_id_counts?fromTime=1717223581000&toTime=1717223589999"
        )
        assert response.status_code == 200
        assert response.json() == {'userId': {'count': 1}}

        # Get Unique trait count
        response = await client.get(
            f"{data_services_base_route}/shield_audits/uniq_trait_counts?fromTime=1717223581000&toTime=1717223589999"
        )
        assert response.status_code == 200
        assert response.json() == {'traits': {'PERSON': {'count': 1}}}

        # Get Access data counts
        response = await client.get(
            f"{data_services_base_route}/shield_audits/access_data_counts?fromTime=1717223581000&toTime=1717223589999&interval=day"
        )
        assert response.status_code == 200
        assert "day" in response.json()

        # Get Access Audits Activity Trends
        response = await client.get(
            f"{data_services_base_route}/shield_audits/activity_trend_counts?fromTime=1717223581000&toTime=1717223589999&interval=day"
        )
        assert response.status_code == 200
        assert "day" in response.json()

