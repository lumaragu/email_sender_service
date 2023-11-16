import os

from email_sender.email import Email, Attachment


class TestEmailMixin:

    def setUpEmail(self):
        self.sender = "info@lumaragu.com"
        self.reply_to = "reply@lumaragu.com"
        self.recipients = ["luis@lumaragu.com"]
        self.subject = "Test Subject"
        self.text_content = "Hello!"
        self.html_content = "<html><body>Hello!</body></html>"
        self.attachment = Attachment(
            filename="report.pdf",
            content_type="application/pdf",
            file_contents=os.urandom(1000)
        )

        self.email = Email(
            sender=self.sender,
            reply_to=self.reply_to,
            recipients=self.recipients,
            subject=self.subject,
            text_content=self.text_content,
            html_content=self.html_content,
            attachments=[self.attachment]
        )
