# Environment Bootstrapping

import os

from django.conf import settings

if not settings.configured:
    settings.configure(
        INSTALLED_APPS=(),
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            },
        },
        TEMPLATE_DIRS=(
            os.path.join(os.path.dirname(__file__), 'templates'),
        )
    )


# Tests

from cStringIO import StringIO
import unittest

from nose.plugins import PluginTester
from django.template.loader import get_template

from templateusage import TemplateUsageReportPlugin


class TestPluginFoo(PluginTester, unittest.TestCase):
    activate = '--with-template-usage-report'
    args = ('--ignore-template-prefix=ignored/',)
    plugins = [TemplateUsageReportPlugin()]

    TEMPLATE_NAME = 'example.html'

    def test_basic(self):
        self.assertIn(self.TEMPLATE_NAME, self.plugins[0].used_templates)

    def test_included(self):
        self.assertIn('included.html', self.plugins[0].used_templates)

    def test_unused(self):
        self.assertIn('unused.html', self.plugins[0].unused_templates)

    def test_ignored(self):
        self.assertNotIn('ignored.html', self.plugins[0].unused_templates)

    def makeSuite(self):
        class TestCase(unittest.TestCase):
            def runTest(_self):
                get_template(self.TEMPLATE_NAME)
        return unittest.TestSuite([TestCase()])
