import numpy

from django.contrib import admin


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'cooking_time'

    def separators(self, queryset):
        cooking_times = numpy.array(
            queryset.values_list('cooking_time', flat=True)
        )
        if not cooking_times.size:
            return 0, 0
        quick = int(numpy.floor(numpy.percentile(cooking_times, 33)))
        medium = int(numpy.floor(numpy.percentile(cooking_times, 66)))
        return quick, medium

    def filter_by_time_range(self, queryset, time_range):
        return queryset.filter(cooking_time__range=time_range)

    def lookups(self, request, model_admin):
        recipes = model_admin.get_queryset(request)
        quick, medium = self.separators(recipes)
        self.filter_range = {
            'quick': (0, quick),
            'medium': (quick + 1, medium),
            'slow': (medium + 1, 999999999)
        }

        return (
            ('quick', 'быстрее {0} минут ({1})'.format(
                quick,
                self.filter_by_time_range(
                    recipes,
                    self.filter_range['quick']
                ).count()
            )),
            ('medium', 'быстрее {0} минут ({1})'.format(
                medium,
                self.filter_by_time_range(
                    recipes,
                    self.filter_range.get('medium')
                ).count()
            )),
            ('slow', '{0} минут и дольше ({1})'.format(
                medium,
                self.filter_by_time_range(
                    recipes,
                    self.filter_range.get('slow')
                ).count()
            ))
        )

    def queryset(self, request, queryset):
        if self.value() in self.filter_range:
            return self.filter_by_time_range(
                queryset,
                self.filter_range.get(self.value())
            )
        return queryset


class HasValueFilter(admin.SimpleListFilter):
    LOOKUPS = (
        ('yes', 'Да'),
        ('no', 'Нет')
    )

    def lookups(self, request, model_admin):
        return self.LOOKUPS

    def queryset(self, request, queryset, field):
        if self.value() == 'yes':
            return queryset.filter(**{f'{field}__isnull': False}).distinct()
        if self.value() == 'no':
            return queryset.filter(**{f'{field}__isnull': True})
        return queryset


class HasRecipesFilter(HasValueFilter):
    title = 'Есть рецепты'
    parameter_name = 'has_recipes'

    def queryset(self, request, queryset):
        return super().queryset(request, queryset, 'recipes')


class HasSubscriptionsFilter(HasValueFilter):
    title = 'Есть подписки'
    parameter_name = 'has_subscriptions'

    def queryset(self, request, queryset):
        return super().queryset(request, queryset, 'followers')


class HasFollowersFilter(HasValueFilter):
    title = 'Есть подписчики'
    parameter_name = 'has_followers'

    def queryset(self, request, queryset):
        return super().queryset(request, queryset, 'authors')
