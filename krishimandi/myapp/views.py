from django.contrib.auth import authenticate
from django.contrib import auth
from django.shortcuts import redirect
from django.views.generic import CreateView
from django.shortcuts import render
from .forms import FarmerSignUpForm,DealerSignUpForm,UserUpdateForm,ProfileUpdateForm
from .models import User
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import Profile,User



def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST,instance = request.user)
        p_form = ProfileUpdateForm(request.POST,request.FILES,instance = request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request,f'Your account has been updated!')
            return redirect(reverse('profile'))
    else:
        u_form = UserUpdateForm(instance = request.user)
        p_form = ProfileUpdateForm(instance = request.user.profile)
    context = {
    'u_form':u_form,
    'p_form':p_form
    }
    return render(request,'myapp/profile.html',context)

def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_farmer or user.is_dealer:
                    auth.login(request, user)
                    messages.info(request, f"You are now logged in as {username}")
                    return redirect('/')
                else:
                    messages.error(request, "Invalid username or password.")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request = request,
                    template_name = "myapp/login.html",
                    context={"form":form})


def SignUpView(request):
   return render(request, "registration/signup.html")

def contactus(request):
    return render(request, 'contactus.html')
def aboutus(request):
    return render(request, 'aboutus.html')

def FarmerSignUpView(request):
    if request.method == 'POST':
        form = FarmerSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            u1=User.objects.get(username=username)
            # profile.usern=u1
            # Profile.objects.create(usern=u1)
            p1=Profile(usern=u1)
            p1.save()

            messages.success(request,f'Account Created for {username}!')
            return redirect(reverse('login'))
    else:
        form = FarmerSignUpForm()
    return render(request,'registration/signup_form.html',{'form':form})


def DealerSignUpView(request):
    if request.method == 'POST':
        form = DealerSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            u1=User.objects.get(username=username)
            # profile.usern=u1
            # Profile.objects.create(usern=u1)
            p1=Profile(usern=u1)
            p1.save()
            messages.success(request,f'Account Created for {username}!')
            return redirect(reverse('login'))
    else:
        form = DealerSignUpForm()
    return render(request,'registration/signup_form.html',{'form':form})


# class FarmerSignUpView(CreateView):
#     model = User
#     form_class = FarmerSignUpForm
#     template_name = 'registration/signup_form.html'

#     def get_context_data(self, **kwargs):
#         kwargs['user_type'] = 'farmer'
#         return super().get_context_data(**kwargs)

#     def form_valid(self, form):
#         user = form.save()
#         # login(self.request, user)
#         return redirect(reverse('login'))

# class DealerSignUpView(CreateView):
#     model = User
#     form_class = DealerSignUpForm
#     template_name = 'registration/signup_form.html'

#     def get_context_data(self, **kwargs):
#         kwargs['user_type'] = 'dealer'
#         return super().get_context_data(**kwargs)

#     def form_valid(self, form):
#         user = form.save()
#         # login(self.request, user)
#         return redirect(reverse('login'))

def index(request):
    return render(request, 'myapp/index.html', )

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from .decorators import dealer_required
# from .models import Quiz

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .decorators import farmer_required

# def ProfileView()
#
# @method_decorator([login_required, student_required], name='dispatch')
# class StudentInterestsView(UpdateView):
#     model = Student
#     form_class = StudentInterestsForm
#     template_name = 'classroom/students/interests_form.html'
#     success_url = reverse_lazy('students:quiz_list')
#
#     def get_object(self):
#         return self.request.user.student
#
#     def form_valid(self, form):
#         messages.success(self.request, 'Interests updated with success!')
#         return super().form_valid(form)


