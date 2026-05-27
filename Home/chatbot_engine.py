import pandas as pd
import re
import random
import os
from datetime import datetime
from django.conf import settings

# Load your CSVs
tvshows_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'Home', 'static', 'tvshows.csv'), encoding='ISO-8859-1')
movies_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'Home', 'static', 'movies.csv'), encoding='ISO-8859-1')
actors_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'Home', 'static', 'actors.csv'), encoding='ISO-8859-1')

print("Actor CSV Columns:", actors_df.columns.tolist())

# Mood keywords mapping
mood_map = {
    'sad': ['healing', 'slice of life', 'comfort', 'friendship'],
    'happy': ['romance', 'comedy', 'feel good'],
    'angry': ['action', 'thriller'],
    'lonely': ['family', 'melodrama'],
    'bored': ['mystery', 'fantasy', 'sci-fi', 'romcom']
}

def get_recommendations_by_mood(user_input):
    for mood, genres in mood_map.items():
        if mood in user_input.lower():
            matches = pd.concat([
                tvshows_df[tvshows_df['Genre'].str.contains('|'.join(genres), case=False, na=False)],
                movies_df[movies_df['Genre'].str.contains('|'.join(genres), case=False, na=False)]
            ])
            if not matches.empty:
                results = matches.sample(min(5, len(matches)))  # 5 random recommendations
                return results[['Title', 'Genre', 'Country', 'Released_Year']].to_dict(orient='records')
    return None

from datetime import datetime

def get_actor_info(actor_name):
    actor_name = actor_name.lower()
    actor_row = actors_df[actors_df['Full Name'].str.lower() == actor_name]

    if not actor_row.empty:
        actor = actor_row.iloc[0]

        # Get and format Born date + Age
        born = "N/A"
        age = "N/A"
        born_raw = actor.get('Born', '').strip()
        try:
            born_date = datetime.strptime(born_raw, "%d-%m-%Y")
            born = born_date.strftime("%d-%m-%Y")
            today = datetime.today()
            age = today.year - born_date.year - ((today.month, today.day) < (born_date.month, born_date.day))
        except Exception as e:
            print("Date parse error:", e)

        # Build the response dictionary
        response = {
            "Name": actor['Full Name'],
            "Born": born,
            "Age": age,
            "Nationality": actor.get('Nationality', 'N/A'),
            "Gender": actor.get('Gender', 'N/A'),
            "Known For": actor.get('Dramas', 'N/A')  # or 'Movies' if preferred
        }

        return response

    return "Sorry, I couldn’t find information for that actor."


def handle_user_input(user_input):
    user_input = user_input.lower()

    # Mood-based recommendations
    if any(mood in user_input for mood in mood_map):
        return get_recommendations_by_mood(user_input)

    # Actor-related keywords
    actor_keywords = ["dramas of", "movies of", "acted in", "tell me about", "who is", "info about"]
    for keyword in actor_keywords:
        if keyword in user_input:
            actor_name = user_input.split(keyword)[-1].strip()
            return get_actor_info(actor_name)

    # Direct actor name match
    for actor in actors_df['Full Name']:
        if actor.lower() in user_input:
            return get_actor_info(actor)

    return "Sorry, I didn't understand. Try asking for mood-based suggestions or actor info."
