from django.db import models


class Post(models.Model): #models모듈의 Model 클래스 사용
    title = models.CharField(max_length=30)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True) #처음 작성 시간 자동저장
    updated_at = models.DateTimeField(auto_now=True) # 수정시간 자동 저장
#     author:

    def __str__(self):
        return f'[{self.pk}] {self.title}'