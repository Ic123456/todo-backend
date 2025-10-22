from django.contrib import admin
from .models import Tag, Todo, Template, TemplateTodo
# Register your models here.


class TodoAdmin(admin.ModelAdmin):
    list_filter = ('user','tags', 'date')
    search_fields = ('title',)
    readonly_fields = ('user', 'tags')
    list_display = ("title", "user_email", "date", "display_tags")

    def display_tags(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())
    display_tags.short_description = "Tags"
    def user_email(self, obj):
        return obj.user.email
    fields = ('user', 'title', 'description', 'date', 'time', 'completed', 'tags')


class TagAdmin(admin.ModelAdmin):
    list_filter = ('user',)
    readonly_fields = ('user',)
    fields = ("user", "name", "color")
    list_display = ("name", "user_email")
    
    def user_email(self, obj):
        return obj.user.email
    
class TemplateAdmin(admin.ModelAdmin):
    list_filter = ('user',)
    readonly_fields = ('user',)
    list_display = ("name", "user_email")
    
    fields = ("user", "name")
    
    def user_email(self, obj):
        return obj.user.email
    
class TemplateTodoAdmin(admin.ModelAdmin):
    list_filter = ('template',)
    readonly_fields = ('template', "tags")
    list_display = ("title", "template")
    
    fields = ('template', 'title', 'description','time', 'completed', 'tags')

    
admin.site.register(Todo, TodoAdmin)
admin.site.register(Tag, TagAdmin)

admin.site.register(Template, TemplateAdmin)
admin.site.register(TemplateTodo, TemplateTodoAdmin)