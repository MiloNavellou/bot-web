"""
app/lastfm.py - Intégration Last.fm API

Gère:
- Recherche de chansons
- Recherche d'artistes
- Recommandations basées sur les genres
- Top charts
- Infos détaillées
"""

import os
import requests
from typing import List, Dict
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

LASTFM_API_KEY = os.getenv('LASTFM_API_KEY')
LASTFM_API_URL = "http://ws.audioscrobbler.com/2.0/"


class LastfmClient:
    """
    Client pour l'API Last.fm
    
    Gère les requêtes à Last.fm
    """
    
    def __init__(self):
        """Initialise le client Last.fm"""
        if not LASTFM_API_KEY:
            print("❌ Erreur: LASTFM_API_KEY manquante dans .env")
        else:
            print("✅ Last.fm API initialisée!")
    
    def _make_request(self, **kwargs) -> dict:
        """
        Fait une requête à Last.fm
        
        Args:
            **kwargs: Paramètres de la requête
            
        Returns:
            dict: Réponse JSON
        """
        
        params = {
            'api_key': LASTFM_API_KEY,
            'format': 'json',
            **kwargs
        }
        
        try:
            response = requests.get(LASTFM_API_URL, params=params, timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Erreur Last.fm: {e}")
            return {}
    
    def search_track(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Cherche une chanson sur Last.fm
        
        Args:
            query (str): Texte à chercher
            limit (int): Nombre de résultats
            
        Returns:
            List[Dict]: Liste des résultats
        """
        
        data = self._make_request(method='track.search', track=query, limit=limit)
        
        if 'results' not in data or 'trackmatches' not in data['results']:
            return []
        
        results = []
        for track in data['results']['trackmatches']['track'][:limit]:
            results.append({
                'name': track.get('name', 'Unknown'),
                'artist': track.get('artist', 'Unknown'),
                'url': track.get('url', '#'),
                'listeners': track.get('listeners', '0')
            })
        
        return results
    
    def search_artist(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Cherche un artiste sur Last.fm
        
        Args:
            query (str): Nom de l'artiste
            limit (int): Nombre de résultats
            
        Returns:
            List[Dict]: Liste des artistes
        """
        
        data = self._make_request(method='artist.search', artist=query, limit=limit)
        
        if 'results' not in data or 'artistmatches' not in data['results']:
            return []
        
        results = []
        for artist in data['results']['artistmatches']['artist'][:limit]:
            results.append({
                'name': artist.get('name', 'Unknown'),
                'url': artist.get('url', '#'),
                'listeners': artist.get('listeners', '0'),
                'mbid': artist.get('mbid', '')
            })
        
        return results
    
    def get_artist_info(self, artist: str) -> Dict:
        """
        Obtient les infos détaillées d'un artiste
        
        Args:
            artist (str): Nom de l'artiste
            
        Returns:
            Dict: Infos de l'artiste
        """
        
        data = self._make_request(method='artist.getinfo', artist=artist)
        
        if 'artist' not in data:
            return {}
        
        artist_data = data['artist']
        
        return {
            'name': artist_data.get('name', 'Unknown'),
            'listeners': artist_data.get('stats', {}).get('listeners', '0'),
            'playcount': artist_data.get('stats', {}).get('playcount', '0'),
            'bio': artist_data.get('bio', {}).get('summary', 'No bio available'),
            'url': artist_data.get('url', '#'),
            'similar': [a.get('name') for a in artist_data.get('similar', {}).get('artist', [])[:5]]
        }
    
    def get_similar_artists(self, artist: str, limit: int = 5) -> List[Dict]:
        """
        Obtient les artistes similaires
        
        Args:
            artist (str): Nom de l'artiste de référence
            limit (int): Nombre de résultats
            
        Returns:
            List[Dict]: Artistes similaires
        """
        
        data = self._make_request(method='artist.getsimilar', artist=artist, limit=limit)
        
        if 'similarartists' not in data:
            return []
        
        results = []
        for similar in data['similarartists']['artist'][:limit]:
            results.append({
                'name': similar.get('name', 'Unknown'),
                'match': similar.get('match', '0'),  # Score de similarité (0-1)
                'url': similar.get('url', '#')
            })
        
        return results
    
    def get_top_tracks_by_tag(self, tag: str, limit: int = 5) -> List[Dict]:
        """
        Obtient les top chansons d'un genre/tag
        
        Args:
            tag (str): Genre ou tag (pop, rock, hip-hop, etc.)
            limit (int): Nombre de résultats
            
        Returns:
            List[Dict]: Top chansons
        """
        
        data = self._make_request(method='tag.gettoptracks', tag=tag, limit=limit)
        
        if 'tracks' not in data or 'track' not in data['tracks']:
            return []
        
        results = []
        for track in data['tracks']['track'][:limit]:
            results.append({
                'name': track.get('name', 'Unknown'),
                'artist': track.get('artist', {}).get('name', 'Unknown') if isinstance(track.get('artist'), dict) else track.get('artist', 'Unknown'),
                'playcount': track.get('playcount', '0'),
                'url': track.get('url', '#')
            })
        
        return results


# Instance globale du client Last.fm
lastfm_client = LastfmClient()


# ========== FONCTIONS PUBLIQUES ==========

def search_music(query: str) -> str:
    """
    Cherche une musique et retourne une réponse formatée
    
    Args:
        query (str): Texte à chercher
        
    Returns:
        str: Réponse formatée
    """
    
    tracks = lastfm_client.search_track(query, limit=3)
    
    if not tracks:
        return "🎵 Désolé, je n'ai trouvé aucune chanson correspondant à ta recherche."
    
    response = "🎵 Voici ce que j'ai trouvé:\n\n"
    
    for i, track in enumerate(tracks, 1):
        response += f"{i}. **{track['name']}** - {track['artist']}\n"
        response += f"   👥 {track['listeners']} auditeurs\n"
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
    
    artists = lastfm_client.search_artist(query, limit=3)
    
    if not artists:
        return "🎤 Désolé, je n'ai trouvé aucun artiste avec ce nom."
    
    response = "🎤 Artistes trouvés:\n\n"
    
    for i, artist in enumerate(artists, 1):
        response += f"{i}. **{artist['name']}**\n"
        response += f"   👥 {artist['listeners']} auditeurs\n"
        response += f"   🔗 {artist['url']}\n\n"
    
    return response


def get_artist_recommendations(artist: str) -> str:
    """
    Obtient des recommandations basées sur un artiste
    
    Args:
        artist (str): Nom de l'artiste
        
    Returns:
        str: Réponse formatée
    """
    
    # D'abord, obtenir les infos de l'artiste
    info = lastfm_client.get_artist_info(artist)
    
    if not info:
        return f"🎤 Désolé, je n'ai pas trouvé l'artiste '{artist}'."
    
    # Ensuite, obtenir les artistes similaires
    similar = lastfm_client.get_similar_artists(artist, limit=5)
    
    if not similar:
        return f"🎤 Pas de recommandations trouvées pour '{artist}'."
    
    response = f"🎤 Artistes similaires à **{info['name']}**:\n\n"
    
    for i, art in enumerate(similar, 1):
        match_percent = int(float(art['match']) * 100)
        response += f"{i}. **{art['name']}** ({match_percent}% similaire)\n"
        response += f"   🔗 {art['url']}\n\n"
    
    return response


def get_recommendations_by_genre(genre: str) -> str:
    """
    Obtient des recommandations pour un genre
    
    Args:
        genre (str): Genre musical (pop, rock, hip-hop, jazz, etc.)
        
    Returns:
        str: Réponse formatée
    """
    
    tracks = lastfm_client.get_top_tracks_by_tag(genre, limit=5)
    
    if not tracks:
        return f"🎵 Désolé, je n'ai pas pu trouver de chansons pour le genre '{genre}'.\n\nEssaie: pop, rock, hip-hop, jazz, electronic, indie, metal, reggae..."
    
    response = f"🎵 Top chansons **{genre}**:\n\n"
    
    for i, track in enumerate(tracks, 1):
        response += f"{i}. **{track['name']}** - {track['artist']}\n"
        response += f"   ▶️ {track['playcount']} écoutes\n"
        response += f"   🔗 {track['url']}\n\n"
    
    return response