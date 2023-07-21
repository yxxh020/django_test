from django.urls import path
from . import views


urlpatterns = [
    # FBV(function based view)
    # path('', views.index),
    # path('<int:pk>/', views.single_post_page),

    # CBV(class based view)
    path('', views.PostList.as_view()),
    path('<int:pk>/', views.PostDetail.as_view()),
]