from django.shortcuts import render


# Create your views here.
def landing(request):  # 대문
    return render(
        request,
        'single_pages/landing.html'
    )


def about_me(request):  # 자기소개
    return render(
        request,
        'single_pages/about_me.html'
    )
