from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import Post, Category, Tag


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
def category_page(request, slug):  # FBV방식은 request 꼭
    # category = Category.objects.get(slug=slug) # 함수의 인자로 받은 slug와 동일한 slug를 가진 카테고리 불러옴

    if slug == 'no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)

    return render(
        request,
        'blog/post_list.html',
        {  # PostList 클래스에서 context로 정의한 부분을 딕셔너리 형태로 직접 정의
            'post_list': post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'category': category,  # 페이지 타이틀 옆
        }
    )


def tag_page(request, slug):  # FBV방식은 request 꼭
    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()

    return render(
        request,
        'blog/post_list.html',
        {  # PostList 클래스에서 context로 정의한 부분을 딕셔너리 형태로 직접 정의
            'post_list': post_list,
            'tag': tag,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
        }
    )


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

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data()  # super(): 부모클래스의 메소드 사용할 수 있게
        context['categories'] = Category.objects.all()  # 모든 카테고리를 가져와 'categories' 키에 연결
        context['no_category_post_count'] = Post.objects.filter(category=None).count()  # 미분류 포스트 카운트
        return context
