from django.contrib import admin

from .models import (
    Tag, Ingredients,
    IngredientRecipe, Recipe,
    ShoppingCart, FavoriteRecipe
)

class IngredientRecipeInline(admin.StackedInline):
    model = IngredientRecipe
    search_fields = ['recipe', 'ingredient']
    extra = 3
    min_num = 1

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientRecipeInline]


admin.site.register(Tag)
admin.site.register(Ingredients)
admin.site.register(ShoppingCart)
admin.site.register(FavoriteRecipe)
