"""
app/bot_logic.py - Logique du bot

Contient toutes les fonctions qui font répondre le bot.
On organise tout ici pour que ce soit lisible et réutilisable.
"""

import random
from app.games import (
    start_guessing_game, guess_number, start_hangman, guess_letter,
    roll_dice_cmd, roll_custom_cmd, GuessingGame, Hangman
)


# ========== DATA ==========
# Listes de réponses possibles

jokes = [
    "Pourquoi les plongeurs plongent-ils toujours en arrière ? Parce que s'ils plongeaient en avant, ils tombent dans le bateau !",
    "Quel est le comble pour un électricien ? De ne pas être au courant !",
    "Pourquoi les poissons n'aiment pas jouer au tennis ? Parce qu'ils ont peur du filet !",
    "Comment appelle-t-on un chat tombé dans un pot de peinture le jour de Noël ? Un chat-peint de Noël !",
]

quotes = [
    "La vie est 10% ce qui t'arrive et 90% comment tu réagis.",
    "Le seul moyen de faire du bon travail est d'aimer ce que tu fais.",
    "Sois toi-même, tous les autres sont déjà pris.",
]

magic_8_ball_answers = [
    "Oui, c'est certain.",
    "Non, absolument pas.",
    "Les signes pointent vers oui.",
    "Pas maintenant, réessaye plus tard.",
    "C'est très incertain.",
    "Peut-être... qui sait ?",
]

normal_responses = [
    "C'est intéressant! Peux-tu en dire plus?",
    "Ah oui? Et qu'est-ce que tu en penses?",
    "Cool! Je suis d'accord avec toi.",
    "Hmm, c'est une bonne observation!",
]


# ========== FONCTIONS DE RÉPONSE ==========

def get_joke():
    """Retourne une blague aléatoire"""
    return f"😂 {random.choice(jokes)}"


def get_quote():
    """Retourne une citation aléatoire"""
    return f"✨ {random.choice(quotes)}"


def get_magic_8_ball():
    """Retourne une réponse magique aléatoire"""
    return f"🔮 {random.choice(magic_8_ball_answers)}"


def get_normal_response(message):
    """
    Retourne une réponse normale basée sur le message
    
    Args:
        message (str): Le message de l'utilisateur
        
    Returns:
        str: La réponse du bot
    """
    
    # Vérifier si c'est un salut
    if any(word in message.lower() for word in ['salut', 'bonjour', 'hello', 'coucou']):
        return "Salut! 👋 Comment ça va? Besoin d'aide?"
    
    # Vérifier si c'est un merci
    elif any(word in message.lower() for word in ['merci', 'thx', 'thanks']):
        return "De rien! 😊 C'est mon plaisir!"
    
    # Si c'est une question
    elif '?' in message:
        return "Bonne question! Tape !8ball si tu veux une réponse magique 🔮"
    
    # Sinon, réponse générique aléatoire
    else:
        return random.choice(normal_responses)


def handle_command(command):
    """
    Gère les commandes (commence par !)
    
    Args:
        command (str): La commande tapée par l'utilisateur (ex: "!joke")
        
    Returns:
        str: La réponse du bot
    """
    
    parts = command.lower().split()
    cmd = parts[0]  # Récupère la première partie (ex: "!joke")
    args = parts[1:] if len(parts) > 1 else []  # Arguments supplémentaires
    
    if cmd == '!joke':
        return get_joke()
    
    elif cmd == '!quote':
        return get_quote()
    
    elif cmd == '!8ball':
        return get_magic_8_ball()
    
    elif cmd == '!dice':
        return roll_dice_cmd(args)
    
    elif cmd == '!roll':
        return roll_custom_cmd(args)
    
    elif cmd == '!guess':
        # Si pas d'argument, démarre un nouveau jeu
        if not args:
            return start_guessing_game()
        # Sinon, traite une tentative
        else:
            result = guess_number(args[0])
            return result['message']
    
    elif cmd == '!hangman':
        # Si pas d'argument, démarre un nouveau jeu
        if not args:
            return start_hangman()
        # Sinon, traite une tentative
        else:
            result = guess_letter(args[0])
            return result['message']
    
    elif cmd == '!help':
        help_text = """📚 Commandes disponibles:
!joke - Une blague aléatoire
!quote - Une citation inspirante
!8ball - La boule de cristal magique
!dice [n] - Lance n dés (1-10)
!roll [type] - Jet de dé (d20, d100, etc.)
!guess [nombre] - Jeu: deviner un nombre
!hangman [lettre] - Jeu du pendu
!help - Affiche cette aide"""
        return help_text
    
    else:
        return "🤔 Commande inconnue. Tape !help pour voir les commandes disponibles."


def process_message(message):
    """
    Traite un message de l'utilisateur et retourne la réponse du bot
    
    C'est la fonction PRINCIPALE qu'on va appeler depuis les routes.
    
    Args:
        message (str): Le message de l'utilisateur
        
    Returns:
        str: La réponse du bot
    """
    
    message = message.strip()
    
    if not message:
        return "Euh... tu as rien écrit! 😄"
    
    # Si c'est une commande (commence par !)
    if message.startswith('!'):
        return handle_command(message)
    
    # Sinon, réponse normale
    else:
        return get_normal_response(message)