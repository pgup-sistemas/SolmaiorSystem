#!/usr/bin/env python3
"""
Script de Migração - Aulas Experimentais
Adiciona campos de agendamento à tabela trial_lessons

Execute com: python migrate_trial_lessons.py
"""

from app import create_app, db
from sqlalchemy import text
import sys

def migrate_trial_lessons():
    """Adicionar novos campos à tabela trial_lessons"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Migrando tabela trial_lessons...")
        print("=" * 60)
        
        try:
            # Lista de comandos SQL para adicionar colunas
            commands = [
                "ALTER TABLE trial_lessons ADD COLUMN scheduled_date DATE",
                "ALTER TABLE trial_lessons ADD COLUMN scheduled_time TIME",
                "ALTER TABLE trial_lessons ADD COLUMN assigned_teacher_id INTEGER REFERENCES teachers(id)",
                "ALTER TABLE trial_lessons ADD COLUMN room_id INTEGER REFERENCES rooms(id)",
                "ALTER TABLE trial_lessons ADD COLUMN duration_minutes INTEGER DEFAULT 60",
                "ALTER TABLE trial_lessons ADD COLUMN confirmation_sent BOOLEAN DEFAULT 0",
                "ALTER TABLE trial_lessons ADD COLUMN notes TEXT",
            ]
            
            for cmd in commands:
                try:
                    db.session.execute(text(cmd))
                    field_name = cmd.split("ADD COLUMN ")[1].split()[0]
                    print(f"   ✓ Campo '{field_name}' adicionado")
                except Exception as e:
                    if "duplicate column" in str(e).lower():
                        field_name = cmd.split("ADD COLUMN ")[1].split()[0]
                        print(f"   ⚠ Campo '{field_name}' já existe")
                    else:
                        print(f"   ✗ Erro: {str(e)}")
            
            db.session.commit()
            
            # Criar índice
            print("\n🔍 Criando índice...")
            try:
                db.session.execute(text(
                    "CREATE INDEX IF NOT EXISTS idx_trial_scheduled_date ON trial_lessons(scheduled_date)"
                ))
                db.session.commit()
                print("   ✓ Índice criado")
            except Exception as e:
                print(f"   ⚠ Índice já existe ou erro: {str(e)}")
            
            print("\n" + "=" * 60)
            print("✅ Migração concluída com sucesso!")
            print("\n📊 Novos campos adicionados:")
            print("   • scheduled_date - Data agendada da aula")
            print("   • scheduled_time - Horário agendado")
            print("   • assigned_teacher_id - Professor designado")
            print("   • room_id - Sala da aula")
            print("   • duration_minutes - Duração em minutos")
            print("   • confirmation_sent - Email de confirmação enviado")
            print("   • notes - Observações internas")
            print("\n💡 Acesse: /trial-lessons para usar o novo sistema")
            print("\n⚠️  REINICIE O SERVIDOR para aplicar as mudanças")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erro durante a migração: {str(e)}")
            print("⚠️ O banco de dados foi revertido ao estado anterior.")
            sys.exit(1)


if __name__ == '__main__':
    print("\n🚀 Sistema de Migração - Aulas Experimentais")
    print("=" * 60)
    
    response = input("\n⚠️  Esta operação irá modificar o banco de dados.\nDeseja continuar? (s/N): ")
    
    if response.lower() in ['s', 'sim', 'yes', 'y']:
        migrate_trial_lessons()
    else:
        print("\n❌ Migração cancelada pelo usuário.")
        sys.exit(0)
