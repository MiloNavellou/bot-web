"""
app/spotify.py - Intégration Spotify API

Gère:
- Authentification avec Spotify
- Recherche de chansons
- Recommandations basées sur les genres/artistes
- Infos sur les chansons
"""

import os
import requests
import base64
from typing import List, Dict, Tuple
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

# URLs Spotify
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_URL = "https://api.spotify.com/v1"


class SpotifyClient:
    """
    Client pour l'API Spotify
    
    Gère l'authentification et les requêtes à Spotify
    """
    
    def __init__(self):
        """Initialise le client Spotify"""
        self.access_token = None
        self.token_expiry = None
        self.authenticate()
    
    def authenticate(self) -> bool:
        """
        S'authentifie auprès de Spotify
        
        Utilise Client Credentials Flow (pas besoin d'utilisateur)
        
        Returns:
            bool: True si authentifié, False sinon
        """
        
        if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
            print("❌ Erreur: Variables Spotify manquantes (.env)")
            return False
        
        # Encoder les credentials en base64
        auth_str = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
        auth_bytes = auth_str.encode('utf-8')
        auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
        
        headers = {
            "Authorization": f"Basic {auth_base64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "client_credentials"
        }
        
        try:
            response = requests.post(SPOTIFY_AUTH_URL, headers=headers, data=data)
            response.raise_for_status()
            
            auth_data = response.json()
            self.access_token = auth_data['access_token']
            
            print("✅ Authentification Spotify réussie!")
            return True
        
        except Exception as e:
            print(f"❌ Erreur d'authentification Spotify: {e}")
            return False
    
    def _get_headers(self) -> dict:
        """Retourne les headers pour les requêtes authentifiées"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def search_track(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Cherche une chanson sur Spotify
        
        Args:
            query (str): Texte à chercher
            limit (int): Nombre de résultats (1-50)
            
        Returns:
            List[Dict]: Liste des résultats
        """
        
        if not self.access_token:
            return []
        
        try:
            params = {
                "q": query,
                "type": "track",
                "limit": min(limit, 50)
            }
            
            response = requests.get(
                f"{SPOTIFY_API_URL}/search",
                headers=self._get_headers(),
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            tracks = data.get('tracks', {}).get('items', [])
            
            # Formater les résultats
            results = []
            for track in tracks:
                results.append({
                    'name': track['name'],
                    'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown',
                    'album': track['album']['name'],
                    'url': track['external_urls']['spotify'],
                    'popularity': track['popularity']
                })
            
            return results
        
        except Exception as e:
            print(f"❌ Erreur recherche Spotify: {e}")
            return []
    
    def search_artist(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Cherche un artiste sur Spotify
        
        Args:
            query (str): Nom de l'artiste
            limit (int): Nombre de résultats
            
        Returns:
            List[Dict]: Liste des artistes
        """
        
        if not self.access_token:
            return []
        
        try:
            params = {
                "q": query,
                "type": "artist",
                "limit": min(limit, 50)
            }
            
            response = requests.get(
                f"{SPOTIFY_API_URL}/search",
                headers=self._get_headers(),
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            artists = data.get('artists', {}).get('items', [])
            
            results = []
            for artist in artists:
                results.append({
                    'name': artist['name'],
                    'genres': artist.get('genres', [])[:3],  # Top 3 genres
                    'popularity': artist['popularity'],
                    'url': artist['external_urls']['spotify']
                })
            
            return results
        
        except Exception as e:
            print(f"❌ Erreur recherche artiste: {e}")
            return []
    
    def get_recommendations(self, seed_artists: List[str] = None, 
                           seed_genres: List[str] = None,
                           limit: int = 5) -> List[Dict]:
        """
        Obtient des recommandations basées sur des artistes/genres
        
        Args:
            seed_artists (List[str]): Liste d'IDs d'artistes
            seed_genres (List[str]): Liste de genres
            limit (int): Nombre de recommandations
            
        Returns:
            List[Dict]: Chansons recommandées
        """
        
        if not self.access_token:
            return []
        
        try:
            params = {
                "limit": min(limit, 50)
            }
            
            if seed_artists:
                params['seed_artists'] = ','.join(seed_artists[:5])  # Max 5
            
            if seed_genres:
                params['seed_genres'] = ','.join(seed_genres[:5])  # Max 5
            
            if not seed_artists and not seed_genres:
                params['seed_genres'] = 'pop'  # Default
            
            response = requests.get(
                f"{SPOTIFY_API_URL}/recommendations",
                headers=self._get_headers(),
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            tracks = data.get('tracks', [])
            
            results = []
            for track in tracks:
                results.append({
                    'name': track['name'],
                    'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown',
                    'album': track['album']['name'],
                    'url': track['external_urls']['spotify'],
                    'popularity': track['popularity']
                })
            
            return results
        
        except Exception as e:
            print(f"❌ Erreur recommandations: {e}")
            return []
    
    def get_available_genres(self) -> List[str]:
        """
        Récupère la liste des genres disponibles
        
        Returns:
            List[str]: Liste des genres
        """
        
        if not self.access_token:
            return []
        
        try:
            response = requests.get(
                f"{SPOTIFY_API_URL}/recommendations/available-genre-seeds",
                headers=self._get_headers()
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get('genres', [])
        
        except Exception as e:
            print(f"❌ Erreur genres: {e}")
            return []


# Instance globale du client Spotify
spotify_client = SpotifyClient()


# ========== FONCTIONS PUBLIQUES ==========

def search_music(query: str) -> str:
    """
    Cherche une musique et retourne une réponse formatée
    
    Args:
        query (str): Texte à chercher
        
    Returns:
        str: Réponse formatée
    """
    
    tracks = spotify_client.search_track(query, limit=3)
    
    if not tracks:
        return "🎵 Désolé, je n'ai trouvé aucune chanson correspondant à ta recherche."
    
    response = "🎵 Voici ce que j'ai trouvé:\n\n"
    
    for i, track in enumerate(tracks, 1):
        response += f"{i}. **{track['name']}** - {track['artist']}\n"
        response += f"   Album: {track['album']}\n"
        response += f"   🔗 {track['url']}\n\n"
    
    return response


def search_artist(query: str) -> str:
    """
    Cherche un artiste et retourne une réponse formatée
    
    Args:
        query (str): Nom de l'artiste
        
    Returns:
        str: Réponse formatée
    """
    
    artists = spotify_client.search_artist(query, limit=3)
    
    if not artists:
        return "🎤 Désolé, je n'ai trouvé aucun artiste avec ce nom."
    
    response = "🎤 Artistes trouvés:\n\n"
    
    for i, artist in enumerate(artists, 1):
        genres = ", ".join(artist['genres']) if artist['genres'] else "Genres variés"
        response += f"{i}. **{artist['name']}**\n"
        response += f"   Genres: {genres}\n"
        response += f"   Popularité: {artist['popularity']}/100\n"
        response += f"   🔗 {artist['url']}\n\n"
    
    return response


def get_recommendations_by_genre(genre: str) -> str:
    """
    Obtient des recommandations pour un genre
    
    Args:
        genre (str): Genre musical
        
    Returns:
        str: Réponse formatée
    """
    
    # Vérifier que le genre existe
    available_genres = spotify_client.get_available_genres()
    genre_lower = genre.lower()
    
    if genre_lower not in available_genres:
        return f"❌ Genre '{genre}' non reconnu. Voici quelques genres disponibles: pop, rock, hip-hop, jazz, classical, electronic..."
    
    tracks = spotify_client.get_recommendations(seed_genres=[genre_lower], limit=5)
    
    if not tracks:
        return f"🎵 Désolé, je n'ai pas pu trouver de recommandations pour le genre '{genre}'."
    
    response = f"🎵 Recommandations pour **{genre}**:\n\n"
    
    for i, track in enumerate(tracks, 1):
        response += f"{i}. **{track['name']}** - {track['artist']}\n"
        response += f"   Album: {track['album']}\n"
        response += f"   🔗 {track['url']}\n\n"
    
    return response