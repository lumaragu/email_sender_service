from unittest import TestCase, mock

from google.api_core.exceptions import NotFound
from google.cloud.secretmanager_v1 import SecretManagerServiceClient
from google.cloud.secretmanager_v1.proto.resources_pb2 import SecretPayload
from google.cloud.secretmanager_v1.proto.service_pb2 import AccessSecretVersionResponse

from email_sender.email_service_factory import EmailServiceFactory
from email_sender.email_services.paubox import PauboxEmailService
from email_sender.email_services.sendgrid import SendgridEmailService


class EmailServiceFactoryTests(TestCase):

    def setUp(self) -> None:
        self.mock_secret_manager = mock.MagicMock(spec=SecretManagerServiceClient)
        self.mock_secret_manager.access_secret_version.side_effect = self.get_secret
        self.sendgrid_api_key_secret = "projects/test-project/secrets/sendgrid-api-key/versions/latest"
        self.paubox_api_key_secret = "projects/test-project/secrets/paubox-api-key/versions/latest"

        self.secrets = {
            self.sendgrid_api_key_secret: "sendgrid_api_key".encode(),
            self.paubox_api_key_secret: "paubox_api_key".encode()
        }
        self.environment = {
            "SENDGRID_API_KEY_SECRET": self.sendgrid_api_key_secret,
            "PAUBOX_API_KEY_SECRET": self.paubox_api_key_secret,
            "PAUBOX_API_HOST": "https://api.paubox.net/v1/test"
        }

        self.factory = EmailServiceFactory(self.environment, self.mock_secret_manager)

    def get_secret(self, name: str) -> str:
        if name not in self.secrets:
            raise NotFound

        return AccessSecretVersionResponse(
            name=name,
            payload=SecretPayload(
                data=self.secrets[name]
            )
        )

    def test_create_sendgrid_service(self):
        self.environment["INSECURE_EMAILS"] = "1"

        service = self.factory.create_service()

        self.assertIsInstance(service, SendgridEmailService)

    def test_create_paubox_service(self):
        service = self.factory.create_service()

        self.assertIsInstance(service, PauboxEmailService)
