import os.path

from django.contrib.auth.models import User
from django.db import models


class Post(models.Model):  # models 모듈의 Model 클래스 사용
    title = models.CharField(max_length=30)
    hook_text = models.CharField(max_length=100, blank=True)
    content = models.TextField()

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d/', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)  # 처음 작성 시간 자동 저장
    updated_at = models.DateTimeField(auto_now=True)  # 수정 시간 자동 저장

    '''
    DateTimeField 옵션
    auto_now: 모델 객체가 저장될 때마다 현재 시간으로 업데이트
    auto_now_add: 처음 생성될 때( 새로운 레코드가 DB에 추가될 때) 한번만 값을 할당
    auto_created: 공식 문서에도 설명 없음. 사용자가 create 시간 설정 가능
    '''

    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    '''
    on_delete=models.CASCADE: 사용자가 db에서 삭제될 때 작성한 post도 같이 삭제
    on_delete=models.SET_NULL: 사용자가 삭제될 때 author는 null값으로 변환
    '''

    def __str__(self):  # 제목에 object로 나와서 문자열로 변환 뒤 출력
        return f'[{self.pk}] {self.title}  :: {self.author} :: ' f'{self.updated_at}'[:-7]

    '''
    자주 쓰는 내장 함수
    __str__(): 해당 클래스로 만들어진 인스턴트(변수)를 문자열로 출력해주는 메소드
    __repr__(): represent. 해당 객체를 문자열로 설명
    __init__(): 객체를 만들 때 처음 실행되는 초기화 메소드. 생성자로 인식되어 객체가 생성되는 시점에 자동으로 호출 됨.
    
    '''

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'

    def get_file_name(self):  # 파일명 가져오기
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):  # 파일명에서 경로 제외하고 확장자만
        return self.get_file_name().split('.')[-1]