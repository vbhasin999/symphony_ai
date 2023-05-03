from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.utils import timezone

from socialnetwork.forms import LoginForm, RegisterForm, ProfileForm
from socialnetwork.models import Post, Profile, Comment

from django.http import HttpResponse, Http404

import json

def redirect_to_sn(request):
    return redirect(reverse('global'))

def login_action(request):
    context = {}

    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'socialnetwork/login.html', context)
    
    form = LoginForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return render(request, 'socialnetwork/login.html', context)
    
    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])
    
    login(request, new_user)
    return redirect(reverse('global'))

@login_required
def logout_action(request):
    logout(request)
    return redirect(reverse('login'))

def register_action(request):
    context = {}
    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'socialnetwork/register.html', context)

    form = RegisterForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return render(request, 'socialnetwork/register.html', context)
    
    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    
    new_user.save()

    new_profile = Profile(bio='', user=new_user)
    new_profile.save()

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])
    
    login(request, new_user)

    return redirect(reverse('global'))

@login_required
def global_action(request):
    timezone.activate('US/Eastern')
    if request.method =='GET':
        return render(request, 'socialnetwork/global.html', {'posts': Post.objects.all().order_by('-creation_time')})
    
    if 'text' not in request.POST or not request.POST['text']:
        return render(request, 'socialnetwork/global.html', {'posts': Post.objects.all().order_by('-creation_time')})
    
    new_post = Post(text=request.POST['text'], user=request.user, creation_time=timezone.now())
    print(timezone.now())
   
    new_post.save()


    return render(request, 'socialnetwork/global.html', {'posts': Post.objects.all().order_by('-creation_time')})


def follower_stream_action(request):
    context = {}

    return render(request, 'socialnetwork/follower.html', {'posts': Post.objects.all().order_by('-creation_time')})

@login_required
def user_profile_action(request):
    profile = request.user.profile

    if request.method == 'GET':
        context = {'profile' : request.user.profile, 'form':ProfileForm(initial={'bio':request.user.profile.bio})}
        return render(request, 'socialnetwork/user_profile.html', context)
    
    form = ProfileForm(request.POST, request.FILES)

    if not form.is_valid():
        context = {'profile': request.user.profile, 'form':form}
        return render(request, 'socialnetwork/user_profile.html', context)

    profile.picture = form.cleaned_data['picture']
    profile.content_type = form.cleaned_data['picture'].content_type
    profile.bio = form.cleaned_data['bio']
    profile.save()

    context = {'profile': request.user.profile, 'form':ProfileForm(initial={'bio':request.user.profile.bio})}
    return render(request, 'socialnetwork/user_profile.html', context)

def get_photo(request, id):
    item = get_object_or_404(Profile, id=id)
    # Maybe we don't need this check as form validation requires a picture be uploaded.
    # But someone could have delete the picture leaving the DB with a bad references.
    if not item.picture:
        raise Http404

    return HttpResponse(item.picture, content_type=item.content_type)

def other_profile_action(request, id):
    profile = get_object_or_404(Profile, id=id)
  
    return render(request, 'socialnetwork/other_profile.html', {'profile': profile})

def follow(request, id):
    print(f'id: {id}')
    user_to_follow = get_object_or_404(User, id=id)
    request.user.profile.following.add(user_to_follow)
    request.user.profile.save()
    return render(request, 'socialnetwork/other_profile.html', {'profile': user_to_follow.profile})

def unfollow(request, id):
 
    user_to_unfollow = get_object_or_404(User, id=id)
    request.user.profile.following.remove(user_to_unfollow)
    request.user.profile.save()
    return render(request, 'socialnetwork/other_profile.html', {'profile': user_to_unfollow.profile})


def get_global_action(request):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)
    # To make quiz11 easier, we permit reading the list without logging in. :-)
    # if not request.user.is_authenticated:
    #     return _my_json_error_response("You must be logged in to do this operation", status=403)

    response_posts      = []
    response_comments   = []
    for model_item in Post.objects.all():
        my_item = {
            'id': model_item.id,
            'text': model_item.text,
            'user': model_item.user.username,
            'user_full_name' : model_item.user.get_full_name(),
            'user_id':model_item.user.id,
            'signed_in_user': request.user.username,
            'signed_in_user_id': request.user.id,
            'creation_time': str(model_item.creation_time.strftime("%m/%d/%Y %-I:%M %p"))
        }
        response_posts.append(my_item)

    for model_item in Comment.objects.all():
        my_item = {
            'id': model_item.id,
            'post_id': model_item.post.id,
            'text': model_item.text,
            'creator_username': model_item.creator.username,
            'creator_fullname': model_item.creator.get_full_name(),
            'creator_user_id': model_item.creator.id,
            'signed_in_user': request.user.username,
            'signed_in_user_id': request.user.id,
            'creation_time': str(model_item.creation_time.strftime("%m/%d/%Y %-I:%M %p"))
        }

        response_comments.append(my_item)


    response_data = {'posts':response_posts, 'comments':response_comments}
    response_json = json.dumps(response_data)

    return HttpResponse(response_json, content_type='application/json')

