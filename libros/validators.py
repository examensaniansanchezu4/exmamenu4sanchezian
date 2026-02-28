from django.core.exceptions import ValidationError
import re


def validar_isbn(value):
    """Validar formato ISBN-10 o ISBN-13"""
    isbn = re.sub(r'[\s-]', '', value)
    
    if len(isbn) not in [10, 13]:
        raise ValidationError(
            'ISBN debe tener 10 o 13 dígitos'
        )
    
    if not isbn.isdigit():
        raise ValidationError(
            'ISBN debe contener solo dígitos'
        )
    
    return isbn


def prevenir_sql_injection(value):
    """Prevenir SQL Injection básico"""
    patrones_peligrosos = [
        r'\bDROP\b', r'\bDELETE\b', r'\bUPDATE\b',
        r'\bINSERT\b', r'\bSELECT\b', r';--', 
        r"'OR'1'='1", r'\bUNION\b'
    ]
    
    for patron in patrones_peligrosos:
        if re.search(patron, value, re.IGNORECASE):
            raise ValidationError(
                'Entrada contiene caracteres no permitidos'
            )
    
    return value


def sanitizar_html(value):
    """Eliminar tags HTML peligrosos"""
    # Remover scripts
    value = re.sub(r']*>.*?', '', value, flags=re.DOTALL | re.IGNORECASE)
    
    # Remover eventos JavaScript
    value = re.sub(r'on\w+\s*=\s*["\'].*?["\']', '', value, flags=re.IGNORECASE)
    
    # Remover tags HTML básicos (opcional)
    value = re.sub(r'<[^>]+>', '', value)
    
    return value.strip()


def validar_password_fuerte(value):
    """Validar contraseña fuerte"""
    if len(value) < 8:
        raise ValidationError('La contraseña debe tener al menos 8 caracteres')
    
    if not re.search(r'[A-Z]', value):
        raise ValidationError('Debe contener al menos una mayúscula')
    
    if not re.search(r'[a-z]', value):
        raise ValidationError('Debe contener al menos una minúscula')
    
    if not re.search(r'\d', value):
        raise ValidationError('Debe contener al menos un número')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError('Debe contener al menos un carácter especial')
    
    return value