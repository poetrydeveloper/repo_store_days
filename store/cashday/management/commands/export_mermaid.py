import os
import zlib
import base64
import requests
from django.core.management.base import BaseCommand
from django.apps import apps
from urllib.parse import quote


class Command(BaseCommand):
    help = 'Export Django models to Mermaid diagrams with reliable PNG export'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            default='mermaid_diagrams',
            help='Output directory for diagrams'
        )
        parser.add_argument(
            '--skip-png',
            action='store_true',
            help='Skip PNG generation'
        )

    def handle(self, *args, **options):
        output_dir = options['output_dir']
        os.makedirs(output_dir, exist_ok=True)

        for app_config in apps.get_app_configs():
            app_name = app_config.label
            mmd_content = self.generate_mermaid_diagram(app_config)

            # Сохраняем .mmd
            mmd_path = os.path.join(output_dir, f'{app_name}.mmd')
            with open(mmd_path, 'w', encoding='utf-8') as f:
                f.write(mmd_content)
            self.stdout.write(self.style.SUCCESS(f'Saved Mermaid: {mmd_path}'))

            # Генерируем PNG если не пропущено
            if not options['skip_png']:
                png_path = os.path.join(output_dir, f'{app_name}.png')
                self.mmd_to_png(mmd_content, png_path)

    def mmd_to_png(self, mmd_code, output_path):
        """Конвертация через mermaid.ink с обработкой ошибок"""
        try:
            # 1. Сжимаем данные
            compressed = zlib.compress(mmd_code.encode())
            # 2. Кодируем в base64 URL-safe
            encoded = base64.urlsafe_b64encode(compressed).decode()
            # 3. URL-кодируем
            url_encoded = quote(encoded)

            url = f"https://mermaid.ink/img/{url_encoded}"

            response = requests.get(url, timeout=15)
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                f.write(response.content)

            self.stdout.write(self.style.SUCCESS(f'Saved PNG: {output_path}'))

        except requests.exceptions.RequestException as e:
            self.stderr.write(f"PNG Error: {str(e)}. Try opening manually at: https://mermaid.live")
        except Exception as e:
            self.stderr.write(f"Unexpected error: {str(e)}")

    def generate_mermaid_diagram(self, app_config):
        """Генерация Mermaid-кода с улучшенным форматированием"""
        diagram = ["classDiagram"]

        models = list(app_config.get_models())
        max_class_width = max(len(m.__name__) for m in models) if models else 0

        # Добавляем классы
        for model in models:
            class_def = [
                f"    class {model.__name__} {{",
                *self.get_field_lines(model),
                "    }"
            ]
            diagram.extend(class_def)

        # Добавляем связи
        for model in models:
            for field in model._meta.get_fields():
                if self.is_valid_relation(field, models):
                    diagram.append(self.get_relation_line(model, field))

        return "\n".join(diagram)

    def get_field_lines(self, model):
        """Форматирование полей модели"""
        lines = []
        for field in model._meta.fields:
            field_line = f"        {field.name} : {field.get_internal_type()}"
            if hasattr(field, 'choices') and field.choices:
                choices = ", ".join(f"{k}={v}" for k, v in field.choices)
                field_line += f"  # Choices: {choices}"
            lines.append(field_line)
        return lines

    def is_valid_relation(self, field, all_models):
        """Проверка валидности связи"""
        return (field.is_relation
                and hasattr(field, 'related_model')
                and field.related_model in all_models)

    def get_relation_line(self, model, field):
        """Генерация строки связи"""
        arrow_map = {
            'ManyToManyField': '}o--o{',
            'OneToOneField': '|--',
            'ForeignKey': '-->'
        }
        arrow = arrow_map.get(field.get_internal_type(), '-->')

        multiplicity = {
            'ManyToManyField': ('*', '*'),
            'OneToOneField': ('1', '1'),
            'ForeignKey': ('1', '*')
        }.get(field.get_internal_type(), ('', ''))

        return (f"    {model.__name__} \"{multiplicity[0]}\" {arrow} "
                f"\"{multiplicity[1]}\" {field.related_model.__name__} : "
                f"\"{field.name}\"")