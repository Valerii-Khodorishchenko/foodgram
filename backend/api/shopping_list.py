import csv

from django.contrib.staticfiles import finders
from io import BytesIO, StringIO
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def get_ingredients(shopping_cart):
    ingredients = {}
    for recipe in shopping_cart:
        for component in recipe.components.all():
            ingredient = component.ingredient
            amount = component.amount
            unit = ingredient.measurement_unit
            if ingredient.name in ingredients:
                ingredients[ingredient.name]['amount'] += amount
            else:
                ingredients[ingredient.name] = {'amount': amount, 'unit': unit}
    return ingredients


def generate_txt_shopping_list(shopping_cart):
    ingredients = get_ingredients(shopping_cart)
    lines = ['Список покупок:\n']
    for name, data in ingredients.items():
        lines.append(f'- {name}: {data["amount"]} {data["unit"]}\n')
    return ''.join(lines)


def generate_pdf_shopping_list(shopping_cart):
    font_path = finders.find('fonts/arial.ttf')
    if not font_path:
        raise FileNotFoundError('Шрифт не найден')
    pdfmetrics.registerFont(TTFont('Arial', font_path))
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.setFont('Arial', 12)
    pdf.drawString(100, 800, "Список покупок:")
    y_position = 780
    ingredients = get_ingredients(shopping_cart)
    for name, data in ingredients.items():
        pdf.drawString(
            100, y_position, f'- {name}: {data["amount"]} {data["unit"]}'
        )
        y_position -= 20
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


def generate_csv_shopping_list(shopping_cart):
    output = StringIO()
    writer = csv.writer(
        output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL
    )
    writer.writerow(['Ингредиент', 'Количество', 'Единицы измерения'])
    ingredients = get_ingredients(shopping_cart)
    for name, data in ingredients.items():
        writer.writerow([name, data['amount'], data['unit']])
    output.seek(0)
    return output.getvalue()
