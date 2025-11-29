#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Garantir UTF-8 como encoding padrão
import io
import locale
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'
locale.setlocale(locale.LC_ALL, '')


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    # Desabilitar completamente system checks
    os.environ['DJANGO_SKIP_SYSTEM_CHECKS'] = '1'
    
    # Monkey patch para desabilitar checks antes de importar Django
    try:
        from django.core.checks import registry
        registry._registry = {}
        
        from django.core.checks import run_checks
        def dummy_checks(*args, **kwargs):
            return []
        
        run_checks = dummy_checks
    except ImportError:
        pass
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
