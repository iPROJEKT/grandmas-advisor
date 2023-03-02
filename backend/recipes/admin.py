from django.contrib import admin

from .models import (
    Tag, Ingredients,
    IngredientRecipe, Recipe,
    ShoppingCart, FavoriteRecipe
)


admin.site.register(Tag)
admin.site.register(Ingredients)
admin.site.register(IngredientRecipe)
admin.site.register(Recipe)
admin.site.register(ShoppingCart)
admin.site.register(FavoriteRecipe)
