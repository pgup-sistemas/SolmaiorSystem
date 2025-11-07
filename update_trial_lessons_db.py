#!/usr/bin/env python3
"""
Script para atualizar tabela de Trial Lessons com novos campos de confirmação
"""

import sys
from app import create_app, db
from sqlalchemy import text, inspect

def update_trial_lessons_table():
    """Adicionar novos campos à tabela trial_lessons"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Atualizando tabela trial_lessons...")

            inspector = inspect(db.engine)
            try:
                existing_columns = {col["name"] for col in inspector.get_columns("trial_lessons")}
            except Exception as e:
                print(f"❌ Não foi possível inspecionar a tabela trial_lessons: {str(e)}")
                sys.exit(1)

            is_sqlite = db.engine.dialect.name == "sqlite"

            new_columns = [
                {
                    "name": "confirmation_token",
                    "default_type": "VARCHAR(100)",
                    "sqlite_type": "TEXT",
                    "unique_index": "idx_trial_confirmation_token"
                },
                {
                    "name": "user_confirmed",
                    "default_type": "BOOLEAN DEFAULT FALSE",
                    "sqlite_type": "INTEGER DEFAULT 0"
                },
                {
                    "name": "user_confirmed_at",
                    "default_type": "DATETIME",
                    "sqlite_type": "DATETIME"
                },
                {
                    "name": "user_declined",
                    "default_type": "BOOLEAN DEFAULT FALSE",
                    "sqlite_type": "INTEGER DEFAULT 0"
                },
                {
                    "name": "user_declined_at",
                    "default_type": "DATETIME",
                    "sqlite_type": "DATETIME"
                },
                {
                    "name": "reminder_sent",
                    "default_type": "BOOLEAN DEFAULT FALSE",
                    "sqlite_type": "INTEGER DEFAULT 0"
                },
                {
                    "name": "reminder_sent_at",
                    "default_type": "DATETIME",
                    "sqlite_type": "DATETIME"
                },
            ]

            for column in new_columns:
                column_name = column["name"]
                column_type = column["sqlite_type"] if is_sqlite else column["default_type"]

                if column_name in existing_columns:
                    print(f"  ⏭️  Coluna '{column_name}' já existe")
                    continue

                try:
                    db.session.execute(text(
                        f"ALTER TABLE trial_lessons ADD COLUMN {column_name} {column_type}"
                    ))
                    print(f"  ✅ Coluna '{column_name}' adicionada")

                    unique_index = column.get("unique_index")
                    if unique_index:
                        db.session.execute(text(
                            f"CREATE UNIQUE INDEX IF NOT EXISTS {unique_index} ON trial_lessons ({column_name})"
                        ))
                        print(f"     ↳ Índice único '{unique_index}' criado")

                except Exception as e:
                    print(f"  ⚠️  Erro ao adicionar coluna '{column_name}': {str(e)}")

            db.session.commit()
            print("\n✅ Atualização concluída com sucesso!")
            print("\n📋 Novos recursos disponíveis:")
            print("   • Confirmação do usuário via link")
            print("   • Recusa de agendamento")
            print("   • Sistema de lembretes")
            print("   • Tokens únicos para segurança")

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erro ao atualizar banco de dados: {str(e)}")
            sys.exit(1)


if __name__ == '__main__':
    print("=" * 60)
    print("ATUALIZAÇÃO: Sistema de Aulas Experimentais")
    print("=" * 60)
    print()
    
    response = input("Deseja atualizar o banco de dados? (s/n): ")
    
    if response.lower() in ['s', 'sim', 'y', 'yes']:
        update_trial_lessons_table()
    else:
        print("❌ Operação cancelada.")
