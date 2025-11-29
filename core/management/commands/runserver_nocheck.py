#!/usr/bin/env python
"""
Management command para rodar servidor sem system checks.
"""
import os
import sys
from django.core.management.commands.runserver import Command as RunserverCommand

class Command(RunserverCommand):
    help = 'Inicia o servidor de desenvolvimento sem system checks'
    
    def run(self, **options):
        # Desabilitar completamente system checks
        os.environ['DJANGO_SKIP_SYSTEM_CHECKS'] = '1'
        
        # Monkey patch para garantir que nenhum check seja executado
        from django.core.checks import registry
        registry._registry = {}
        
        from django.core.checks import run_checks
        def dummy_checks(*args, **kwargs):
            return []
        
        import django.core.checks
        django.core.checks.run_checks = dummy_checks
        
        # Chamar o runserver original
        super().run(**options)