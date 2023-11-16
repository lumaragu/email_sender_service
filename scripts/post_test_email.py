import argparse
import json
from typing import List

from google.cloud import pubsub_v1


def make_payload(recipients: List[str]):
    return {
        "subject": "test",
        "email_from": "no_reply@lumaragu.com",
        "reply_to": "info@lumaragu.com",
        "recipients": recipients,
        "content": {
            "text/plain": "Test email",
            "text/html": "<html><body>Test email</body></html>"
        }
    }


def main(project: str, secure: bool, recipients: List[str]):
    security_setting = 'secure' if secure else 'insecure'
    pretty_recipients = ', '.join([f'"{recipient}"' for recipient in recipients])
    print(f"Posting {security_setting} test email on project '{project}' to {pretty_recipients}.")

    payload = make_payload(recipients)
    data = json.dumps(payload).encode()

    publisher_client = pubsub_v1.PublisherClient()
    pubsub_topic = f"projects/{project}/topics/{security_setting}-emails"
    future = publisher_client.publish(pubsub_topic, data)
    message = future.result()

    print(message)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project")
    parser.add_argument("--secure", action="store_true")
    parser.add_argument("recipients", nargs="+")
    args = parser.parse_args()

    main(**vars(args))
