import csv
from django.http import HttpRequest, HttpResponse
from django.db.models import QuerySet
from django.db.models.options import Options
# HttpResponse позволяет складывать данные как будто это файл
# csv позволяет записывать данные в очень просто виде

class ExportCSVMixin:
    def export_csv(self, request: HttpRequest, queryset: QuerySet):
        meta: Options = self.model._meta
        fields_names = [field.name for field in meta.fields] # Список из строк с названиями полей в модели

        response = HttpResponse(content_type="text/csv") # Нужен чтобы записывать в него результат
        response["Content-Disposition"] = f"attachment; filename={meta}-export.csv" # Чтобы файл можно было скачать
        csv_writer = csv.writer(response)  # Записываем результат в ответ
        csv_writer.writerow(fields_names)  # Записываем заголовки

        for obj in queryset: # Записываем все поля моделей в строчку
            csv_writer.writerow([getattr(obj, field)for field in fields_names])

        return response

        export_csv.short_description = "Export as CSV" # Назначаем описание