from django.urls import path
from . import views


urlpatterns = [
    # path('', views.index),  # FBV(function based view)
    path('', views.PostList.as_view()),  # CBV(class based view)
    path('<int:pk>/', views.single_post_page),
]