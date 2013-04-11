import os
from paloma import Mail, TemplateMail
from django.core import mail
from django.test.utils import override_settings
from .testcase import TestCase


TEMPLATE_DIRS = (os.path.join(os.path.abspath(os.path.dirname(__file__)),
                              'templates'), )


@override_settings(DEFAULT_FROM_EMAIL='default@example.com',
                   DEFAULT_FROM_NAME='Default sender')
class MailTestCase(TestCase):
    """Test case for :class:`Mail`.
    """

    def assertSimple(self, sent, **kwargs):
        self.assertEqual(sent.subject,
                         kwargs.pop('subject', 'Subject of the e-mail'))
        self.assertEqual(sent.body, kwargs.pop('body', 'Body of the e-mail'))
        from_email = kwargs.pop('from_email', 'default@example.com')
        from_name = kwargs.pop('from_name', 'Default sender')
        if from_name:
            self.assertEqual(sent.from_email, '%s <%s>' % (from_name,
                                                           from_email))
        else:
            self.assertEqual(sent.from_email, from_email)
        self.assertEqual(len(sent.to), 1)
        self.assertEqual(sent.to[0], kwargs.pop('to', 'test@example.com'))

        html_alternatives = filter(lambda a: a[1] == 'text/html',
                                   sent.alternatives)
        self.assertEqual(any(html_alternatives), 'html_body' in kwargs)

        if 'html_body' in kwargs:
            html_body = kwargs.pop('html_body')
            actual_html_body, mime_type = html_alternatives[0]
            self.assertEqual(html_body, actual_html_body)

    def test_init__defaults_to_setting_for_from_email_and_from_name(self):
        """Mail().__init__(from_name=None, from_email=None) uses defaults
        """

        class TestMail(Mail):
            subject = 'Subject of the e-mail'

        # Test with global.
        with override_settings(DEFAULT_FROM_EMAIL='someone@example.com',
                               DEFAULT_FROM_NAME='Someone'):
            m = TestMail()
            self.assertEqual(m.from_email, 'someone@example.com')
            self.assertEqual(m.from_name, 'Someone')

            with self.assertMailsSent(1):
                m.send('test@example.com', 'Body of the e-mail')
            self.assertSimple(mail.outbox[-1],
                              from_email='someone@example.com',
                              from_name='Someone')

    def test_send__respects_from_email_ivar_from_sent(self):
        """Mail().send(..) respects from_email instance variable
        """

        class TestMail(Mail):
            subject = 'Subject of the e-mail'
            from_email = 'from@example.com'

        # Test without global.
        with override_settings(DEFAULT_FROM_EMAIL=None):
            with self.assertMailsSent(1):
                TestMail().send('test@example.com', 'Body of the e-mail')
            self.assertSimple(mail.outbox[-1], from_email='from@example.com')

        # Test with global.
        with self.assertMailsSent(1):
            TestMail().send('test@example.com', 'Body of the e-mail')
        self.assertSimple(mail.outbox[-1], from_email='from@example.com')

    def test_send__respects_from_name_ivar_from_sent(self):
        """Mail().send(..) respects from_name instance variable
        """

        class TestMail(Mail):
            subject = 'Subject of the e-mail'
            from_name = 'Overridden'

        # Test without global.
        with override_settings(DEFAULT_FROM_NAME=None):
            with self.assertMailsSent(1):
                TestMail().send('test@example.com', 'Body of the e-mail')
            self.assertSimple(mail.outbox[-1], from_name='Overridden')

        # Test with global.
        with self.assertMailsSent(1):
            TestMail().send('test@example.com', 'Body of the e-mail')
        self.assertSimple(mail.outbox[-1], from_name='Overridden')

    def test_send__respects_subject(self):
        """Mail().send(..) respects subject argument
        """

        class TestMail(Mail):
            subject = 'Not this subject of the e-mail'

        with self.assertMailsSent(1):
            TestMail().send('test@example.com',
                            'Body of the e-mail',
                            subject='This is the subject')
        self.assertSimple(mail.outbox[-1], subject='This is the subject')

    def test_send__with_html_body(self):
        """Mail().send(..) with HTML body sends both plain text and HTML body
        """

        class TestMail(Mail):
            subject = 'Subject of the e-mail'

        html_body = '<h1>HTML body of the e-mail</h1>'
        with self.assertMailsSent(1):
            TestMail().send('test@example.com',
                            'Body of the e-mail',
                            html_body)
        self.assertSimple(mail.outbox[-1], html_body=html_body)


