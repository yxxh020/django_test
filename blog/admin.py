from django.contrib import admin
from .models import Post, Category


admin.site.register(Post)

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}  # Category 모델 name 필드 값이 입력됬을 때 자동 slug

admin.site.register(Category, CategoryAdmin)