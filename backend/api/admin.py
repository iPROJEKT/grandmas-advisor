from django.contrib import admin
from .models import Tag, Recipe, IngredientRecipe, Ingredients, FavoriteRecipe, ShoppingCart

admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(IngredientRecipe)
admin.site.register(Ingredients)
admin.site.register(FavoriteRecipe)
admin.site.register(ShoppingCart)