#!/usr/bin/env python3
"""
Script de Correção Rápida do Banco de Dados
Adiciona as colunas que estão faltando
"""

from app import create_app, db
from sqlalchemy import text

def fix_database():
    app = create_app()
    
    with app.app_context():
        print("🔧 Corrigindo banco de dados...")
        
        try:
            # Lista de comandos SQL para adicionar colunas faltantes
            commands = [
                # lesson_schedule
                "ALTER TABLE lesson_schedule ADD COLUMN attendance_status VARCHAR(20)",
                "ALTER TABLE lesson_schedule ADD COLUMN confirmed_by INTEGER",
                "ALTER TABLE lesson_schedule ADD COLUMN confirmed_at DATETIME",
                "ALTER TABLE lesson_schedule ADD COLUMN lesson_notes TEXT",
                "ALTER TABLE lesson_schedule ADD COLUMN lesson_content TEXT",
                "ALTER TABLE lesson_schedule ADD COLUMN homework_assigned TEXT",
                "ALTER TABLE lesson_schedule ADD COLUMN student_progress VARCHAR(20)",
                
                # payments
                "ALTER TABLE payments ADD COLUMN discount_reason VARCHAR(255)",
                "ALTER TABLE payments ADD COLUMN is_installment BOOLEAN DEFAULT 0",
                "ALTER TABLE payments ADD COLUMN installment_number INTEGER",
                "ALTER TABLE payments ADD COLUMN installment_total INTEGER",
                "ALTER TABLE payments ADD COLUMN parent_payment_id INTEGER",
            ]
            
            for cmd in commands:
                try:
                    db.session.execute(text(cmd))
                    print(f"✓ {cmd[:50]}...")
                except Exception as e:
                    if "duplicate column" in str(e).lower():
                        print(f"⚠ Coluna já existe")
                    else:
                        print(f"⚠ Erro: {str(e)}")
            
            db.session.commit()
            
            # Criar tabelas novas
            print("\n📋 Criando novas tabelas...")
            db.create_all()
            
            print("\n✅ Banco de dados corrigido!")
            print("\nAGORA REINICIE O SERVIDOR:")
            print("  1. Pare o servidor (Ctrl+C)")
            print("  2. Execute: python app.py")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erro: {str(e)}")

if __name__ == '__main__':
    fix_database()
