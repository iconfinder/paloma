"""Paloma - view-style class based e-mailing.

Inspired by the recent move from method based views to the more inheritance
friendly class based views. Send e-mails in Django is currently still a
bastardized procedure, which Paloma aims to mitigate.
"""

from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


class Mail(object):
    """Base mail class.

    :ivar subject: Subject of the e-mail.
    :ivar from_email: Sender's e-mail address.
    :ivar from_name: Sender's name.
    """

    subject = None
    from_email = None
    from_name = None
    attachments = None

    def __init__(self, subject=None, from_email=None, from_name=None):
        """Initialize an e-mail.

        :param subject: Subject of the e-mail.
        :param from_email:
            Sender's e-mail address. If ``None``, defaults to the
            ``DEFAULT_FROM_EMAIL`` setting if available. Default ``None``.
        :param from_name:
            Sender's name. If ``None``, defaults to the ``DEFAULT_FROM_NAME``
            setting if available. Default ``None``.
        """

        if subject:
            self.subject = subject
        if from_email:
            self.from_email = from_email
        elif not self.from_email:
            self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        if from_name:
            self.from_name = from_name
        elif not self.from_name:
            self.from_name = getattr(settings, 'DEFAULT_FROM_NAME', None)
        self.attachments = {}

    def send(self,
             to,
             text_body,
             html_body=None,
             subject=None):
        """Send the e-mail.

        :param to: Recipient of the e-mail.
        :param text_body: Plain text e-mail body.
        :param html_body: Rich HTML e-mail body.
        :param subject:
            Subject. If not provided, the class instance variable will be used.
        """

        from_combined = '%s <%s>' % (
            self.from_name,
            self.from_email
        ) if self.from_name else self.from_email

        message = EmailMultiAlternatives(subject or self.subject,
                                         text_body,
                                         from_combined,
                                         [to])

        if html_body:
            message.attach_alternative(html_body, "text/html")

        # Attach any files.
        for filename, (data, mime_type) in self.attachments.items():
            message.attach(filename, data, mime_type)

        # Send the message.
        message.send()

    def attach_file(self,
                    filename,
                    path,
                    mime_type=None):
        """Attach a file to the e-mail.

        :param filename: Filename in the e-mail.
        :param path: Path to the file to attach.
        :param mime_type:
            MIME type of the attachment. If ``None``, the MIME type will be
            guessed from the filename.
        """

        with open(path, 'rb') as attachment_file:
            self.attachments[filename] = (attachment_file.read(),
                                          mime_type)
            attachment_file.close()


class TemplateMail(Mail):
    """Template mail class.

    :ivar subject: Subject of the e-mail.
    :ivar from_email: Sender's e-mail address.
    :ivar from_name: Sender's name.
    :ivar context: Recipient independent context.
    :ivar subject_template_name:
        Template to use for the subject line of the e-mail. If provided, the
        subject template will be prioritized over the subject variable.
    :ivar text_template_name:
        Template to use for the plain text body of the e-mail.
    :ivar html_template_name:
        Template to use for the HTML body of the e-mail.
    """

    subject_template_name = None
    text_template_name = None
    html_template_name = None
    context = None

    def __init__(self,
                 subject_template_name=None,
                 text_template_name=None,
                 html_template_name=None,
                 context=None,
                 subject=None,
                 from_email=None,
                 from_name=None):
        """Initialize a template based e-mail.

        :param subject_template_name:
            Template to use for the subject line of the e-mail. If provided,
            the subject template will be prioritized over the subject variable.
        :param text_template_name:
            Template to use for the plain text body of the e-mail.
        :param html_template_name:
            Template to use for the HTML body of the e-mail.
        :param context: Recipient independent context.
        :param subject: Subject of the e-mail.
        :param from_email:
            Sender's e-mail address. If ``None``, defaults to the
            ``DEFAULT_FROM_EMAIL`` setting if available. Default ``None``.
        :param from_name:
            Sender's name. If ``None``, defaults to the ``DEFAULT_FROM_NAME``
            setting if available. Default ``None``.
        """

        if subject_template_name:
            self.subject_template_name = subject_template_name
        if text_template_name:
            self.text_template_name = text_template_name
        if html_template_name:
            self.html_template_name = html_template_name

        if context:
            self.context = context
        elif not self.context:
            self.context = {}

        super(TemplateMail, self).__init__(subject=subject,
                                           from_email=from_email,
                                           from_name=from_name)

    def send(self, to, context={}):
        """Send the e-mail.

        :param to: Recipient of the e-mail.
        :param context: Recipient-specific template context.
        """

        # Construct the local context.
        local_context = {}
        for k, v in local_contest.items():
            local_context[k] = v
        if context:
            for k, v in context.items():
                local_context[k] = v

        # Render what needs to be rendered.
        subject = None
        if self.subject_template_name:
            subject = ''.join(render_to_string(self.subject_template_name,
                                               local_context)
                              .strip()
                              .splitlines())

        text_body = render_to_string(self.text_template_name,
                                     local_context).strip()

        html_body = None
        if self.html_template_name:
            html_body = render_to_string(self.html_template_name,
                                         local_context).strip()

        super(TemplateMail, self).send(to, text_body, html_body, subject)
