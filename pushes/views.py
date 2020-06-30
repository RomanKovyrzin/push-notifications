from django.shortcuts import render
from django.views import generic
from pushes.models import Push, Option
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from pushes.forms import LoginForm, CreatePushForm, SendPushForm
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime

from django.http import HttpResponse
from django.contrib.auth import authenticate, login

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

import redis
import os
from django.conf import settings


# connect to redis
# r = redis.Redis(host=settings.REDIS_HOST,
#                 port=settings.REDIS_PORT,
#                 db=settings.REDIS_DB)

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
r = redis.from_url(redis_url)

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username = cd['username'],
                                password = cd['password'],
                                remember_me = cd['remember_me'],)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated '\
                                        'successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})



# Create your views here.
@login_required
def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main
    num_pushes = 0
    if request.user.is_superuser:
        num_pushes = Push.objects.all().count()
    else:
        num_pushes = Push.objects.filter(sender=request.user).count()

    unsended = Push.objects.filter(sender=request.user, is_sent=False)
    
    num_options = Option.objects.all().count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    # Number of sended pushes
    redis_key = 'pushes:{0}'.format(request.user)
    r.setnx(redis_key, 0)
    total_count = int(r.get(redis_key))
    
    context = {
        'num_pushes': num_pushes,
        'unsended': unsended,
        'num_options': num_options,
        'num_visits': num_visits,
        'total_count': total_count,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


# Create class-based list view
class PushListView(LoginRequiredMixin, generic.ListView):
    model = Push
    paginate_by = 10
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Push.objects.all()
        else:
            return Push.objects.filter(sender=self.request.user)

class OptionListView(LoginRequiredMixin, generic.ListView):
    model = Option
    paginate_by = 10
    

# Create class-based detail view
class PushDetailView(LoginRequiredMixin, generic.DetailView):
    model = Push

class OptionDetailView(LoginRequiredMixin, generic.DetailView):
    model = Option


# Create Push Form view
def create_push(request):
    """View function for creating Push notification."""
    push_instance = Push()
    redis_key = 'pushes:{0}'.format(request.user)

    # If this is a POST request then process the Form data
    if request.method == 'POST' and 'send' in request.POST:

        # Create a form instance and populate it with data from the request (binding):
        form = CreatePushForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            push_instance.title = form.cleaned_data['title']
            push_instance.text = form.cleaned_data['text']
            push_instance.sender = request.user
            push_instance.send_date = datetime.datetime.now()
            push_instance.is_sent = True
            push_instance.save()

            total_count = r.incr(redis_key)

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('pushes') )

    elif request.method == 'POST' and 'save' in request.POST:

        # Create a form instance and populate it with data from the request (binding):
        form = CreatePushForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            push_instance.title = form.cleaned_data['title']
            push_instance.text = form.cleaned_data['text']
            push_instance.sender = request.user
            push_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('pushes') )
    
    # If this is a GET (or any other method) create the default form.
    else:
        form = CreatePushForm()

    context = {
        'form': form,
        'push_instance': push_instance,
    }

    return render(request, 'pushes/push_create_form.html', context)


# Send Push Form view
def send_push(request, pk):
    """View function for sending Push notification."""
    push_to_send = get_object_or_404(Push, pk=pk)
    redis_key = 'pushes:{0}'.format(request.user)

    # If this is a POST request then process the Form data
    if request.method == 'POST' and 'send' in request.POST:

        # Create a form instance and populate it with data from the request (binding):
        form = SendPushForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            push_to_send.title = form.cleaned_data['title']
            push_to_send.text = form.cleaned_data['text']
            push_to_send.send_date = datetime.datetime.now()
            push_to_send.is_sent = True
            push_to_send.save()
            total_count = r.incr(redis_key)

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('pushes') )

    elif request.method == 'POST' and 'update' in request.POST:

        # Create a form instance and populate it with data from the request (binding):
        form = SendPushForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            push_to_send.title = form.cleaned_data['title']
            push_to_send.text = form.cleaned_data['text']
            push_to_send.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('pushes') )
    
    # If this is a GET (or any other method) create the default form.
    else:
        form = SendPushForm(instance=push_to_send)
            

    context = {
        'form': form,
        'push_to_send': push_to_send,
    }

    return render(request, 'pushes/push_send_form.html', context)

# Delete Form + View
class PushDelete(DeleteView):
    model = Push
    success_url = reverse_lazy('pushes')
    # r.decr(redis_key)


# class PushUpdate(UpdateView):
#     model = Push
#     fields = ['title', 'text',]
#     template_name_suffix = '_update_form'

