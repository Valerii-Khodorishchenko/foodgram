import numpy

from django.contrib import admin
from django.utils.translation import gettext_lazy


class CookingTimeFilter(admin.SimpleListFilter):
    title = gettext_lazy('Время приготовления')
    parameter_name = 'cooking_time'

    def separators(self, queryset):
        cooking_times = numpy.array(
            queryset.values_list('cooking_time', flat=True)
        )
        quick = int(numpy.floor(numpy.percentile(cooking_times, 33)))
        medium = int(numpy.floor(numpy.percentile(cooking_times, 66)))
        return quick, medium

    def lookups(self, request, model_admin):
        recipes = model_admin.get_queryset(request)
        quick, medium = self.separators(recipes)
        quick_recipes = recipes.filter(cooking_time__lt=quick)
        medium_recipes = recipes.filter(
            cooking_time__gte=quick, cooking_time__lte=medium
        )
        slow_recipes = recipes.filter(cooking_time__gt=medium)

        return (
            ('quick', 'быстрее {0}минут ({1})'.format(
                quick, quick_recipes.count()
            )),
            ('medium', 'быстрее {0}минут ({1})'.format(
                medium, medium_recipes.count()
            )),
            ('slow', 'долше {0}минут ({1})'.format(
                medium, slow_recipes.count()
            ))
        )

    def queryset(self, request, queryset):
        quick, medium = self.separators(queryset)
        if self.value() == 'quick':
            return queryset.filter(cooking_time__lt=quick)
        if self.value() == 'medium':
            return queryset.filter(
                cooking_time__gte=quick, cooking_time__lt=medium
            )
        if self.value() == 'slow':
            return queryset.filter(cooking_time__gte=medium)
        return queryset


class HasRecipesFilter(admin.SimpleListFilter):
    title = gettext_lazy('Есть рецепты')
    parameter_name = 'has_recipes'

    def lookups(self, request, model_admin):
        return (('yes', 'Да'), ('no', 'Нет'))

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(recipes__isnull=False).distinct()
        if self.value() == 'no':
            return queryset.filter(recipes__isnull=True)
        return queryset


class HasSubscriptionsFilter(admin.SimpleListFilter):
    title = gettext_lazy('Есть подписки')
    parameter_name = 'has_subscriptions'

    def lookups(self, request, model_admin):
        return (('yes', 'Да'), ('no', 'Нет'))

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(followings__isnull=False).distinct()
        if self.value() == 'no':
            return queryset.filter(followings__isnull=True)
        return queryset


class HasFollowersFilter(admin.SimpleListFilter):
    title = gettext_lazy('Есть подписчики')
    parameter_name = 'has_followers'

    def lookups(self, request, model_admin):
        return (('yes', 'Да'), ('no', 'Нет'))

    def queryset(self, request, queryset):
        users_list = []
        if self.value() == 'yes':
            for user in queryset:
                if queryset.filter(followings=user).exists():
                    users_list.append(user)
            return queryset.filter(id__in=[user.id for user in users_list])
        if self.value() == 'no':
            for user in queryset:
                if queryset.filter(followings=user).exists():
                    users_list.append(user)
            return queryset.exclude(id__in=[user.id for user in users_list])
        return queryset
