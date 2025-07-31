import os
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = 'Export all models to Mermaid diagrams'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='mermaid_schemas',
            help='Output directory for Mermaid files'
        )

    def handle(self, *args, **options):
        output_dir = options['output_dir']
        os.makedirs(output_dir, exist_ok=True)

        for app_config in apps.get_app_configs():
            app_name = app_config.label
            mmd_path = os.path.join(output_dir, f'{app_name}.mmd')

            with open(mmd_path, 'w', encoding='utf-8') as f:
                # Генерируем схему для приложения
                content = self.generate_app_schema(app_config)
                f.write(content)

            self.stdout.write(self.style.SUCCESS(f'Saved {mmd_path}'))

    def generate_app_schema(self, app_config):
        lines = ['```mermaid', 'classDiagram']

        for model in app_config.get_models():
            class_name = model.__name__
            lines.append(f'    class {class_name} {{')

            # Добавляем поля
            for field in model._meta.fields:
                field_type = field.get_internal_type()
                lines.append(f'        {field.name} : {field_type}')

                # Добавляем choices если есть
                if hasattr(field, 'choices') and field.choices:
                    choices = [f"{k}={v}" for k, v in field.choices]
                    lines.append(f'        /* Choices: {", ".join(choices)} */')

            lines.append('    }')

            # Добавляем связи
            for field in model._meta.get_fields():
                if field.is_relation and field.related_model:
                    relation_type = "-->"
                    if field.many_to_many:
                        relation_type = "o--"
                    elif field.one_to_one:
                        relation_type = "|--"

                    lines.append(f'    {class_name} {relation_type} {field.related_model.__name__} : "{field.name}"')

        lines.append('```')
        return '\n'.join(lines)