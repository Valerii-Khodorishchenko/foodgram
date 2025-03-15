from datetime import datetime


def generate_txt_shopping_list(ingredients, recipes):
    current_date = datetime.now().strftime('%d-%m-%Y')
    ingredients_lines = [
        (f'{i}. {item["product__name"]}: '
         f'{item["amount"]} {item["product__measurement_unit"]}\n')
        for i, item in enumerate(ingredients, start=1)
    ]
    recipes_lines = [
        f'- {recipe.name} ({recipe.author})\n' for recipe in recipes
    ]
    return ''.join([
        f'Дата составления списка: {current_date}',
        'Список продуктов:\n',
        *ingredients_lines,
        '\nРецепты:\n',
        *recipes_lines
    ])
