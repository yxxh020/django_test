from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import Post


# FBV(function based view 방식)
# def index(request):
#     posts = Post.objects.all().order_by('-pk')  # 모든 데이터를 다 가져오는 ORM 쿼리
#
#     return render(
#         request,
#         'blog/post_list.html',
#         {
#             'posts': posts,  # 딕셔너리
#         }
#     )
#
# def single_post_page(request, pk):
#     post = Post.objects.get(pk=pk)
#
#     return render(
#         request,
#         'blog/post_detail.html',
#         {
#             'post': post,
#         }
#     )

# CBV(class based view 방식)
class PostList(ListView):  # ListView: 여러 레코드를 목록 형태로 보여줄 때 사용
    model = Post
    # template_name = 'blog/post_list.html'
    ordering = '-pk'

    '''
    ListView 디폴트 속성
    1) context 변수: object_list 또는 모델명_list
    2) template: 모델명_list.html
        ex) post_list.html
    '''

class PostDetail(DetailView):
    model = Post
