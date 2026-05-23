"""
app/validators.py - Validation des données

Contient toutes les fonctions pour valider les inputs.
C'est CRUCIAL pour la sécurité!

"Never trust user input" - dit le proverbe de la sécurité informatique.
"""

import re
from typing import Tuple


# ========== CONSTANTES DE VALIDATION ==========

MAX_MESSAGE_LENGTH = 500  # Longueur max d'un message
MIN_MESSAGE_LENGTH = 1    # Longueur min d'un message
MAX_COMMAND_ARGS = 10     # Nombre max d'arguments


# ========== FONCTIONS DE VALIDATION ==========

def is_valid_message(message: str) -> Tuple[bool, str]:
    """
    Valide un message utilisateur
    
    Vérifie:
    - Que ce n'est pas vide
    - Que ce n'est pas trop long
    - Qu'il ne contient pas de caractères malveillants
    
    Args:
        message (str): Le message à valider
        
    Returns:
        Tuple[bool, str]: (est_valide, message_d_erreur)
    """
    
    # Vérifier que ce n'est pas None
    if message is None:
        return False, "Message vide"
    
    # Convertir en string si ce n'est pas le cas
    message = str(message).strip()
    
    # Vérifier la longueur
    if len(message) < MIN_MESSAGE_LENGTH:
        return False, "Message vide"
    
    if len(message) > MAX_MESSAGE_LENGTH:
        return False, f"Message trop long (max {MAX_MESSAGE_LENGTH} caractères)"
    
    # Vérifier qu'il ne contient que des caractères valides
    # On autorise: lettres, chiffres, espaces, ponctuation, emojis
    # On refuse: caractères de contrôle, null bytes, etc.
    
    # Vérifier les caractères de contrôle (invisibles et dangereux)
    for char in message:
        if ord(char) < 32 and char not in '\n\t':  # Autoriser newline et tab seulement
            return False, "Message contient des caractères invalides"
    
    return True, ""


def sanitize_message(message: str) -> str:
    """
    Nettoie un message (supprime les caractères dangereux)
    
    Args:
        message (str): Le message à nettoyer
        
    Returns:
        str: Le message nettoyé
    """
    
    # Supprimer les caractères de contrôle
    message = ''.join(char for char in message if ord(char) >= 32 or char in '\n\t')
    
    # Limiter la longueur
    message = message[:MAX_MESSAGE_LENGTH]
    
    return message.strip()


def is_valid_number(value: str, min_val: int = None, max_val: int = None) -> Tuple[bool, int]:
    """
    Valide qu'une string est un nombre entier
    
    Args:
        value (str): La valeur à valider
        min_val (int): Valeur minimale (optionnel)
        max_val (int): Valeur maximale (optionnel)
        
    Returns:
        Tuple[bool, int]: (est_valide, nombre)
    """
    
    try:
        number = int(value)
        
        # Vérifier les limites
        if min_val is not None and number < min_val:
            return False, number
        
        if max_val is not None and number > max_val:
            return False, number
        
        return True, number
    
    except (ValueError, TypeError):
        return False, 0


def is_valid_letter(value: str) -> Tuple[bool, str]:
    """
    Valide qu'une string est une seule lettre
    
    Args:
        value (str): La valeur à valider
        
    Returns:
        Tuple[bool, str]: (est_valide, lettre)
    """
    
    value = str(value).lower().strip()
    
    # Vérifier que c'est une seule lettre
    if len(value) != 1 or not value.isalpha():
        return False, ""
    
    return True, value


def is_valid_command(command: str) -> Tuple[bool, str, list]:
    """
    Valide une commande
    
    Args:
        command (str): La commande à valider (ex: "!joke 5 test")
        
    Returns:
        Tuple[bool, str, list]: (est_valide, cmd, args)
    """
    
    command = str(command).strip()
    
    # Vérifier que ça commence par !
    if not command.startswith('!'):
        return False, "", []
    
    parts = command.split()
    cmd = parts[0].lower()
    args = parts[1:]
    
    # Vérifier qu'il y a pas trop d'arguments
    if len(args) > MAX_COMMAND_ARGS:
        return False, cmd, []
    
    # Vérifier que la commande ne contient que des caractères valides
    # Pattern: !nomdecommande (lettres et chiffres seulement)
    if not re.match(r'^![a-z0-9]+$', cmd):
        return False, cmd, []
    
    return True, cmd, args


def validate_request_data(data: dict) -> Tuple[bool, str, str]:
    """
    Valide les données reçues d'une requête API
    
    Args:
        data (dict): Les données JSON reçues
        
    Returns:
        Tuple[bool, str, str]: (est_valide, message_d_erreur, message_propre)
    """
    
    # Vérifier que data est un dict
    if not isinstance(data, dict):
        return False, "Données invalides (pas un objet JSON)", ""
    
    # Récupérer le message
    message = data.get('message', '')
    
    if not isinstance(message, str):
        return False, "Le message doit être un texte", ""
    
    # Valider le message
    is_valid, error = is_valid_message(message)
    if not is_valid:
        return False, error, ""
    
    # Nettoyer le message
    clean_message = sanitize_message(message)
    
    return True, "", clean_message


# ========== TESTS DE SÉCURITÉ ==========

def test_xss_injection(text: str) -> bool:
    """
    Détecte les tentatives simples de XSS (injection de code HTML/JS)
    
    Args:
        text (str): Le texte à vérifier
        
    Returns:
        bool: True si c'est une tentative de XSS
    """
    
    xss_patterns = [
        r'<script',
        r'javascript:',
        r'on\w+\s*=',  # onclick=, onload=, etc.
        r'<iframe',
        r'<object',
        r'<embed',
    ]
    
    text_lower = text.lower()
    
    for pattern in xss_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False


def test_sql_injection(text: str) -> bool:
    """
    Détecte les tentatives simples de SQL injection
    
    Args:
        text (str): Le texte à vérifier
        
    Returns:
        bool: True si c'est une tentative de SQL injection
    """
    
    sql_patterns = [
        r"'\s*OR\s*'",
        r"'\s*OR\s*1\s*=\s*1",
        r"DROP\s+TABLE",
        r"DELETE\s+FROM",
        r"UNION\s+SELECT",
    ]
    
    text_upper = text.upper()
    
    for pattern in sql_patterns:
        if re.search(pattern, text_upper):
            return True
    
    return False