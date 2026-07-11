import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
BASE_URL = "http://api.football-data.org/v4"

HEADERS = {
    "X-Auth-Token": API_KEY
}

def get_standings(competition_code="PL"):
    """
    Fetches the current standings for a league to calculate average goals.
    competition_code: PL (Premier League), PD (La Liga), SA (Serie A), BL1 (Bundesliga), FL1 (Ligue 1)
    """
    if not API_KEY:
        raise ValueError("Missing FOOTBALL_DATA_API_KEY in .env file")
        
    url = f"{BASE_URL}/competitions/{competition_code}/standings"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        raise Exception(f"API Error fetching standings: {response.status_code} - {response.text}")
        
    return response.json()

def get_upcoming_matches(competition_code="PL"):
    """
    Fetches scheduled matches for the current matchday.
    """
    url = f"{BASE_URL}/competitions/{competition_code}/matches?status=SCHEDULED"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        raise Exception(f"API Error fetching upcoming matches: {response.status_code} - {response.text}")
        
    return response.json()

def get_finished_matches(competition_code="PL"):
    """
    Fetches recently finished matches to evaluate our past predictions.
    """
    url = f"{BASE_URL}/competitions/{competition_code}/matches?status=FINISHED"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        raise Exception(f"API Error fetching finished matches: {response.status_code} - {response.text}")
        
    return response.json()
