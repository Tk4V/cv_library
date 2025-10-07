"""
Management command to run Celery Beat scheduler.
"""
from django.core.management.base import BaseCommand
import subprocess
import sys


class Command(BaseCommand):
    help = 'Run Celery Beat scheduler for periodic tasks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--loglevel',
            type=str,
            default='info',
            choices=['debug', 'info', 'warning', 'error', 'critical'],
            help='Log level'
        )
        parser.add_argument(
            '--pidfile',
            type=str,
            default='celerybeat.pid',
            help='PID file for Beat process'
        )

    def handle(self, *args, **options):
        loglevel = options['loglevel']
        pidfile = options['pidfile']

        self.stdout.write(
            self.style.SUCCESS('Starting Celery Beat scheduler...')
        )
        
        cmd = [
            'celery', '-A', 'CVProject', 'beat',
            '--loglevel', loglevel,
            '--pidfile', pidfile
        ]
        
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'Error running Celery Beat: {e}')
            )
            sys.exit(1)
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('Celery Beat stopped by user')
            )





