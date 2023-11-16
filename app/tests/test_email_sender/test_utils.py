from datetime import datetime as dt

from unittest import TestCase
from unittest.mock import patch

from email_sender.utils import BqConnector

class UtilsTests(TestCase):
    def setUp(self) -> None:
        self.expected_data = {
            'client_id': 'test_client_id',
            'bio_id': 'test_bio_id',
            'email_response': 'test_tracking_id',
            'timestamp': dt.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        }

    @patch('google.cloud.bigquery.Client', autospec=True)
    def test_build_data(self, mock_bigquery):
        bq_connector = BqConnector()
        data = {
            'client_id': 'test_client_id',
            'bio_id': 'test_bio_id'
        }

        response = MockedResponse("sourceTrackingId", "test_tracking_id")        
        _data = bq_connector.build_data(data, response)

        assert _data, self.expected_data

    @patch('google.cloud.bigquery.Client', autospec=True)
    def test_write_bq(self, mock_bigquery):
        mock_bigquery().insert_rows_json.return_value = False
        bq_connector = BqConnector()
        data = {
            'client_id': 'test_client_id',
            'bio_id': 'test_bio_id'
        }

        response = MockedResponse("sourceTrackingId", "test_tracking_id")        
        result = bq_connector.write(data, response)

        assert result, True

class MockedResponse:
    def __init__(self, key, value):
        self.data = {key: value}
    
    def json(self):
        return self.data