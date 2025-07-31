from django.core.management.base import BaseCommand
from django_extensions.management.commands import graph_models

class Command(BaseCommand):
    help = 'Generates database schema visualization'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            default='schema.png',
            help='Output file name (default: schema.png)'
        )

    def handle(self, *args, **options):
        output_file = options['output']
        cmd = graph_models.Command()
        cmd.run_from_argv(['manage.py', 'graph_models', '-a', '-g', '-o', output_file])
        self.stdout.write(self.style.SUCCESS(f'Schema saved to {output_file}'))