import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from .forms import RegisterForm, ProfileUpdateForm
from django.contrib.auth.models import User
from .forms import ProfileForm
from articles.models import Profile, Comment


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            profile = Profile(user=user)
            profile.save()
            login(request, user)
            return redirect('article_list')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required(login_url='/login/')
def profile(request):
    user = request.user
    profile = Profile.objects.get(user_id=user.id)
    comments = Comment.objects.filter(author_id=user.id)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'registration/profile.html', {'form': form, 'profile':profile, 'comments':comments})


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    # fields = ['bio', 'profile_picture']
    template_name = 'profile_edit'
    success_url = reverse_lazy('profile')
    form_class = ProfileUpdateForm

    def get_object(self):
        return self.request.user.profile

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        user.first_name = form.cleaned_data.get('first_name')
        user.last_name = form.cleaned_data.get('last_name')
        user.save()

        profile = self.object
        profile.user = user
        profile.bio = form.cleaned_data.get('bio')
        profile.profile_picture = self.request.FILES.get('profile_picture')
        profile.save()

        return response

