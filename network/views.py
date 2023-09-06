from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect , JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from .models import User , Post, Follow, Like
import json

def remove_like(request , post_id):
    post = Post.objects.get(pk = post_id)
    user = User.objects.get(pk = request.user.id)
    like = Like.objects.filter(user = user, post= post)
    like.delete()
    return JsonResponse ({"message" : "Post unliked"})

def add_like(request,post_id):
    post = Post.objects.get(pk = post_id)
    user = User.objects.get(pk = request.user.id)
    newLike = Like(user = user ,post=post)
    newLike.save()
    return JsonResponse ({"message" : "Post liked"})



def index(request):
    posts = Post.objects.all().order_by("id").reverse()

    paginator = Paginator(posts , 10)
    page_number = request.GET.get('page')
    page_posts = paginator.get_page(page_number)

    likes = Like.objects.all()
    likedWho = []
    try:
        for like in likes:
            if like.user.id == request.user.id:
                likedWho.append(like.post.id)
    except:
        likedWho = []

    return render(request, "network/index.html", {
        "posts":posts,
        "page_posts":page_posts,
        "likedWho" : likedWho
    })

def profile(request , user_id):
    user = User.objects.get(pk=user_id)
    posts = Post.objects.filter(user=user).order_by("id").reverse()

    following = Follow.objects.filter(user=user)
    followers = Follow.objects.filter(user_follower = user)

    try:
        followCheck = followers.filter(user= User.objects.get(pk=request.user.id) )
        if len(followCheck) != 0 :
            isFollowing = True
        else:
            isFollowing = False
    except:
        isFollowing = False        

    paginator = Paginator(posts , 10)
    page_number = request.GET.get('page')
    page_posts = paginator.get_page(page_number)

    return render(request, "network/profile.html", {
        "posts":posts,
        "page_posts":page_posts,
        "username":user.username,
        "following":following,
        "followers":followers,
        "isFollowing":isFollowing,
        "user_profile":user
    })

def follow (request):
    userfollow = request.POST['userfollow']
    currentUser = User.objects.get(pk = request.user.id)
    userfollowData = User.objects.get(username = userfollow)
    follo = Follow(user= currentUser , user_follower = userfollowData)
    follo.save()
    user_id = userfollowData.id
    return HttpResponseRedirect(reverse("profile", kwargs={'user_id':user_id}))

def unfollow(request):
    userfollow = request.POST['userfollow']
    currentUser = User.objects.get(pk = request.user.id)
    userfollowData = User.objects.get(username = userfollow)
    follo = Follow.objects.get(user= currentUser , user_follower = userfollowData)
    follo.delete()
    user_id = userfollowData.id
    return HttpResponseRedirect(reverse("profile", kwargs={'user_id':user_id}))

def following(request):
    currentUser = User.objects.get(pk = request.user.id)
    followingPeople = Follow.objects.filter(user= currentUser)
    posts = Post.objects.all().order_by('id').reverse()
    followingPost=[]

    for post in posts:
        for person in followingPeople:
            if person.user_follower == post.user:
                followingPost.append(post)

    paginator = Paginator(followingPost , 10)
    page_number = request.GET.get('page')
    page_posts = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "page_posts":page_posts
    })


def edit(request,post_id):
    if request.method == "POST":
        data = json.loads(request.body)
        editPost = Post.objects.get(pk = post_id)
        editPost.content = data["content"]
        editPost.save()
        return JsonResponse({"message": "change successfully" , "data" : data["content"]})

def newPost(request):
    if request.method == "POST":
        content = request.POST['content']
        user = User.objects.get(pk=request.user.id)
        post = Post(content=content , user=user)
        post.save()
        return HttpResponseRedirect(reverse("index"))

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
