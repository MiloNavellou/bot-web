"""
app/games.py - Logique des jeux

Contient la logique pour:
- Deviner un nombre
- Pendu
- Lancer des dés

On gère aussi "l'état du jeu" (les données qui changent pendant le jeu)
"""

import random


# ========== DONNÉES DES JEUX ==========

hangman_words = [
    "python",
    "programmation",
    "robot",
    "intelligence",
    "aventure",
    "mystère",
    "ordinateur",
    "technologie",
    "serveur",
    "internet",
]


# ========== ÉTATS DES JEUX ==========
# On stocke l'état de chaque jeu ici
# Dans un vrai projet, ce serait une base de données!

games_state = {
    'guessing_game': {
        'active': False,
        'number': None,
        'attempts': 0,
        'range': (1, 100)
    },
    'hangman': {
        'active': False,
        'word': None,
        'guessed': [],
        'wrong': 0,
        'max_wrong': 6
    }
}


# ========== JEUX ==========

class GuessingGame:
    """
    Jeu: Deviner un nombre entre 1 et 100
    """
    
    @staticmethod
    def start():
        """Démarre un nouveau jeu"""
        games_state['guessing_game'] = {
            'active': True,
            'number': random.randint(1, 100),
            'attempts': 0,
            'range': (1, 100)
        }
        return "🎯 J'ai pensé à un nombre entre 1 et 100! Devine avec !guess <nombre>"
    
    @staticmethod
    def guess(number):
        """
        Traite une tentative de deviner
        
        Args:
            number (int): Le nombre proposé
            
        Returns:
            dict: {'message': str, 'won': bool, 'won_attempts': int}
        """
        
        state = games_state['guessing_game']
        
        if not state['active']:
            return {'message': "Aucun jeu en cours! Tape !guess pour commencer.", 'won': False}
        
        state['attempts'] += 1
        target = state['number']
        
        # Victoire!
        if number == target:
            state['active'] = False
            return {
                'message': f"🎉 Bravo! Tu as trouvé {target} en {state['attempts']} tentatives!",
                'won': True,
                'won_attempts': state['attempts']
            }
        
        # Trop petit
        elif number < target:
            return {
                'message': f"⬆️ C'est plus grand! (tentative {state['attempts']})",
                'won': False
            }
        
        # Trop grand
        else:
            return {
                'message': f"⬇️ C'est plus petit! (tentative {state['attempts']})",
                'won': False
            }
    
    @staticmethod
    def is_active():
        """Retourne True si un jeu est en cours"""
        return games_state['guessing_game']['active']


