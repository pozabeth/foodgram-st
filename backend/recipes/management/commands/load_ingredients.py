import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient

DATA_PATH = os.path.join(settings.BASE_DIR, "data", "ingredients.json")


class Command(BaseCommand):
    help = f"Загружает ингредиенты из файла {DATA_PATH}"

    def handle(self, *args, **kwargs):
        if Ingredient.objects.exists():
            self.stdout.write(self.style.WARNING("Ингредиенты уже загружены."))
            return

        self.stdout.write(self.style.NOTICE("Начата загрузка ингредиентов..."))

        try:
            with open(DATA_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)

            ingredients = []
            for item in data:
                fields = item.get("fields", {})
                name = fields.get("name")
                unit = fields.get("measurement_unit")
                if name and unit:
                    ingredients.append(
                        Ingredient(name=name.strip(),
                                   measurement_unit=unit.strip())
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"Некорректные данные — {item}")
                    )
            count = len(ingredients)
            Ingredient.objects.bulk_create(ingredients)
            self.stdout.write(
                self.style.SUCCESS(f"Загружено: {count} ингредиентов.")
            )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Файл не найден: {DATA_PATH}"))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f"Ошибка чтения: {DATA_PATH}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Неизвестная ошибка: {e}"))
