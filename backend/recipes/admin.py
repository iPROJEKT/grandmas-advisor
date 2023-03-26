from django.contrib import admin

from .models import (
    Tag, Ingredients,
    IngredientRecipe, Recipe,
    ShoppingCart, FavoriteRecipe
)

class IngredientRecipeInline(admin.StackedInline):
    model = IngredientRecipe
    search_fields = ['recipe', 'ingredient']

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientRecipeInline]


admin.site.register(Tag)
admin.site.register(Ingredients)
admin.site.register(ShoppingCart)
admin.site.register(FavoriteRecipe)
