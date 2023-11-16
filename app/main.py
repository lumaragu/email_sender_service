import os

from google.cloud.secretmanager_v1 import SecretManagerServiceClient

from email_sender.application import Application
from email_sender.email_service_factory import EmailServiceFactory

secretmanager_client = SecretManagerServiceClient()

email_service_factory = EmailServiceFactory(os.environ, secretmanager_client)
email_service = email_service_factory.create_service()

app = Application(email_service)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
