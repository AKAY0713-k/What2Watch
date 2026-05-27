from django.shortcuts import render, HttpResponse, redirect
from datetime import datetime
from Home.models import ContactMessage
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Drama
from datetime import date
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics
from django.contrib.auth.models import User
import requests
import csv
from datetime import date
import pandas as pd
from django.shortcuts import render, get_object_or_404
from .models import Actor
from django.db.models import Count
import os
import csv
from django.conf import settings
from django.http import HttpResponseNotFound
from django.db.models import Q
from django.core.paginator import Paginator

from django.http import JsonResponse
import csv
from django.conf import settings

from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import render, redirect

import pandas as pd
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .chatbot_engine import handle_user_input 

# views.py
from django.http import JsonResponse
import json
from .chatbot_engine import handle_user_input  

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def chatbot(request):
    if request.method == 'GET':
        return render(request, 'chatbot.html')

    if request.method == 'POST':
        try:
            message = request.POST.get('message')

            if not message:
                return render(request, 'chatbot.html', {'response': "No message provided."})

            from Home.chatbot_engine import handle_user_input
            raw_response = handle_user_input(message)

            if isinstance(raw_response, list):
                formatted_response = "\n".join([
                    f"🎬 {r.get('Title', 'N/A')} – {r.get('Genre', 'Unknown')} | {r.get('Country', 'Unknown')} ({r.get('Released_Year', 'N/A')})"
                    for r in raw_response
                ])
            elif isinstance(raw_response, dict):
                formatted_response = (
                    f"👤 Name: {raw_response.get('Name', 'N/A')}\n"
                    f"📅 Born: {raw_response.get('Born', 'N/A')}\n"
                    f"🌍 Nationality: {raw_response.get('Nationality', 'N/A')}\n"
                    f"⚧ Gender: {raw_response.get('Gender', 'N/A')}\n"
                    f"🎭 Known For: {raw_response.get('Known For', 'N/A')}"
                )
            elif isinstance(raw_response, str):
                formatted_response = raw_response
            else:
                formatted_response = "Sorry, I couldn't understand that."

            return render(request, 'chatbot.html', {'response': formatted_response})

        except Exception as e:
            return render(request, 'chatbot.html', {'response': f"Error: {str(e)}"})

    return render(request, 'chatbot.html', {'response': "Invalid request."})


def about(request):
    return render(request,'about.html')

