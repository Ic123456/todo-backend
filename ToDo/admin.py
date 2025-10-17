from django.contrib import admin
from .models import Tag, Todo, Template, TemplateTodo
# Register your models here.
admin.site.register([Tag, Todo, Template, TemplateTodo])