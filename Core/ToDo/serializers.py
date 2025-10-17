from rest_framework import serializers
from .models import Tag, Todo, Template, TemplateTodo


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color']


    
class TodoSerializer(serializers.ModelSerializer):
    time = serializers.TimeField(required=False, allow_null=True, format="%H:%M", input_formats=["%H:%M", "%H:%M:%S"])
    class Meta:
        model = Todo
        fields = ['id', 'title', 'description', 'date', 'time', 'tags', 'completed', 'week']

    
class DetailedTodoSerializers(serializers.ModelSerializer):
    time = serializers.TimeField(required=False, allow_null=True, format="%H:%M", input_formats=["%H:%M", "%H:%M:%S"])
    class Meta:
        model = Todo
        fields = ['id', 'title', 'description', 'time', 'tags', 'completed']

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        instance = super().update(instance, validated_data)

        if tags is not None:
            # Replace existing tags — even with []
            instance.tags.set(tags)

        return instance


class TemplateTodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateTodo
        fields = ['id', 'title', 'description', 'time', 'tags', 'completed']


class TemplateSerializer(serializers.ModelSerializer):
    template_todos = TemplateTodoSerializer(many=True, read_only=True)

    class Meta:
        model = Template
        fields = ['id', 'name', 'template_todos']