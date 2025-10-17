
from django.urls import path

from . import views

urlpatterns = [
    path('todo', views.TodoListCreateAPIView.as_view(), name="todo"),
    path('todo/<int:pk>', views.TodoDetailView.as_view(), name='todo-detail'),
    
    
    path('tag', views.TagListCreateAPIView.as_view(), name="tag"),
    path('tag/<int:pk>', views.TagDetailView.as_view(), name='tag-detail'),
    
    path('applycurrenttemplate', views.SaveTemplate.as_view(), name="template"),
    path('template/<int:pk>', views.TemplateView.as_view(), name='template-detail'),
]