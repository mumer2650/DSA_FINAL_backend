from django.contrib import admin
from .models import Property

# Register your models here.

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'is_featured')
    list_editable = ('is_featured',)  # Allows checking the box without opening the detail page
    list_filter = ('is_featured',)    # Allows filtering the table to see only featured props