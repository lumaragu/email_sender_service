import abc

from email_sender.email import Email


class EmailService(abc.ABC):

    @abc.abstractmethod
    def send_email(self, email: Email):
        pass
