import os
import sys
change_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(change_directory)
sys.path.append(change_directory)
import random
import time
import sys
from core.config import load_config_file
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
import asyncio
from api.audit.RDS_service.db_models.access_audit_model import AccessAuditModel
import click

# Constants
MILLISECONDS_IN_SECOND = 1000
SECONDS_IN_A_DAY = 86400


app_names = ["PAIG Demo App1", "PAIG Demo App2", "PAIG Demo App3", "PAIG Demo App4", "PAIG Demo App5"]

request_type = ["prompt", "rag", "reply", "enriched_prompt"]  # rag: Context documents, enriched_prompt: Prompt to LLM

result = ["allowed", "denied", "masked"]

traits = ["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "US_PASSPORT", "US_SSN", "US_BANK_NUMBER", "CREDIT_CARD", "CRYPTO", "IT_PASSPORT"]

user_ids = ["Sally", "Mark", "john", "Sam", "Rahul"]


messages = [
    [
        {"originalMessage": "GANRiUcwqJiwVupXmNrAnZycFYJAXniKphl2nsYE8+sQudiiFW9MjIlv1UBzOw+ADDEvFFSUK2Mbp/EtdOxL2TQUXdjAkjRLtJwAFMVRhP2M+sGw/1zivu9DOEExP89RSsSAvP41jBPqfLhaVYOPlcrhjDfKRWj0mbPeG0D0+Mw=",
        "maskedMessage": "",
        "analyzerResult": "[{\"entity_type\": \"PERSON\", \"start\": 0, \"end\": 14, \"score\": 0.85, \"analysis_explanation\": null, \"recognition_metadata\": {\"recognizer_name\": \"SpacyRecognizer\", \"recognizer_identifier\": \"SpacyRecognizer_140700819276240\"}, \"model_name\": \"\", \"scanner_name\": \"PIIScanner\"}, {\"entity_type\": \"PHONE_NUMBER\", \"start\": 59, \"end\": 71, \"score\": 0.4, \"analysis_explanation\": null, \"recognition_metadata\": {\"recognizer_name\": \"PhoneRecognizer\", \"recognizer_identifier\": \"PhoneRecognizer_140699597549776\"}, \"model_name\": \"\", \"scanner_name\": \"PIIScanner\"}]"
        },
    ],
    [
        {"originalMessage": "dlM+u0vf2swToD8TAoXE79LVTI+Niw3JtoNNPZkshYoxvXLa/Akt/3ZPH6602ADAahAFGSSpMt/1WVXpEUbcfGPNRlqnTlLq40RQwmH8rdWag/2fje6T0dHTus7fUg1L6cpkC24g58sZBHZVLdy2BeCsT0bRfm40OJ0oM8e0rsk=",
        "maskedMessage": "",
        "analyzerResult": "[{\"entity_type\": \"PERSON\", \"start\": 28, \"end\": 42, \"score\": 0.85, \"analysis_explanation\": null, \"recognition_metadata\": {\"recognizer_name\": \"SpacyRecognizer\", \"recognizer_identifier\": \"SpacyRecognizer_140700819276240\"}, \"model_name\": \"\", \"scanner_name\": \"PIIScanner\"}]"
        },
    ],
    [
        {"originalMessage": "GANRiUcwqJiwVupXmNrAnZycFYJAXniKphl2nsYE8+sQudiiFW9MjIlv1UBzOw+ADDEvFFSUK2Mbp/EtdOxL2TQUXdjAkjRLtJwAFMVRhP2M+sGw/1zivu9DOEExP89RSsSAvP41jBPqfLhaVYOPlcrhjDfKRWj0mbPeG0D0+Mw=",
        "maskedMessage": "",
        "analyzerResult": "[{\"entity_type\": \"PERSON\", \"start\": 0, \"end\": 14, \"score\": 0.85, \"analysis_explanation\": null, \"recognition_metadata\": {\"recognizer_name\": \"SpacyRecognizer\", \"recognizer_identifier\": \"SpacyRecognizer_140700819276240\"}, \"model_name\": \"\", \"scanner_name\": \"PIIScanner\"}, {\"entity_type\": \"PHONE_NUMBER\", \"start\": 59, \"end\": 71, \"score\": 0.4, \"analysis_explanation\": null, \"recognition_metadata\": {\"recognizer_name\": \"PhoneRecognizer\", \"recognizer_identifier\": \"PhoneRecognizer_140699597549776\"}, \"model_name\": \"\", \"scanner_name\": \"PIIScanner\"}]"
        },
    ],
    [
        {"originalMessage": "EecTBpjltF47oi3WjZSFEeufJiES3bN4In4K5nCb0TWfN2DfzLi9svcbw6in0kkx6jYyq0KQkC7gfFp8GbZ/FVeUI1s/VycHMDaE8x8O02UFvJrwxUKZ6RnsbQzHGW7GXEYaigRYTXn+UMg4sl+uqfjXB7bJ+lrX30EfwDme7lU=",
        "maskedMessage": "",
        "analyzerResult": "[]"
        },
    ],
    [
        {"originalMessage": "WrDfirxqa5NKxZ7CWjOxG0UXqH1uwgHc9G1cuv8+a6GTFQo+yzFTPeAL/x2/ztURLTNGJeNHqIeOAvpVvzLgwbjCoMW51I8O1piG31QjkAmsNGwMHnqvnW8xqYnhUREZKz2dxVU2X3tkAcNaEk1baXH3BBGm8L6uLik3hDmImVg=a3NwUQQmyMY99bA4DFdIkVjXw+9kG3ytUne83l3qpXIxrfkcXCAPLK3IAAZRE6fBhSBgQ1mqs1q4pvtJ8Stowu6CgIxeD0Xpsb0XRGUca8L6EfcCjChcetvJc4RkeGWCJ8YdshXirNgSeXJd+9TBMdFjsyXIct+S9IJVmM70wps=",
        "maskedMessage": "",
        "analyzerResult": "[]"
        }
    ],
]


def pick_random_traits(traits):
    number_of_traits = random.choices([1, 2, 3], weights=[0.5, 0.3, 0.1], k=1)[0]
    random_traits = random.choices(traits, weights=[0.7, 0.4, 0.2, 0.1, 0.3, 0.1, 0.4, 0.25, 0.2], k=number_of_traits)
    # random_traits = random.sample(traits_random, number_of_traits)
    return random_traits


config = load_config_file()


async def create_access_audits_in_bulk(access_audits):
    engine = None
    try:
        database_url = config["database"]["url"]
        engine = create_async_engine(url=database_url)

        class SyncSession(Session):
            def get_bind(self, mapper=None, clause=None, **kwargs):
                return engine.sync_engine

        async_session = sessionmaker(
            class_=AsyncSession,
            sync_session_class=SyncSession,
            expire_on_commit=False
        )
        async with async_session() as session:
            async with session.begin():
                session.add_all(access_audits)
                await session.commit()
    except Exception as e:
        print(f"An error occurred during Access Audit creation: {e}")
        sys.exit(f"An error occurred during Access Audit creation: {e}")
    finally:
        if engine:
            await engine.dispose()


def create_access_audits_model_list(no_days, no_of_rows):
    # Get the current time in UTC in milliseconds
    current_time_ms = int(time.time() * MILLISECONDS_IN_SECOND)

    # Calculate the interval between each timestamp
    total_duration_ms = no_days * SECONDS_IN_A_DAY * MILLISECONDS_IN_SECOND
    interval_ms = total_duration_ms // (no_of_rows - 1)

    start_thread_id = 1
    access_audits = []
    start_time = time.time()
    print("Generating Access Audit data")
    for i in range(no_of_rows):
        access_audit = AccessAuditModel()
        access_audit.app_name = random.choices(app_names, weights=[0.2, 0.4, 0.6, 0.3, 0.1], k=1)[0]
        access_audit.messages = random.choices(messages, weights=[0.2, 0.4, 0.6, 0.3, 0.1], k=1)[0]
        access_audit.request_type = random.choices(request_type, weights=[0.2, 0.5, 0.3, 1.0], k=1)[0]
        access_audit.result = random.choices(result, weights=[0.6, 0.15, 0.35], k=1)[0]
        access_audit.traits = pick_random_traits(traits)
        access_audit.user_id = random.choices(user_ids, weights=[0.4, 0.2, 0.5, 0.3, 0.1], k=1)[0]
        access_audit.thread_id = str(start_thread_id + i)
        timestamp = current_time_ms - (i * interval_ms)
        access_audit.event_time = int(timestamp)
        access_audits.append(access_audit)
    end_time = time.time()
    print("Access Audit data generated successfully in:: ", end_time - start_time, " seconds")
    return access_audits


def insert_access_audits_data(access_audits):
    print("Inserting Access Audit data")
    start_time = time.time()
    if len(access_audits) < 50000:
        asyncio.run(create_access_audits_in_bulk(access_audits))
    else:
        for k in range(0, len(access_audits), 50000):
            asyncio.run(create_access_audits_in_bulk(access_audits[k:k + 50000]))
            print(f"Access Audit Rows {k+50000} inserted successfully.")
    print("Access Audit data inserted successfully in:: ", time.time() - start_time, " seconds")


@click.option(
    "--days",
    type=click.INT,
    default=90,
    help="Num of Days for which data needs to be generated. Default is 90 days.",
)
@click.option(
    "--rows",
    type=click.INT,
    default=100000,
    help="Num of rows to be generated. Default is 100000.",
)
@click.command()
def main(
    days: int,
    rows: int,
):
    access_audits = create_access_audits_model_list(days, rows)
    insert_access_audits_data(access_audits)


if __name__ == "__main__":
    main()
