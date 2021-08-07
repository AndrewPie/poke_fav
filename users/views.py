from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from users.forms import LoginForm, SignupForm


class SignUp(View):
    
    def get(self, request):
        form=SignupForm()
        return render(request,'users/signup.html',{'form':form})
    def post(self,request):
        form=SignupForm(request.POST)
        if form.is_valid():
            # user.is_active=True
            user=form.save()
            return redirect('users:login')
        else:
            return render(request,'users/signup.html',{'form':form})


class Login(View):
    def get(self,request):
        form=LoginForm()
        return render(request,'users/login.html',{'form':form})
    def post(self,request):
        redirect_url=request.GET.get('next', 'main')
        form=LoginForm(request.POST)
        print(form.is_valid())
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'],password=form.cleaned_data['password'])
            if user is not None:
                    login(request,user)
                    if redirect_url:
                        return redirect('main')
                    else:
                        return redirect('/')

            else:
                return HttpResponse('There is no such user')
        return HttpResponse('Error while loggin')
    
    
class Logout(View):
    def get(self,request):
        logout(request)
        return redirect('users:login')