from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Group, GroupMember, Poll, Vote
import random, requests
from django.contrib.auth.decorators import login_required
import urllib.parse


API_KEY = "88e134f9"  # API key
OMDB_URL = "http://www.omdbapi.com/"  # API URL

YOUTUBE_API_KEY = "AIzaSyAfJ4PdLFErOwUeJ9dHcdfsxl6-hXJYrKU"  # Replace with your YouTube API key
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"


def fetch_movie_poster_and_trailer(movie_name):
    """Fetch movie poster from OMDb API and trailer from YouTube."""
    # Fetch Poster from OMDB API
    params = {"t": movie_name, "apikey": API_KEY}
    response = requests.get(OMDB_URL, params=params)
    data = response.json()
    
    poster_url = data.get("Poster") if data.get("Response") == "True" else None

    # Fetch Trailer from YouTube API
    youtube_params = {
        "q": f"{movie_name} official trailer",
        "part": "snippet",
        "type": "video",
        "key": YOUTUBE_API_KEY,
        "maxResults": 1
    }
    youtube_response = requests.get(YOUTUBE_SEARCH_URL, params=youtube_params).json()
    
    if youtube_response.get("items"):
        video_id = youtube_response["items"][0]["id"]["videoId"]
        trailer_url = f"https://www.youtube.com/embed/{video_id}"
    else:
        trailer_url = None

    return poster_url, trailer_url
def home(request):
    return render(request, 'home.html')

def sign_up(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect('group_login')

    return render(request, 'sign_up.html')

def group_login(request):
    if request.method == "POST":
        group_name = request.POST['group_name']
        group_password = request.POST['group_password']
        username = request.POST['username']
        user_password = request.POST['password']

        user = authenticate(request, username=username, password=user_password)
        group = Group.objects.filter(name=group_name, password=group_password).first()

        if user and group:
            GroupMember.objects.get_or_create(user=user, group=group)
            login(request, user)
            return redirect('user_dashboard', group_id=group.id)

    return render(request, 'group_login.html')

def create_group(request):
    if request.method == "POST":
        name = request.POST['group_name']
        password = request.POST['password']

        if not Group.objects.filter(name=name).exists():
            group = Group.objects.create(name=name, password=password)
            return redirect('admin_login')

    return render(request, 'create_group.html')

def admin_login(request):
    if request.method == "POST":
        group_name = request.POST.get('group_name')
        group_password = request.POST.get('group_password')

        group = Group.objects.filter(name=group_name, password=group_password).first()

        if group:
            return redirect('admin_dashboard', group_id=group.id)

    return render(request, 'admin_login.html', {'error': 'Invalid group name or password'})

def admin_dashboard(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group_members = GroupMember.objects.filter(group=group).select_related('user')
    members_list = [member.user.username for member in group_members]
    
    if request.method == "POST":
        movie_name = request.POST.get('movie_name')
        if movie_name:
            movie_poster, movie_trailer = fetch_movie_poster_and_trailer(movie_name)
            Poll.objects.create(
                group=group,
                movie_name=movie_name,
                movie_image=movie_poster,
                movie_trailer=movie_trailer  # Save trailer
            )

    polls = Poll.objects.filter(group=group)
    return render(request, 'admin_dashboard.html', {'group': group, 'polls': polls, 'group_members': members_list})

def delete_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    group_id = poll.group.id  # Get the group ID before deleting
    poll.delete()
    return redirect('admin_dashboard', group_id=group_id)

def user_dashboard(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    polls = Poll.objects.filter(group=group)
    has_voted = Vote.objects.filter(user=request.user, poll__group=group).exists()
    
    group_members = GroupMember.objects.filter(group=group).select_related('user')
    members_list = [member.user.username for member in group_members]
    
    # Fetch movie poster and trailer for each poll
    for poll in polls:
        if not poll.movie_image or not poll.movie_trailer:
            movie_poster, movie_trailer = fetch_movie_poster_and_trailer(poll.movie_name)
            poll.movie_image = movie_poster
            poll.movie_trailer = movie_trailer
            poll.save()
    
    return render(request, 'user_dashboard.html', {
        'group': group,
        'polls': polls,
        'has_voted': has_voted,
        'group_members': members_list,
        'user': request.user
    })
def vote(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    if not Vote.objects.filter(user=request.user, poll=poll).exists():
        poll.votes += 1
        poll.save()
        Vote.objects.create(user=request.user, poll=poll)
    
    return redirect('user_dashboard', group_id=poll.group.id)

def show_results(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    polls = Poll.objects.filter(group=group).order_by('-votes')
    return render(request, 'results.html', {'group': group, 'polls': polls})

def randomize_tie(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    top_polls = Poll.objects.filter(group=group).order_by('-votes')

    if len(top_polls) > 1 and top_polls[0].votes == top_polls[1].votes:
        winner = random.choice(top_polls[:2])
    else:
        winner = top_polls[0]

    return render(request, 'winner.html', {'group': group, 'winner': winner})

def search_movies(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    movies = []
    category = request.GET.get('category')
    rating = request.GET.get('rating')
    year = request.GET.get('year')
    
    if category or rating or year:
        params = {
            "apikey": API_KEY,
            "s": category if category else "",
            "y": year if year else "",
            "type": "movie"
        }
        response = requests.get(OMDB_URL, params=params).json()
        
        if response.get("Response") == "True":
            for movie in response.get("Search", [])[:5]:
                movie_details = requests.get(OMDB_URL, params={"apikey": API_KEY, "t": movie["Title"]}).json()
                
                imdb_rating = movie_details.get("imdbRating", "0")
                try:
                    imdb_rating = float(imdb_rating) if imdb_rating != "N/A" else 0.0
                except ValueError:
                    imdb_rating = 0.0
                
                if rating and imdb_rating < float(rating):
                    continue
                if year and movie_details.get("Year") != str(year):
                    continue
                
                movies.append(movie_details)

    return render(request, 'movie_search.html', {'group': group, 'movies': movies})

MOVIEPIRE_SEARCH_URL = "https://moviepire.net/search?q="  

def watch_movie(request,group_id):
    group = get_object_or_404(Group,id=group_id)
    if request.method == "POST":
        query = request.POST.get("query","").strip()
        if query:
            search_url = MOVIEPIRE_SEARCH_URL + urllib.parse.quote(query)
            return redirect(search_url)
    
    return render(request, "watch.html", {"group": group})