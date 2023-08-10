from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import Post, Category


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
    model = Post  # 선언하면 자동으로 post_list = Post.objects.all() 명령함
    # template_name = 'blog/post_list.html'
    ordering = '-pk'

    '''
    ListView 디폴트 속성
    1) context 변수: object_list 또는 모델명_list
    2) template: 모델명_list.html
        ex) post_list.html
    '''

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data()  # super(): 부모클래스의 메소드 사용할 수 있게
        context['categories'] = Category.objects.all()  # 모든 카테고리를 가져와 'categories' 키에 연결
        context['no_category_post_count'] = Post.objects.filter(category=None).count()  # 미분류 포스트 카운트
        return context

class PostDetail(DetailView):
    model = Post

