import os
import sys


os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
from tests import settings

settings.INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'django.contrib.admin',
    'django.contrib.sites',
    'paloma',
)


def run_tests(settings):
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner(interactive=False)
    failures = test_runner.run_tests(['paloma'])
    return failures


def main():
    failures = run_tests(settings)
    sys.exit(failures)


if __name__ == '__main__':
    main()
