from django.shortcuts import render,get_object_or_404,redirect
from django.contrib import messages

# Create your views here.
def home(request):
    return render(request,'myapp/home.html')

def about(request):
    return render(request,'myapp/about.html')