@override_settings(DEFAULT_FROM_EMAIL='default@example.com',
                   DEFAULT_FROM_NAME='Default sender',
                   TEMPLATE_DIRS=TEMPLATE_DIRS)
class TemplateMailTestCase(TestCase):
    """Test case for :class:`TemplateMail`.
    """

    def assertSimple(self, sent, body, **kwargs):
        self.assertEqual(sent.subject,
                         kwargs.pop('subject', 'Subject of the e-mail'))
        self.assertEqual(sent.body, body)
        from_email = kwargs.pop('from_email', 'default@example.com')
        from_name = kwargs.pop('from_name', 'Default sender')
        if from_name:
            self.assertEqual(sent.from_email, '%s <%s>' % (from_name,
                                                           from_email))
        else:
            self.assertEqual(sent.from_email, from_email)
        self.assertEqual(len(sent.to), 1)
        self.assertEqual(sent.to[0], kwargs.pop('to', 'test@example.com'))

        html_alternatives = filter(lambda a: a[1] == 'text/html',
                                   sent.alternatives)
        self.assertEqual(any(html_alternatives), 'html_body' in kwargs)

        if 'html_body' in kwargs:
            html_body = kwargs.pop('html_body')
            actual_html_body, mime_type = html_alternatives[0]
            self.assertEqual(html_body, actual_html_body)

    def test_send__only_text_template(self):
        """TemplateMail(<only text template>).send(..) sends expected e-mail
        """

        # Local context variable.
        class TestMail(TemplateMail):
            subject = 'Subject of the e-mail'
            text_template_name = 'test_mail.txt'

        with self.assertMailsSent(1):
            TestMail().send('test@example.com', {'a': 'in local context'})

        self.assertSimple(mail.outbox[-1],
                          body=u'Test body.\n\nHas variable in local context.')

        # Class context variable.
        class TestMail(TemplateMail):
            subject = 'Subject of the e-mail'
            text_template_name = 'test_mail.txt'

        with self.assertMailsSent(1):
            TestMail(context={'a': 'in class context'}) \
                .send('test@example.com')

        self.assertSimple(mail.outbox[-1],
                          body=u'Test body.\n\nHas variable in class context.')

        # Class and local context variable.
        class TestMail(TemplateMail):
            subject = 'Subject of the e-mail'
            text_template_name = 'test_mail.txt'

        with self.assertMailsSent(1):
            TestMail(context={'a': 'in class context'}) \
                .send('test@example.com',
                      {'a': 'in local context'})

        self.assertSimple(mail.outbox[-1],
                          body=u'Test body.\n\nHas variable in local context.')

    def test_send__templated(self):
        """TemplateMail(<templated>).send(..) sends expected e-mail
        """

        # Local context variable.
        class TestMail(TemplateMail):
            subject = 'Subject of the e-mail'
            subject_template_name = 'test_mail_subject.txt'
            text_template_name = 'test_mail.txt'
            html_template_name = 'test_mail.html'

        with self.assertMailsSent(1):
            TestMail().send('test@example.com', {'a': 'in local context'})

        body_format = u'Test body.\n\nHas variable %s.'
        html_body_format = u'''<html>
    <body>
        <p>Test body.</p>
        <p>Has variable %s.</p>
    </body>
</html>'''

        self.assertSimple(
            mail.outbox[-1],
            subject=u'Test subject with variable in local context',
            body=body_format % ('in local context'),
            html_body=html_body_format % ('in local context')
        )

        # Class context variable.
        class TestMail(TemplateMail):
            subject = 'Subject of the e-mail'
            subject_template_name = 'test_mail_subject.txt'
            text_template_name = 'test_mail.txt'
            html_template_name = 'test_mail.html'

        with self.assertMailsSent(1):
            TestMail(context={'a': 'in class context'}) \
                .send('test@example.com')

        self.assertSimple(
            mail.outbox[-1],
            subject=u'Test subject with variable in class context',
            body=body_format % ('in class context'),
            html_body=html_body_format % ('in class context')
        )

        # Class and local context variable.
        class TestMail(TemplateMail):
            subject = 'Subject of the e-mail'
            subject_template_name = 'test_mail_subject.txt'
            text_template_name = 'test_mail.txt'
            html_template_name = 'test_mail.html'

        with self.assertMailsSent(1):
            TestMail(context={'a': 'in class context'}) \
                .send('test@example.com',
                      {'a': 'in local context'})

        self.assertSimple(
            mail.outbox[-1],
            subject=u'Test subject with variable in local context',
            body=body_format % ('in local context'),
            html_body=html_body_format % ('in local context')
        )


__all__ = (
    'MailTestCase',
    'TemplateMailTestCase',
)
