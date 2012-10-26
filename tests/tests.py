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

import json
import tempfile
import unittest
from cStringIO import StringIO

from nose.plugins import PluginTester
from django.template.loader import get_template

from templateusage import TemplateUsageReportPlugin


class TemplateUsageReportTestMixin(PluginTester):
    TEMPLATE_NAME = 'example.html'

    activate = '--with-template-usage-report'
    plugins = [TemplateUsageReportPlugin()]

    def makeSuite(self):
        class TestCase(unittest.TestCase):
            def runTest(_self):
                get_template(self.TEMPLATE_NAME)
        return unittest.TestSuite([TestCase()])


class TemplateUsageReportPluginTestCase(TemplateUsageReportTestMixin, unittest.TestCase):
    def test_basic(self):
        self.assertIn(self.TEMPLATE_NAME, self.plugins[0].used_templates)

    def test_included(self):
        self.assertIn('included.html', self.plugins[0].used_templates)

    def test_unused(self):
        self.assertIn('unused.html', self.plugins[0].unused_templates)


class IgnoredDirectoryUsageReportPluginTestCase(TemplateUsageReportTestMixin, unittest.TestCase):
    args = ('--ignore-template-prefix=ignored/',)

    def test_ignored(self):
        self.assertNotIn('ignored/ignored.html', self.plugins[0].used_templates)
        self.assertNotIn('ignored/ignored.html', self.plugins[0].unused_templates)


class ReportFileTestCase(TemplateUsageReportTestMixin, unittest.TestCase):
    def setUp(self, *args, **kwargs):
        f = tempfile.NamedTemporaryFile(delete=False)
        f.close()
        self.filename = f.name
        self.args = ('--template-usage-report-file=%s' % self.filename,)
        super(ReportFileTestCase, self).setUp(*args, **kwargs)

    def tearDown(self):
        os.unlink(self.filename)

    def test_report_file(self):
        self.assertIsNotNone(self.plugins[0].outfile)

        with open(self.filename) as raw:
            report = json.load(raw)

            used = set(('example.html', 'included.html'))
            self.assertEqual(used, set(report['used']))

            unused = set(('unused.html', 'ignored/ignored.html'))
            self.assertEqual(unused, set(report['unused']))
