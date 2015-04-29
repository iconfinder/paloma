"""Paloma - view-style class based e-mailing.

Inspired by the recent move from method based views to the more inheritance
friendly class based views. Send e-mails in Django is currently still a
bastardized procedure, which Paloma aims to mitigate.
"""

from django.conf import settings
from django.core.mail import EmailMultiAlternatives


if 'coffin' in settings.INSTALLED_APPS:
    from coffin.shortcuts import render_to_string
else:
    from django.template.loader import render_to_string


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
    cc = None
    bcc = None
    headers = None
    important = None

    def __init__(self,
                 subject=None,
                 from_email=None,
                 from_name=None,
                 cc=None,
                 bcc=None,
                 headers=None,
                 important=None):
        """Initialize an e-mail.

        :param subject: Subject of the e-mail.
        :param from_email:
            Sender's e-mail address. If ``None``, defaults to the
            ``DEFAULT_FROM_EMAIL`` setting if available. Default ``None``.
        :param from_name:
            Sender's name. If ``None``, defaults to the ``DEFAULT_FROM_NAME``
            setting if available. Default ``None``.
        :param cc:
            List of emails this message should be CC'd to
        :param bcc:
            List of emails this message should be BCC'd to
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
        if cc:
            self.cc = cc
        if bcc:
            self.bcc = bcc
        if headers:
            self.headers = headers
        self.important = important
        self.attachments = {}

    def send(self,
             to,
             text_body,
             html_body=None,
             subject=None,
             tags=None,
             metadata=None,
             cc=None,
             bcc=None,
             headers=None,
             important=None):
        """Send the e-mail.

        :param to: Recipient of the e-mail.
        :param text_body: Plain text e-mail body.
        :param html_body: Rich HTML e-mail body.
        :param subject:
            Subject. If not provided, the class instance variable will be used.
        :param tags: list of mandrill tags
        :param metadata: dict of mandrill metadata
        :param cc: list of emails this message should be CC'd to
        :param bcc: list of emails this message should be BCC'd to
        """

        from_combined = '%s <%s>' % (
            self.from_name,
            self.from_email
        ) if self.from_name else self.from_email

        cc = cc if cc is not None else self.cc
        bcc = bcc if bcc is not None else self.bcc
        headers = headers if headers is not None else self.headers

        message = EmailMultiAlternatives(subject or self.subject,
                                         text_body,
                                         from_combined,
                                         [to],
                                         cc=cc,
                                         bcc=bcc,
                                         headers=headers)

        if html_body:
            message.attach_alternative(html_body, "text/html")

        # Attach any files.
        for filename, (data, mime_type) in self.attachments.items():
            message.attach(filename, data, mime_type)

        # Optional Mandrill-specific extensions:
        if tags:
            message.tags = tags
        if metadata:
            message.metadata = metadata

        if important is None:
            important = self.important
        if important is not None:
            message.important = important

        # Send the message.
        message.send()

    def attach_file(self,
                    filename,
                    path_or_file,
                    mime_type=None):
        """Attach a file to the e-mail.

        :param filename: Filename in the e-mail.
        :param path_or_file: Path to the file or file object to attach.
        :param mime_type:
            MIME type of the attachment. If ``None``, the MIME type will be
            guessed from the filename.
        """

        if isinstance(path_or_file, (str, unicode)):
            with open(path_or_file, 'rb') as attachment_file:
                self.attachments[filename] = (attachment_file.read(),
                                              mime_type)
                attachment_file.close()
        else:
            self.attachments[filename] = (path_or_file.read(), mime_type)


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
                 from_name=None,
                 cc=None,
                 bcc=None,
                 headers=None,
                 important=None):
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
        :param cc:
            List of emails this message should be CC'd to
        :param bcc:
            List of emails this message should be BCC'd to
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
                                           from_name=from_name,
                                           cc=cc,
                                           bcc=bcc,
                                           headers=headers,
                                           important=None)

    def render_template(self, template_name, context):
        """Render a template.

        :param template_name: Template name.
        :type template_name: str
        :param context: Context.
        :returns: the rendered template.
        """

        return render_to_string(template_name, context)

    def send(self,
             to,
             context=None,
             tags=None,
             metadata=None,
             cc=None,
             bcc=None,
             headers=None,
             important=None):
        """Send the e-mail.

        :param to: Recipient of the e-mail.
        :param context: Recipient-specific template context.
        """

        # Construct the local context.
        local_context = {}
        if self.context:
            for k, v in self.context.items():
                local_context[k] = v
        if context:
            for k, v in context.items():
                local_context[k] = v

        # Render what needs to be rendered.
        subject = None
        if self.subject_template_name:
            subject = ''.join(self.render_template(self.subject_template_name,
                                                   local_context)
                              .strip()
                              .splitlines())

        text_body = self.render_template(self.text_template_name,
                                         local_context).strip()

        html_body = None
        if self.html_template_name:
            html_body = self.render_template(self.html_template_name,
                                             local_context).strip()

        super(TemplateMail, self).send(
            to=to,
            text_body=text_body,
            html_body=html_body,
            subject=subject,
            tags=tags,
            metadata=metadata,
            cc=cc,
            bcc=bcc,
            headers=headers,
            important=important
        )
