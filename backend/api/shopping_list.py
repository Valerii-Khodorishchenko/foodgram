from datetime import datetime


def generate_txt_shopping_list(ingredients, recipes):
    current_date = datetime.now().strftime('%d-%m-%Y')
    ingredients_lines = [
        '{}. {}/{}: {}'.format(
            i,
            item['product__name'].capitalize(),
            item['product__measurement_unit'],
            item['amount'],
        )
        for i, item in enumerate(ingredients, start=1)
    ]
    recipes_lines = [
        f'- {recipe.name} ({recipe.author})' for recipe in recipes
    ]
    return '\n'.join([
        f'Дата составления списка: {current_date}',
        'Список продуктов:',
        *ingredients_lines,
        'Рецепты:',
        *recipes_lines
    ])
