import random
import string

DEBUG = False

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.messages',
    'paloma',
)

TEST_RUNNER = 'django.test.simple.DjangoTestSuiteRunner'

SECRET_KEY = ''.join([random.choice(string.ascii_letters) for x in range(40)])

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'TEST_NAME': ':memory:',
    },
}