def movies(request):
    return render(request,'movies.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        company = request.POST.get('company')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        desc = request.POST.get('desc')

        # Save to database
        contact_obj = ContactMessage(
            name=name,
            company=company,
            phone=phone,
            email=email,
            subject=subject,
            desc=desc
        )
        contact_obj.save()

        # Send email
        send_mail(
            subject=f"New Contact Form: {subject}",
            message=f"""
Name: {name}
Company: {company}
Phone: {phone}
Email: {email}

Message:
{desc}
""",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=['what2watch.support@gmail.com'],
            fail_silently=False,
        )

        messages.success(request, 'Your message has been sent!')
        return redirect('contact')

    return render(request, 'contact.html')





def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("userprofile")  
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")
    return render(request, "login.html")


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
       
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')  # Reload the signup page

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('signup')

        user = User.objects.create_user(username=username, password=password)

        # Avoid UNIQUE constraint error
        UserProfile.objects.get_or_create(user=user)

        messages.success(request, "Signup successful. Please log in.")
        return redirect('login')  

    return render(request, 'signup.html')


# views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import WatchlistItem, UserProfile

from .models import WatchlistItem

@login_required
@login_required
def userprofile(request):
    profile = request.user.userprofile

    context = {
        "UserProfile": profile,
        "currently_watching": WatchlistItem.objects.filter(user=request.user, status="currently_watching"),
        "completed": WatchlistItem.objects.filter(user=request.user, status="completed"),
        "on_hold": WatchlistItem.objects.filter(user=request.user, status="on_hold"),
        "dropped": WatchlistItem.objects.filter(user=request.user, status="dropped"),
        "plan_to_watch": WatchlistItem.objects.filter(user=request.user, status="plan_to_watch"),  # this was missing
    }

    return render(request, "userprofile.html", context)


@login_required
def upload_avatar(request):
    if request.method == 'POST' and request.FILES.get('upload_avatar'):
        profile = UserProfile.objects.get(user=request.user)
        profile.upload_avatar = request.FILES['upload_avatar']
        profile.save()
        messages.success(request, 'Profile image uploaded successfully!')
        return redirect('userprofile')

    messages.error(request, 'No file selected.')
    return redirect('userprofile')

def logout_view(request):
    logout(request)
    return redirect('homepage')


def homepage(request):
    csv_path_upcoming = os.path.join(settings.BASE_DIR, 'Home', 'static', 'Upcoming.csv')
    csv_path_trending = os.path.join(settings.BASE_DIR, 'Home', 'static', 'Trending.csv')

    upcoming = []
    trending = []

    def process_csv(csv_path):
        shows = []
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                genre_list = [g.strip() for g in row['Genre'].split(',')]
                shows.append({
                    'title': row['Title'],
                    'image': row['Image_URL'],
                    'genre': genre_list,
                    'country': row['Country']
                })
        return shows

    upcoming = process_csv(csv_path_upcoming)
    trending = process_csv(csv_path_trending)

    context = {
        'upcoming': upcoming,
        'trending': trending,
    }
    return render(request, 'homepage.html', context)

def actor_list(request):
    # Path to your CSV file
    csv_path = os.path.join(settings.BASE_DIR, 'Home', 'static', 'actors.csv')

    # Read CSV using pandas
    df = pd.read_csv(csv_path, encoding='ISO-8859-1')

    # Convert to list of dictionaries
    actors = df.to_dict(orient='records')

    # Send to HTML template
    return render(request, 'actors.html', {'actors': actors})

def load_actors_from_csv():
    with open('path/to/your/file.csv', encoding='utf-8', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            Actor.objects.create(
                name=row['Name'],
                dob=row.get('DOB'),
                gender=row.get('Gender'),
                age=int(row['Age']) if row['Age'].isdigit() else None,
                nationality=row.get('Nationality'),
                description=row.get('Description'),
                dramas=row.get('Dramas'),
                movies=row.get('Movies'),
            )



def actors(request):
    csv_path = os.path.join(settings.BASE_DIR, 'Home', 'data', 'actors.csv')

    actors_list = []

    with open(csv_path, newline='', encoding='ISO-8859-1') as csvfile:
        reader = csv.DictReader(csvfile)
        for index, row in enumerate(reader):
          name = row.get('Full Name', '').strip()
          if name:  
             actors_list.append({
            'name': name,
            'nationality': row.get('Nationality', '').strip(),
            'gender': row.get('Gender', '').strip(),
            'image': row.get('Image_URL', '').strip(),
            'description': row.get('Description', '').strip()
        })


    nationalities = sorted(set(actor['nationality'] for actor in actors_list))
    genders = sorted(set(actor['gender'] for actor in actors_list))

    # Get selected filters from request
    selected_nationality = request.GET.getlist('nationality')
    selected_gender = request.GET.getlist('gender')

    # Filter actors based on selected filters
    filtered_actors = actors_list
    if selected_nationality:
        filtered_actors = [a for a in filtered_actors if a['nationality'] in selected_nationality]
    if selected_gender:
        filtered_actors = [a for a in filtered_actors if a['gender'] in selected_gender]
    # Pagination
    paginator = Paginator(filtered_actors, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    
    context = {
        'page_obj': page_obj,
        'actors': page_obj.object_list,
        'nationalities': nationalities,
        'genders': genders,
        'selected_nationality': selected_nationality,
        'selected_gender': selected_gender,
    }

    return render(request, 'actors.html', context)




def actor_profile(request, actor_name):
    actor_name = actor_name.strip().lower()  # Slug in URL
    csv_path = os.path.join(settings.BASE_DIR, 'Home', 'static', 'actors.csv')

    with open(csv_path, newline='', encoding='ISO-8859-1') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            full_name = row.get('Full Name', '').strip()
            if slugify(full_name) == actor_name:
                dramas = [d.strip() for d in row['Dramas'].split(',')] if row['Dramas'] else []
                drama_years = [y.strip() for y in row['Drama_Year'].split(',')] if row['Drama_Year'] else []
                movies = [m.strip() for m in row['Movies'].split(',')] if row['Movies'] else []
                movie_years = [y.strip() for y in row['Movie_Year'].split(',')] if row['Movie_Year'] else []

                actor = {
                    'name': row['Full Name'],
                    'gender': row['Gender'],
                    'born': row['Born'],
                    'age': row['Age'],
                    'nationality': row['Nationality'],
                    'description': row['Description'],
                    'dramas': list(zip(dramas, drama_years)),
                    'movies': list(zip(movies, movie_years)),
                    'image': row['Image_URL'],
                }

                return render(request, 'actor_profile.html', {'actor': actor})

    return HttpResponseNotFound("Actor not found")




def tv_shows(request):
    file_path = os.path.join('Home', 'static', 'tvshows.csv')
    dramas = []  

    with open(file_path, encoding='latin1') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dramas.append({
                'title': row['Title'],
                'image': row['Image_URL'],
                'country': row['Country'],
                'release_year': row['Released_Year'],
                'episodes': int(row['Episodes']),
                'rating': float(row['Rating']),
                'description': row['Description'],
                'trailer_url': row['Trailer_URL'],
                'type': row['Type'],
                'status': row['Status'],
                'genre': row['Genre'],
                'tags': row['Tags'],
            })
    countries = sorted(set(d['country'] for d in dramas if d['country']))
    types = sorted(set(d['type'] for d in dramas if d['type']))
    statuses = sorted(set(d['status'] for d in dramas if d['status']))


    genre_set = set()
    for drama in dramas:
        if drama['genre']:
            genre_set.update(g.strip() for g in drama['genre'].split(','))

    genres = sorted(genre_set)

    type_filter = request.GET.get('type')
    country_filter = request.GET.get('country')
    genre_filter = request.GET.get('genre')
    status_filter = request.GET.get('status')

    # Apply filters
    if type_filter:
        dramas = [d for d in dramas if d['type'].lower() == type_filter.lower()]
    if country_filter:
        dramas = [d for d in dramas if d['country'].lower() == country_filter.lower()]
    if genre_filter:
       dramas = [d for d in dramas if genre_filter.lower() in d['genre'].lower()]
    if status_filter:
        dramas = [d for d in dramas if d['status'].lower() == status_filter.lower()]

    # Pagination (10 per page)
    paginator = Paginator(dramas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    
    # Top 5 trending (by rating, ongoing or upcoming)
    top_trending = sorted(
        [d for d in dramas if 'ongoing' in d['status'].lower() or 'upcoming' in d['status'].lower() or 'completed' in d['status'].lower()],
        key=lambda x: x['rating'],
        reverse=True
    )[:6]

    context = {
        'page_obj': page_obj,
        'countries': countries,
        'types': types,
        'statuses': statuses,
        'genres': genres,
        'top_trending': top_trending,
    }

    return render(request, 'tvshows.html', context)
from django.utils.text import slugify


def dramaview(request, title):
    file_path = os.path.join('Home', 'static', 'tvshows.csv')
    selected_drama = None

    with open(file_path, encoding='latin1') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if slugify(row['Title']) == title:
                selected_drama = {
                    'title': row['Title'],
                    'image': row['Image_URL'],
                    'country': row['Country'],
                    'release_year': row['Released_Year'],
                    'episodes': int(row['Episodes']),
                    'rating': float(row['Rating']),
                    'description': row['Description'],
                    'trailer_url': row['Trailer_URL'],
                    'type': row['Type'],
                    'status': row['Status'],
                    'genre': row['Genre'],
                    'tags': row['Tags'],
                    'duration':row['Duration'],
                    'original_network':row['Original_Network'],
                    'where_to_watch': row['Where_to_Watch'].split(',') if row['Where_to_Watch'] else [],
                    'cast': row['Cast'].split(',') if row['Cast'] else [],
                    'photos': row['Photos'].split(',') if row['Photos'] else [],
                }
                break

    if not selected_drama:
        return HttpResponse("Drama not found", status=404)

    rating_range = range(1, 11)  
    episode_range = range(1, selected_drama['episodes'] + 1)  # e.g., 1 to 16

    return render(request, 'dramaview.html', {
        'drama': selected_drama,
        'rating_range': rating_range,
        'episode_range': episode_range,
    })

def movies(request):
    file_path = os.path.join('Home', 'static', 'movies.csv')  # Assuming you have a movies.csv
    movies = []

    with open(file_path, encoding='latin1') as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies.append({
                'title': row['Title'],
                'image': row['Image_URL'],
                'country': row['Country'],
                'release_year': row['Released_Year'],
                'rating': float(row['Rating']) if row['Rating'].strip() else 0.0,
                'description': row['Description'],
                'trailer_url': row['Trailer_URL'],
                'status': row['Status'],
                'genre': row['Genre'],
                'tags': row['Tags'],
            })

    # Filter dropdown options
    countries = sorted(set(m['country'] for m in movies if m['country']))
    statuses = sorted(set(m['status'] for m in movies if m['status']))

    genre_set = set()
    for movie in movies:
        if movie['genre']:
            genre_set.update(g.strip() for g in movie['genre'].split(','))

    genres = sorted(genre_set)

    # Filters from request
    country_filter = request.GET.get('country')
    genre_filter = request.GET.get('genre')
    status_filter = request.GET.get('status')

    # Apply filters
   
    if country_filter:
        movies = [m for m in movies if m['country'].lower() == country_filter.lower()]
    if genre_filter:
        movies = [m for m in movies if genre_filter.lower() in m['genre'].lower()]
    if status_filter:
        movies = [m for m in movies if m['status'].lower() == status_filter.lower()]

    paginator = Paginator(movies, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    top_trending = sorted(
        [m for m in movies if 'ongoing' in m['status'].lower() or 'upcoming' in m['status'].lower() or 'completed' in m['status'].lower()],
        key=lambda x: x['rating'],
        reverse=True
    )[:6]

    context = {
        'page_obj': page_obj,
        'countries': countries,
        'statuses': statuses,
        'genres': genres,
        'top_trending': top_trending,
    }

    return render(request, 'movies.html', context)

def movieview(request, title):
    file_path = os.path.join('Home', 'static', 'movies.csv')
    selected_movie = None

    with open(file_path, encoding='latin1') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Title'].strip().lower() == title.strip().lower():
                selected_movie = {
                    'title': row['Title'],
                    'image': row['Image_URL'],
                    'country': row['Country'],
                    'release_year': row['Released_Year'],
                    'rating': float(row['Rating']),
                    'description': row['Description'],
                    'trailer_url': row['Trailer_URL'],
                    'status': row['Status'],
                    'genre': row['Genre'],
                    'tags': row['Tags'],
                    'duration':row['Duration'],
                    'where_to_watch': row['Where_to_Watch'].split(',') if row['Where_to_Watch'] else [],
                    'cast': row['Cast'].split(',') if row['Cast'] else [],
                    'photos': row['Photos'].split(',') if row['Photos'] else [],
                }
                break

    if not selected_movie:
        return HttpResponse("Drama not found", status=404)


    rating_range = range(1, 11)  

    return render(request, 'movieview.html', {'movie': selected_movie,
                          'rating_range': rating_range
                            })
from django.shortcuts import render, redirect
import csv
import os
from django.conf import settings

def search(request):
    query = request.GET.get('q', '').strip().lower()
    matched_dramas = []
    matched_movies = []
    matched_actors = []

    if query:
        # --- TV Shows ---
        tv_path = os.path.join('Home', 'static', 'tvshows.csv')
        with open(tv_path, encoding='latin1') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if query in row['Title'].strip().lower():
                    matched_dramas.append({
                        'title': row['Title'],
                        'image': row['Image_URL'],
                        'description':row['Description'],
                         'country':row['Country'],
                        'type': 'Drama'
                    })

        # --- Movies ---
        movie_path = os.path.join('Home', 'static', 'movies.csv')
        with open(movie_path, encoding='latin1') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if query in row['Title'].strip().lower():
                    matched_movies.append({
                        'title': row['Title'],
                        'image': row['Image_URL'],
                        'description':row['Description'],
                        'country':row['Country'],
                        'type': 'Movie'
                    })
        actor_path = os.path.join('Home', 'static', 'actors.csv')
        with open(actor_path, encoding='latin1') as f:
             reader = csv.DictReader(f)
             for row in reader:
              print("Checking actor:", row['Full Name'])
              if query in row['Full Name'].strip().lower():
                print("Match found:", row['Full Name'])  # ← This should print!
                matched_actors.append({
                    'name': row['Full Name'],
                    'image': row['Image_URL'],
                    'description':row['Description'],
                    'nationality':row['Nationality']

        })



    context = {
        'query': query,
        'matched_dramas': matched_dramas,
        'matched_movies': matched_movies,
        'matched_actors': matched_actors
    }

    return render(request, 'search_results.html', context)

from .models import WatchlistItem
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

# views.py

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import redirect
from .models import WatchlistItem

@require_POST
@login_required
def add_to_watchlist(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        image_url = request.POST.get('image_url')
        content_type = request.POST.get('content_type')
        status = request.POST.get('status')
        rating = request.POST.get('rating', 0)
        episodes_watched = request.POST.get('episodes_watched', 0)
        notes = request.POST.get('notes', '')

        watchlist, created = WatchlistItem.objects.update_or_create(
            user=request.user,
            title=title,
            defaults={
                'image_url': image_url,
                'content_type': content_type,
                'status': status,
                'rating': rating,
                'episodes_watched': episodes_watched,
                'notes': notes,
            }
        )

        return redirect('userprofile')