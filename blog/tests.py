from django.contrib.auth.models import User
from django.test import TestCase, Client
from bs4 import BeautifulSoup

from blog.models import Post, Category, Tag


# Create your tests here.
class TestView(TestCase):
    # def test_post_list(self):
    #     self.assertEqual(2, 2)  # 입력값들이 같은지 검증
    def setUp(self):  # setUp함수: 초기 DB 상태를 정의/ 같은 클래스 안에 있는 다른 테스트 함수에 공통으로 적용
        self.client = Client()
        # 유저 생성
        self.user_tomato = User.objects.create_user(username='tomato', password='thvmxmspt1')
        self.user_orange = User.objects.create_user(username='orange', password='thvmxmspt1')
        self.user_orange.is_staff = True
        self.user_orange.save()

        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_music = Category.objects.create(name='music', slug='music')

        self.tag_python_kor = Tag.objects.create(name='python', slug='python')
        self.tag_hello = Tag.objects.create(name='hello', slug='hello')
        self.tag_weather = Tag.objects.create(name='weather', slug='weather')

        self.post_001 = Post.objects.create(
            title='첫 번째 포스트입니다.',
            content='Hello World. We are the world.',
            category=self.category_programming,
            author=self.user_tomato
        )
        self.post_001.tags.add(self.tag_hello)

        self.post_002 = Post.objects.create(
            title='두 번째 포스트입니다.',
            content='1등이 전부는 아니잖아요?',
            category=self.category_music,
            author=self.user_orange
        )

        self.post_003 = Post.objects.create(
            title='세 번째 포스트입니다.',
            content='category가 없을 수도 있지',
            author=self.user_orange
        )
        self.post_003.tags.add(self.tag_python_kor)
        self.post_003.tags.add(self.tag_weather)
    def test_update_post(self):
        update_post_url = f'/blog/update_post/{self.post_003.pk}/'

        # 로그인하지 않은 경우
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200)


        # 로그인 했지만 해당 작성자가 아닌경우
        self.assertNotEqual(self.post_003.author, self.user_tomato)
        self.client.login(
            username=self.user_tomato.username,
            password='thvmxmspt1'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 403)

        # 작성자가 접근하는 경우
        self.client.login(
            username=self.post_003.author.username,
            password='thvmxmspt1'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edit Post', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)
        self.assertIn('python; weather', tag_str_input.attrs['value'])

        response = self.client.post(
            update_post_url,
            {
                'title': '세 번째 포스트를 수정했습니다.',
                'content': '수정한 포스트 내용입니다~',
                'category': self.category_music.pk,
                'tags_str': '파이썬; 한글 태그, eng tag'
            },
            follow=True  # post요청 후 서버에서 페이지가 redirect됬을때 따라가도록
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('세 번째 포스트를 수정했습니다.', main_area.text)
        self.assertIn('수정한 포스트 내용입니다~', main_area.text)
        self.assertIn(self.category_music.name, main_area.text)
        self.assertIn('파이썬', main_area.text)
        self.assertIn('한글 태그', main_area.text)
        self.assertIn('eng tag', main_area.text)
        self.assertNotIn('python', main_area.text)

    def test_create_post(self):
        # 로그인하지 않으면 status code가 200되면 안됨.
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # staff가 아닌 일반 사용자가 로그인한 경우( 글 못올림)
        self.client.login(username='tomato', password='thvmxmspt1')
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # staff가 로그인
        self.client.login(username='orange', password='thvmxmspt1')
        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Create Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Create New Post', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)

        self.client.post(
            '/blog/create_post/',
            {
                'title': 'Post Form 만들기',
                'content': 'Post Form 페이지를 만들자.',
                'tags_str': 'new tag; 한글 태그, python'
            }
        )
        self.assertEqual(Post.objects.count(), 4)
        last_post = Post.objects.last()
        self.assertEqual(last_post.title, "Post Form 만들기")
        self.assertEqual(last_post.author.username, "orange")

        self.assertEqual(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name='new tag'))
        self.assertTrue(Tag.objects.get(name='한글 태그'))
        self.assertEqual(Tag.objects.count(), 5)

    def test_tag_page(self):
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.tag_hello.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_hello.name, main_area.text)

        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_category_page(self):
        response = self.client.get(self.category_programming.get_absolute_url()) #get_absolute_url로 고유 url만들기
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.category_programming.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_programming.name, soup.h1.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')  #id가 categories-card인 div 요소 찾아서
        self.assertIn('Categories', categories_card.text)  # 그 안에 Categories라는 문구가 있는지 확인
        # 모든 카테고리가 제대로 출력 되어 있는지 확인
        self.assertIn(f'{self.category_programming.name} ({self.category_programming.post_set.count()})', categories_card.text)
        self.assertIn(f'{self.category_music.name} ({self.category_music.post_set.count()})', categories_card.text)
        self.assertIn(f'미분류 (1)', categories_card.text)  #카테고리가 없는 포스트

    def test_post_list(self):
        # post가 있는 경우
        self.assertEqual(Post.objects.count(), 3)

        # 1.1 포스트 목록 페이지를 가져온다.
        response = self.client.get('/blog/')

        # 1.2 정상적으로 페이지가 로드된다.
        self.assertEqual(response.status_code, 200)

        # 1.3 페이지 긁어오기
        soup = BeautifulSoup(response.content, 'html.parser')
        # self.assertEqual(soup.title.text, 'Blog')
        # 1.4 내비게이션 바, 카테고리 카드가 있다.
        self.navbar_test(soup)
        self.category_card_test(soup)

        # 메인 area가 있다.
        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text) # 뱃지로 카테고리 표현
        # tag 출력 확인
        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_001_card.text)
        self.assertNotIn(self.tag_weather.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_002_card.text)
        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_weather.name, post_002_card.text)


        post_003_card = main_area.find('div', id='post-3')
        self.assertIn('미분류', post_003_card.text)
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn(self.tag_weather.name, post_003_card.text)
        self.assertIn(self.tag_python_kor.name, post_003_card.text)
        self.assertNotIn(self.tag_hello.name, post_003_card.text)

        self.assertIn(self.user_tomato.username.upper(), main_area.text)
        self.assertIn(self.user_orange.username.upper(), main_area.text)

        # 포스트가 없는 경우
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        # 포스트 목록 페이지를 새고로침했을 때 포스트가 없는걸 확인
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)

    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        # href 링크 연결 테스트
        logo_btn = navbar.find('a', text='Do It Django')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text='About Me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')


    # def test_post_list(self):
    #     # 1.1 포스트 목록 페이지를 가져온다.
    #     response = self.client.get('/blog/')
    #
    #     # 1.2 정상적으로 페이지가 로드된다.
    #     self.assertEqual(response.status_code, 200)
    #
    #     # 1.3 페이지 타이틀은 'Blog'이다.
    #     soup = BeautifulSoup(response.content, 'html.parser')
    #     self.assertEqual(soup.title.text, 'Blog')
    #     # 1.4 내비게이션 바가 있다.
    #     self.navbar_test(soup)
    #
    #     # 2.1 메인 영역에 게시물이 하나도 없다면
    #     self.assertEqual(Post.objects.count(), 0)
    #     # 2.2 '아직 게시물이 없습니다'라는 문구가 보인다.
    #     main_area = soup.find('div', id='main-area')
    #     self.assertIn('아직 게시물이 없습니다', main_area.text)
    #
    #     # 3.1 게시물이 2개 있다면
    #
    #     self.assertEqual(Post.objects.count(), 2)
    #
    #     # 3.2 포스트 목록 페이지를 새고로침했을 때
    #     response = self.client.get('/blog/')
    #     soup = BeautifulSoup(response.content, 'html.parser')
    #     self.assertEqual(response.status_code, 200)
    #     # 3.3 메인 영역에 포스트 2개의 타이틀이 존재한다.
    #     main_area = soup.find('div', id='main-area')
    #     self.assertIn(post_001.title, main_area.text)
    #     self.assertIn(post_002.title, main_area.text)
    #     # 3.4 '아직 게시물이 없습니다'라는 문구는 더 이상 보이지 않는다.
    #     self.assertNotIn('아직 게시물이 없습니다', main_area.text)
    #
    #     self.assertIn(self.user_tomato.username.upper(), main_area.text)
    #     self.assertIn(self.user_orange.username.upper(), main_area.text)

    def test_post_detail(self):
        # 1.1 포스트가 하나 있다.
        # post_001 = Post.objects.create(
        #     title='첫 번째 포스트입니다.',
        #     content='Hello World. We are the world.',
        #     author=self.user_tomato,
        # )
        # 1.2 그 포스트이 url은 /'blog/1/' 이다.
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')

        # 2. 첫 번째 포스트의 상세 페이지 테스트
        # 2.1 첫 번째 포스트의 url로 접근하면 정상적으로 작동한다(status code: 200).
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 2.2 포스트 목록 페이지와 똑같은 내비게이션 바, 카테고리 카드가 있다.
        self.navbar_test(soup)
        self.category_card_test(soup)

        # 2.3. 첫 번째 포스트의 제목이 웹 브라우저 탭 타이틀에 있다
        self.assertIn(self.post_001.title, soup.title.text)

        # 2.4. 첫 번쨰 포스트의 제목이 포스트 영역에 있다
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.category_programming.name, post_area.text)


        # 2.5. 첫 번째 포스트의 작성자(author)가 포스트 영역에 있다(아직 구현 no)
        self.assertIn(self.user_tomato.username.upper(), post_area.text)

        # 2.6. 첫 번째 포스트의 내용(content)이 포스트 영역에 있다
        self.assertIn(self.post_001.content, post_area.text)

        self.assertIn(self.tag_hello.name, post_area.text)
        self.assertNotIn(self.tag_python_kor.name, post_area.text)
        self.assertNotIn(self.tag_weather.name, post_area.text)
