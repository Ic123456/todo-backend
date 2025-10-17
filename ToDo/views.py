
from .models import Tag, Todo, Template, TemplateTodo
from .serializers import TagSerializer, TodoSerializer, DetailedTodoSerializers, TemplateSerializer
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone

class TodoListCreateAPIView(generics.ListCreateAPIView):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    
    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
class TodoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Todo.objects.all()
    serializer_class = DetailedTodoSerializers
    lookup_field = 'pk'
    

    
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        serializer = self.get_serializer(
            self.get_object(),
            data=request.data,
            partial=True
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def get_queryset(self):
        # Only allow access to the logged-in user's notes
        return Todo.objects.filter(user=self.request.user)
    
class TagListCreateAPIView(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    
    
class TagDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'pk'
    
    def get_queryset(self):
        # Only allow access to the logged-in user's notes
        return Tag.objects.filter(user=self.request.user)
    
class SaveTemplate(APIView):


    def get(self, request):
        # user = request.user filter(user=user)
        templates = Template.objects.filter(user=self.request.user)
        serializer = TemplateSerializer(templates, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        name = request.data.get('name')
        today = request.data.get('date')
        user = request.user
        # user = request.user
        
            # Create template user=user, 
        template = Template.objects.create(name=name, user=user)

        # Get today's todos
        todos = Todo.objects.filter( date=today, completed=False, user=user)

        # Copy todos into TemplateTodo
        for todo in todos:
            temp_todo = TemplateTodo.objects.create(
                template=template,
                title=todo.title,
                description=todo.description,
                time=todo.time,
                completed=todo.completed,
            )
            temp_todo.tags.set(todo.tags.all())  # Copy tags

        return Response({
    "message": "Template created successfully!",
    "id": template.id,
    "name": template.name,
})

        
    
class TemplateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    lookup_field = 'pk'
    
    def get_queryset(self):
        # Only allow access to the logged-in user's notes
        return Template.objects.filter(user=self.request.user)