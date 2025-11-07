#!/usr/bin/env python3
"""
Script para executar tarefas automatizadas
Pode ser agendado via cron ou usado manualmente

Exemplos:
  python run_tasks.py daily     # Executar tarefas diárias
  python run_tasks.py hourly    # Executar tarefas horárias
  python run_tasks.py all       # Executar todas as tarefas
"""

import sys
from app import create_app
from app.tasks import run_daily_tasks, run_hourly_tasks

def main():
    app = create_app()
    
    with app.app_context():
        if len(sys.argv) < 2:
            print("Uso: python run_tasks.py [daily|hourly|all]")
            sys.exit(1)
        
        task_type = sys.argv[1].lower()
        
        if task_type == 'daily':
            print("🔄 Executando tarefas diárias...")
            results = run_daily_tasks()
            print(f"✅ Concluído: {results}")
        
        elif task_type == 'hourly':
            print("🔄 Executando tarefas horárias...")
            results = run_hourly_tasks()
            print(f"✅ Concluído: {results}")
        
        elif task_type == 'all':
            print("🔄 Executando todas as tarefas...")
            daily_results = run_daily_tasks()
            hourly_results = run_hourly_tasks()
            print(f"✅ Tarefas diárias: {daily_results}")
            print(f"✅ Tarefas horárias: {hourly_results}")
        
        else:
            print(f"❌ Tipo de tarefa inválido: {task_type}")
            print("Uso: python run_tasks.py [daily|hourly|all]")
            sys.exit(1)

if __name__ == '__main__':
    main()
