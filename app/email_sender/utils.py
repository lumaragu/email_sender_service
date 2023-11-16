import logging
import os
from datetime import datetime as dt
from typing import Any, Dict, List

from google.cloud import bigquery


class BqConnector:
    def __init__(self):
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.instance = bigquery.Client(project=project)
        self.table = f"{project}.user_data.bioreport_email_response"

    def build_data(self, data: Dict, email_response: Any) -> List:
        email_uuid = email_response.json().get("sourceTrackingId")
        return [
            {
                'client_id': data["client_id"],
                'bio_id': data["bio_id"],
                'email_response': email_uuid,
                'timestamp': dt.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            }
        ]

    def write(self, data: Dict, email_response: Any) -> bool:
        _data = self.build_data(data, email_response)
        try:
            errors = self.instance.insert_rows_json(self.table, _data)
            if errors:
                logging.error(f"Could not write data into BigQuery. {data}")
        except BaseException as e:
            print(e)

        return True