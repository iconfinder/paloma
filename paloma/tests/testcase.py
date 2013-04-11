from django.test import TestCase as DjangoTestCase
from django.core import mail


class AssertMailSentContext(object):
    """Context manager for implementing TestCase.assertMailsSent.
    """

    def __init__(self,
                 expected_sent,
                 test_case):
        """Initialize a sent mail assertion context.

        :param expected_sent:
            Number of e-mails that are expected to have been sent within the
            context.
        :param test_case: Test case.
        """

        self.expected_sent = expected_sent
        self.failure_exception = test_case.failureException
        self.sent_before = None

    def __enter__(self):
        self.sent_before = len(mail.outbox)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        # Determine how many e-mails were actually sent.
        actual_sent = len(mail.outbox) - self.sent_before

        # Raise an exception if the expectation isn't met.
        if not exc_type and actual_sent != self.expected_sent:
            raise self.failure_exception(
                'expected %d e-mail%s to be sent, but %d was actually sent' % (
                    self.expected_sent,
                    ('s' if self.expected_sent != 1 else ''), actual_sent
                )
            )


class TestCase(DjangoTestCase):
    """Base test case.

    Provides a series of easy to use assertions for common test cases.
    """

    def assertMailsSent(self, expected_sent):
        """Fail unless an expected number of e-mails has been sent.

        Should be used for wrapping contextually:

        ::

            with self.assertMailsSent(5):
                do_something()

        :param expected_sent:
            Number of e-mails that are expected to be sent within the context.
        """

        return AssertMailSentContext(expected_sent, self)
