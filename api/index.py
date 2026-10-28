"""
Handler Serverless para Deploy na Vercel
Permite que os endpoints de autenticação e colaboradores rodem na infraestrutura da Vercel.
"""
import os
import sys

# Adiciona a raiz do projeto ao path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.server import ApiColaboradorHandler


class handler(ApiColaboradorHandler):
    """Handler serverless compatível com a especificação da Vercel."""
    pass
