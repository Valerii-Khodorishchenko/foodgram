from datetime import datetime

from django.db.models import Sum



def get_ingredients(shopping_cart):
    ingredients = (
        shopping_cart.values(
            'components__product__name',
            'components__product__measurement_unit'
        )
        .annotate(total_amount=Sum('components__amount'))
        .order_by('components__product__name')
    )
    return {
        item['components__product__name']: {
            'amount': item['total_amount'],
            'unit': item['components__product__measurement_unit'],
        }
        for item in ingredients
    }

import pymorphy2
morph = pymorphy2.MorphAnalyzer()
dict_exception = {'банка': ('банки', 'банок')}
def pluralize(word, num):
    if (words := dict_exception.get(word)) is not None:
        return f'{words[0]}' if num < 5 else {words[1]}
    parsed_word = morph.parse(word)[0]
    return f'{parsed_word.make_agree_with_number(num).word}'
    

def generate_txt_shopping_list(shopping_cart):
    ingredients = get_ingredients(shopping_cart)
    recipes = {recipe.name for recipe in shopping_cart}
    current_date = datetime.now().strftime('%d-%m-%Y')
    ingredients_lines = [
        '{0}. {1}: {2} {3}\n'.format(i+1, name.capitalize(), data["amount"], pluralize(data["unit"], int(data["amount"])))
        for i, (name, data) in enumerate(ingredients.items())
    ]
    print(ingredients_lines)
    recipes_lines = [f'- {recipe}' for recipe in recipes]
    return '\n'.join([
        f'Дата составления списка: {current_date}',
        'Список продуктов:\n',
        *ingredients_lines,
        '\nРецепты:\n',
        *recipes_lines
    ])
