from django.urls import path
from . import views


urlpatterns = [
    # FBV(function based view)
    # path('', views.index),
    # path('<int:pk>/', views.single_post_page),

    path('tag/<str:slug>/', views.tag_page),
    path('category/<str:slug>/', views.category_page),
    # CBV(class based view)
    path('', views.PostList.as_view()),
    path('<int:pk>/', views.PostDetail.as_view()),
    path('create_post/', views.PostCreate.as_view()),
]