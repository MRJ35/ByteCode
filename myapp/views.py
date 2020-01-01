from django.shortcuts import render, redirect
from django.http import HttpResponse
# Create your views here.
from .models import Tutorial, TutorialCategory, TutorialSeries
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from .forms import new_user_form


def single_slug(request, single_slug):
   categories = [c.category_slug for c in TutorialCategory.objects.all()]
   if single_slug in categories:
      matching_series = TutorialSeries.objects.filter(tutorial_category__category_slug=single_slug)
      series_urls = {}
      for m in matching_series.all():
         part_one = Tutorial.objects.filter(tutorial_series__tutorial_series=m.tutorial_series).earliest("published_date")
         series_urls[m] = part_one.tutorial_slug
      return render(request,"main/category.html",{"part_ones" : series_urls})
   
   tutorials = [c.tutorial_slug for c in Tutorial.objects.all()]
   if single_slug in tutorials:
      this_tutorial = Tutorial.objects.get(tutorial_slug=single_slug)
      tutorial_from_series = Tutorial.objects.filter(tutorial_series__tutorial_series=this_tutorial.tutorial_series).order_by("published_date")
      this_tutorial_index = list(tutorial_from_series).index(this_tutorial)
      return render(request,
                     "main/tutorial.html",
                     {"tutorial" : this_tutorial,
                      "sidebar" : tutorial_from_series,
                      "this_tutorial_index" : this_tutorial_index})
      # return HttpResponse(f"{single_slug} is a tutorial!!")

   return HttpResponse(f"{single_slug} does not correspond to any page!!")


def homepage(request):
   return render(request = request,
                 template_name = "main/categories.html",
                 context = {"categories": TutorialCategory.objects.all}) 

def register(request):
   if request.method == "POST":
      form = new_user_form(request.POST)
      if form.is_valid():
         user = form.save()
         username = form.cleaned_data.get('username')
         messages.success(request,f"{username} Registered Successfully")
         login(request,user)
         messages.info(request,f"You are now logged in as {username}")
         return redirect("myapp:homepage")
      else:
         for msg in form.error_messages:
            messages.error(request,f"{msg}: {form.error_messages[msg]}")   

   form = new_user_form
   return render(request,
                  "main/register.html",
                  context={"form":form})     

def logout_request(request):
   logout(request)
   messages.info(request,"Logged out Successfully!")
   return redirect("myapp:homepage")                    

def login_request(request):
   if request.method == "POST":
      form = AuthenticationForm(request,data =request.POST)
      if form.is_valid():
         username = form.cleaned_data.get('username')
         password = form.cleaned_data.get('password')
         user = authenticate(username=username,password=password)
         if user is not None:
            login(request,user)
            messages.info(request,f"You are now logged in as {username}")
            return redirect("myapp:homepage")
         else:
            for msg in form.error_messages:
               messages.error(request,"Invalid username or password")
      else:
         messages.error(request,"Invalid username or password")
   form = AuthenticationForm()
   return render(request,"main/login.html",{"form":form})
