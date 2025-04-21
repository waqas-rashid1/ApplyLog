from django.shortcuts import render
from .forms import UserRegisterationForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login

def register(request):
    if request.method == 'POST':
        form = UserRegisterationForm(request.POST)
        if form.is_valid():
            user = form.save(commit = False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user)
            return redirect('homepage')      
    else:
        form = UserRegisterationForm()
    
    return render(request, 'registration/register.html', {'form': form})

def homepage(request):
    return render(request, 'basics/home.html')