def get_follower_action(request):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)
    # To make quiz11 easier, we permit reading the list without logging in. :-)
    # if not request.user.is_authenticated:
    #     return _my_json_error_response("You must be logged in to do this operation", status=403)

    response_posts      = []
    response_posts_id   = []
    response_comments   = []
    for model_item in Post.objects.all():
        show = False
        if model_item.user in request.user.profile.following.all():
            show = True

        if model_item.user.username == request.user.username:
            show = False
        
        if not show:
            continue

        my_item = {
            'id': model_item.id,
            'text': model_item.text,
            'user': model_item.user.username,
            'user_full_name' : model_item.user.get_full_name(),
            'user_id':model_item.user.id,
            'signed_in_user': request.user.username,
            'signed_in_user_id': request.user.id,
            'creation_time': str(model_item.creation_time.strftime("%m/%d/%Y %-I:%M %p"))
        }
        response_posts.append(my_item)
        response_posts_id.append(model_item.id)

    for model_item in Comment.objects.all():
        post_id = model_item.post.id

        if post_id not in response_posts_id:
            continue
        
        my_item = {
            'id': model_item.id,
            'post_id': model_item.post.id,
            'text': model_item.text,
            'creator_username': model_item.creator.username,
            'creator_fullname': model_item.creator.get_full_name(),
            'creator_user_id': model_item.creator.id,
            'signed_in_user': request.user.username,
            'signed_in_user_id': request.user.id,
            'creation_time': str(model_item.creation_time.strftime("%m/%d/%Y %-I:%M %p"))
        }

        response_comments.append(my_item)


    response_data = {'posts':response_posts, 'comments':response_comments}
    response_json = json.dumps(response_data)

    return HttpResponse(response_json, content_type='application/json')

def new_comment_action(request):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)
    # To make quiz11 easier, we permit reading the list without logging in. :-)
    # if not request.user.is_authenticated:
    #     return _my_json_error_response("You must be logged in to do this operation", status=403)

    response_comments   = []
    

    for model_item in reversed(Comment.objects.all()):
        my_item = {
            'id': model_item.id,
            'post_id': model_item.post.id,
            'text': model_item.text,
            'creator_username': model_item.creator.username,
            'creator_fullname': model_item.creator.get_full_name(),
            'creator_user_id': model_item.creator.id,
            'signed_in_user': request.user.username,
            'signed_in_user_id': request.user.id,
            'creation_time': str(model_item.creation_time.strftime("%m/%d/%Y %-I:%M %p"))
        }
        print(f'loaded comment: {model_item.creation_time}')
        print(my_item['creation_time'])
        response_comments.append(my_item)
        break


    response_data = {'posts':[], 'comments':response_comments}
    response_json = json.dumps(response_data)

    return HttpResponse(response_json, content_type='application/json')

def add_comment_action(request):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)

    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=405)

    if not 'comment_text' in request.POST or not request.POST['comment_text']:
        return _my_json_error_response("You must enter an item to add.", status=400)
    
    if not 'post_id' in request.POST or not request.POST['post_id']:
        return _my_json_error_response("invalid post id", status=400)
    
    if not request.POST['post_id'].isdigit():
        return _my_json_error_response("invalid post id", status=400)
    
    try:
        Post.objects.get(id=request.POST['post_id'])
    except:
        return _my_json_error_response("invalid post id", status=400)
    
    post_id         = request.POST['post_id']

    text            = request.POST['comment_text']

    creator         = request.user

    creation_time   = timezone.localtime(timezone.now())
    print(f'creation_time at creation before save: {creation_time}')
    post            = Post.objects.get(id=request.POST['post_id'])

    new_comment     = Comment(text=text, creator=creator, creation_time=creation_time, post=post)
    new_comment.save()
    print(f"creation_time at creation after save: {Comment.objects.order_by('-creation_time')[0].creation_time}")


    return new_comment_action(request)

def _my_json_error_response(message, status=200):
    # You can create your JSON by constructing the string representation yourself (or just use json.dumps)
    response_json = '{"error": "' + message + '"}'
    return HttpResponse(response_json, content_type='application/json', status=status)
# Create your views here.
