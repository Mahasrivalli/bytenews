

from django.shortcuts import render, redirect
from users.Registration.registration import Registration

from django.contrib import messages
def home(request):
    return render(request, 'users/home.html')

def register(request):
    if request.method == 'POST':
        form = Registration(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully!')
            return redirect('login')
    else:
        form = Registration()
    return render(request, 'users/register.html', {'form': form})
