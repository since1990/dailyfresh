from django.shortcuts import render


# Create your views here.
def register(request):
    '''注册页面'''
    return render(request, 'register.html')