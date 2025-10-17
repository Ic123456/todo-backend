from django.db import models
from django.conf import settings  # ✅ for custom User model



class Template(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="templates")
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Tag(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tags")
    name = models.CharField(max_length=20)
    color = models.CharField(max_length=7, default="#000000")  # includes '#' + 6 hex digits

    def __str__(self):
        return self.name


class TemplateTodo(models.Model):
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name="template_todos")
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="template_todos")
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Todo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="todos")
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="todos")
    completed = models.BooleanField(default=False)
    week = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.user.email})"
