from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.utils.text import slugify
from django.views.generic import ListView, DetailView, CreateView, UpdateView

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

class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView): # Mixin 사용하면 다른 클래스의 메서드 추가 가능
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    def test_func(self): # 작성 페이지에 접근 가능한 사용자를 superuser(최고 관리자) or staff로 제한
        return self.request.user.is_superuser or self.request.user.is_staff

    # CreateView 기본함수 form_valid를 사용해서 author field 자동으로 채우기
    def form_valid(self, form): # 방문자가 form에 담아 보낸 정보를 포스트로 만들어서 고유 경로로 redirect
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            form.instance.author = current_user
            response = super(PostCreate, self).form_valid(form)

            '''
            form_valid() 함수: 폼에 들어온 값으로 모델에 해당하는 인스턴스를 만들어 DB에 저장하고 그 인스턴스 경로로 리다이렉트 해줌.
                Post와 Tag모델은 다대다(M:N)관계이므로 태그를 추가하려면 미리 포스트가 db에 있어야함.
            '''

            tags_str = self.request.POST.get('tags_str')  # post방식으로 전달된거 받기
            if tags_str:
                tags_str = tags_str.strip()  # 앞뒤 공백 제거

                tags_str = tags_str.replace(',', ';')  # 쉼표를 세미콜론으로 구분자로 처리되게 변경
                tags_list = tags_str.split(';')

                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t) # get_or_create(): Tag 모델 인스턴스, 새로 생성됬는지 bool값 리턴
                    if is_tag_created:  # 태그를 새로 생성한다면 slug값도 같이 생성
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)  # 새로만든 포스트의 tags 필드에 추가

            return response  # 작업 완료 후 새로 만든 포스트 페이지로 이동
        else:
            return redirect('/blog/')

class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category', 'tags']

    template_name = 'blog/post_update_form.html'  # default template name은 모델명(post)_form.html인데 PostCreate 메서드랑 겹쳐서 직접 지정
    '''
    dispatch(): get방식 요청 인지 post방식 요청인지 판단
        get방식인 경우: 폼 페이지 보여줌
        post방식인 경우: 받은 폼이 유효한지 확인후 db에 내용 저장
    '''
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author: # 유저 아이디가 author필드와 동일한 경우
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied # 권한 없음 403