class Hangman:
    """
    Jeu: Pendu - Deviner les lettres d'un mot
    """
    
    @staticmethod
    def start():
        """Démarre un nouveau jeu"""
        games_state['hangman'] = {
            'active': True,
            'word': random.choice(hangman_words),
            'guessed': [],
            'wrong': 0,
            'max_wrong': 6
        }
        display = Hangman._get_display()
        return f"👤 Jeu du pendu!\n{display}\nDevine avec !hangman <lettre>"
    
    @staticmethod
    def guess(letter):
        """
        Traite une tentative de deviner une lettre
        
        Args:
            letter (str): La lettre proposée
            
        Returns:
            dict: {'message': str, 'won': bool, 'lost': bool}
        """
        
        state = games_state['hangman']
        
        if not state['active']:
            return {'message': "Aucun jeu en cours! Tape !hangman pour commencer.", 'won': False, 'lost': False}
        
        letter = letter.lower()
        
        # Vérifier que c'est une lettre
        if not letter.isalpha() or len(letter) != 1:
            return {'message': "Propose une lettre valide!", 'won': False, 'lost': False}
        
        # Lettre déjà proposée?
        if letter in state['guessed']:
            display = Hangman._get_display()
            return {
                'message': f"Tu as déjà proposé '{letter}'!\n{display}",
                'won': False,
                'lost': False
            }
        
        # Ajouter la lettre
        state['guessed'].append(letter)
        
        # La lettre est dans le mot?
        if letter not in state['word']:
            state['wrong'] += 1
        
        # Vérifier victoire (toutes les lettres trouvées)
        if all(l in state['guessed'] for l in state['word']):
            state['active'] = False
            return {
                'message': f"🎉 Gagné! Le mot était: **{state['word']}**",
                'won': True,
                'lost': False
            }
        
        # Vérifier défaite (trop d'erreurs)
        if state['wrong'] >= state['max_wrong']:
            state['active'] = False
            return {
                'message': f"💀 Perdu! Le mot était: **{state['word']}**",
                'won': False,
                'lost': True
            }
        
        # Jeu continue
        display = Hangman._get_display()
        return {
            'message': f"{display}\nErreurs: {state['wrong']}/{state['max_wrong']}",
            'won': False,
            'lost': False
        }
    
    @staticmethod
    def _get_display():
        """Affiche le mot avec les lettres devinées"""
        state = games_state['hangman']
        word = state['word']
        guessed = state['guessed']
        display = " ".join([letter if letter in guessed else "_" for letter in word])
        return display
    
    @staticmethod
    def get_status():
        """Retourne le statut du jeu en cours"""
        state = games_state['hangman']
        if not state['active']:
            return None
        
        display = Hangman._get_display()
        return {
            'display': display,
            'wrong': state['wrong'],
            'max_wrong': state['max_wrong']
        }
    
    @staticmethod
    def is_active():
        """Retourne True si un jeu est en cours"""
        return games_state['hangman']['active']


class DiceGame:
    """
    Jeu: Lancer des dés
    """
    
    @staticmethod
    def roll_dice(count=1, sides=6):
        """
        Lance des dés
        
        Args:
            count (int): Nombre de dés (1-10)
            sides (int): Nombre de faces (6, 20, 100, etc.)
            
        Returns:
            str: Résultat du lancer
        """
        
        count = min(max(count, 1), 10)  # Entre 1 et 10
        sides = min(max(sides, 1), 1000)  # Entre 1 et 1000
        
        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls)
        
        if count == 1:
            return f"🎲 Tu as lancé 1d{sides}: {rolls[0]}"
        else:
            return f"🎲 Tu as lancé {count}d{sides}: {rolls} = {total}"
    
    @staticmethod
    def roll_custom(dice_type):
        """
        Lance un dé custom (d20, d100, etc.)
        
        Args:
            dice_type (str): Format "dXX" (ex: "d20", "d100")
            
        Returns:
            str: Résultat du lancer
        """
        
        try:
            if not dice_type.startswith('d'):
                return "Format invalide! Utilise d20, d100, etc."
            
            sides = int(dice_type[1:])
            sides = min(sides, 1000)
            
            roll = random.randint(1, sides)
            return f"⚔️ Jet de {dice_type}: {roll}"
        except:
            return "Format invalide! Utilise d20, d100, etc."


# ========== RACCOURCIS POUR LES JEUX ==========

def start_guessing_game():
    """Démarre le jeu de deviner un nombre"""
    return GuessingGame.start()


def guess_number(number_str):
    """Traite une tentative au jeu de deviner"""
    try:
        number = int(number_str)
        return GuessingGame.guess(number)
    except:
        return {'message': "Propose un nombre valide!"}


def start_hangman():
    """Démarre le jeu du pendu"""
    return Hangman.start()


def guess_letter(letter):
    """Traite une tentative au pendu"""
    return Hangman.guess(letter)


def roll_dice_cmd(args):
    """Traite la commande !dice"""
    if not args:
        return DiceGame.roll_dice(1)
    
    try:
        count = int(args[0])
        return DiceGame.roll_dice(count)
    except:
        return "Format: !dice [nombre] (1-10 dés)"


def roll_custom_cmd(args):
    """Traite la commande !roll"""
    if not args:
        return DiceGame.roll_custom('d20')
    
    return DiceGame.roll_custom(args[0])