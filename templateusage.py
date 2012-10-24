import sys

import mock
from django.template import TemplateDoesNotExist
from django.template.loader import find_template
from nose.plugins.base import Plugin


LINE_LENGTH = 70


class TemplateUsageReportPlugin(Plugin):
    enabled = False
    score = sys.maxint
    name = 'template-usage-report'

    def options(self, parser, env):
        parser.add_option('--with-%s' % self.name, dest='enabled', default=False,
            action='store_true', help='Enable template usage reporting.')

    def configure(self, options, conf):
        self.enabled = options.enabled

    def begin(self):
        self.used_templates = set()
        def register_template_usage(name, *args, **kwargs):
            result = find_template(name, *args, **kwargs)
            self.used_templates.add(name)
            return result

        self.patch = mock.patch('django.template.loader.find_template',
            side_effect=register_template_usage)
        self.patch.start()

    def report(self, stream):
        print >> stream, '=' * LINE_LENGTH
        print >> stream, 'Template Usage Report'
        print >> stream, '-' * LINE_LENGTH

        for template in self.used_templates:
            print >> stream, ' * ', template
