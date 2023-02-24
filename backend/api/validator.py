from django.core.exceptions import ValidationError


def min_valid_valuse(value):
    if value < 1:
        raise ValidationError(
            'Время приготовление не может быть меньше 1 минуты'
        )


def weight_valid(value):
    if value < 1:
        raise ValidationError(
            'Вес должен быть больше грамма'
        )
