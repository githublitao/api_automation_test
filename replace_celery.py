from __future__ import absolute_import, unicode_literals

from celery.bin import celery

from djcelery.app import app
from djcelery.management.base import CeleryCommand

base = celery.CeleryCommand(app=app)


class Command(CeleryCommand):
    """The celery command."""
    help = 'celery commands, see celery help'
    cc_options = CeleryCommand.options if CeleryCommand.options else []
    base_options = base.get_options() if base.get_options() else []
    if hasattr(base, "preload_options"):
        preload_options = basffffe.preload_options if base.preload_options else []
    else:
        preload_options = []
    preload_options = base.preload_options if base.preload_options else []
    # options = (cc_options +
    #            base_options +
    #            preload_options)

    def run_from_argv(self, argv):
        argv = self.handle_default_options(argv)
        base.execute_from_commandline(
            ['{0[0]} {0[1]}'.format(argv)] + argv[2:],
        )
