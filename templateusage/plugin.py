import json
import os
import string
import sys

import mock
from django.template import TemplateDoesNotExist
from django.template.loader import find_template
from nose.plugins.base import Plugin


LINE_LENGTH = 70


def heading(stream, value):
    print >> stream, '=' * LINE_LENGTH
    print >> stream, value
    print >> stream, '-' * LINE_LENGTH


def bulleted(stream, values):
    for value in values:
        print >> stream, ' * ', value


def files(directory):
    """
    Returns a set of paths of all files located within the provided directory.
    """
    paths = set()
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            paths.add(os.path.relpath(path, directory))
    return paths


class TemplateUsageReportPlugin(Plugin):
    enabled = False
    score = sys.maxint
    name = 'template-usage-report'

    def options(self, parser, env):
        parser.add_option('--with-%s' % self.name, dest='enabled', default=False,
            action='store_true', help='Enable template usage reporting.')

        parser.add_option("--ignore-template-prefix", dest='ignore_prefixes',
            action='append', help='Add a template directory to the ignore list.',
            default=[])

        parser.add_option('--template-usage-report-file', dest='outfile',
            help='Write JSON template usage report to file.')

    def configure(self, options, conf):
        self.enabled = options.enabled
        if not self.enabled:
            return

        ignore_prefixes = options.ignore_prefixes
        # Allow for multiple values in a single argument, e.g. from `setup.cfg`.
        if len(ignore_prefixes) == 1:
            ignore_prefixes = map(string.strip, ignore_prefixes[0].split('\n'))

        self.ignore_prefixes = ignore_prefixes
        self.outfile = options.outfile

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
        heading(stream, 'Used Templates (%s)' % len(self.used_templates))
        bulleted(stream, sorted(self.used_templates))

        from django.conf import settings
        from django.template.loader import template_source_loaders
        from django.template.loaders.filesystem import Loader as FileSystemLoader
        from django.template.loaders.app_directories import Loader as AppDirectoryLoader

        def filter_ignored(paths):
            for path in paths:
                for prefix in self.ignore_prefixes:
                    if os.path.commonprefix((prefix, path)) == prefix:
                        break
                else:
                    yield path

        available_templates = set()
        for loader in template_source_loaders:
            # XXX: This should only execute once per class since you can't
            # actually instantiate the loaders multiple times.
            if isinstance(loader, FileSystemLoader):
                for directory in settings.TEMPLATE_DIRS:
                    available_templates.update(filter_ignored(files(directory)))

            elif isinstance(loader, AppDirectoryLoader):
                from django.template.loaders.app_directories import app_template_dirs
                for directory in app_template_dirs:
                    available_templates.update(filter_ignored(files(directory)))

        self.unused_templates = available_templates - self.used_templates
        heading(stream, 'Unused Templates (%s)' % len(self.unused_templates))
        bulleted(stream, sorted(self.unused_templates))

        if self.outfile:
            with open(self.outfile, 'w') as out:
                json.dump({
                    'used': list(self.used_templates),
                    'unused': list(self.unused_templates),
                }, out)
