#!/bin/bash
# Script para executar o simulador de equilíbrio químico

# Verifica se o streamlit está instalado
if ! command -v streamlit &> /dev/null
then
    echo "Streamlit não encontrado. Instalando dependências..."
    pip install -r requirements.txt
fi

# Executa o simulador
echo "A iniciar o simulador..."
streamlit run app.py
