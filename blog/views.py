from django.shortcuts import render
from .models import Post


# Create your views here.
def index(request):
    posts = Post.objects.all().order_by('-pk')  # 모든 데이터를 다 가져오는 ORM 쿼리

    return render(
        request,
        'blog/index.html',
        {
            'posts': posts,
        }
    )
