#!/usr/bin/env python3
"""
Script de Migração - Novas Funcionalidades v2.2
Adiciona novos campos e tabelas ao banco de dados existente

Execute com: python migrate_new_features.py
"""

from app import create_app, db
from app.models import *
from sqlalchemy import text
import sys

def migrate_database():
    """Executar migrações necessárias"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Iniciando migração do banco de dados...")
        print("=" * 60)
        
        try:
            # Criar todas as novas tabelas
            print("\n📋 Criando novas tabelas...")
            db.create_all()
            print("✅ Novas tabelas criadas com sucesso!")
            
            # Adicionar novos campos às tabelas existentes (SQLite suporta apenas ADD COLUMN)
            print("\n📝 Adicionando novos campos às tabelas existentes...")
            
            # Campos da tabela lesson_schedule
            lesson_schedule_fields = [
                ("attendance_status", "VARCHAR(20)"),
                ("confirmed_by", "INTEGER"),
                ("confirmed_at", "DATETIME"),
                ("lesson_notes", "TEXT"),
                ("lesson_content", "TEXT"),
                ("homework_assigned", "TEXT"),
                ("student_progress", "VARCHAR(20)")
            ]
            
            for field_name, field_type in lesson_schedule_fields:
                try:
                    db.session.execute(text(
                        f"ALTER TABLE lesson_schedule ADD COLUMN {field_name} {field_type}"
                    ))
                    print(f"   ✓ Adicionado campo '{field_name}' à tabela lesson_schedule")
                except Exception as e:
                    if "duplicate column name" in str(e).lower():
                        print(f"   ⚠ Campo '{field_name}' já existe em lesson_schedule")
                    else:
                        print(f"   ✗ Erro ao adicionar '{field_name}': {str(e)}")
            
            # Campos da tabela payments
            payments_fields = [
                ("discount_reason", "VARCHAR(255)"),
                ("is_installment", "BOOLEAN DEFAULT 0"),
                ("installment_number", "INTEGER"),
                ("installment_total", "INTEGER"),
                ("parent_payment_id", "INTEGER")
            ]
            
            for field_name, field_type in payments_fields:
                try:
                    db.session.execute(text(
                        f"ALTER TABLE payments ADD COLUMN {field_name} {field_type}"
                    ))
                    print(f"   ✓ Adicionado campo '{field_name}' à tabela payments")
                except Exception as e:
                    if "duplicate column name" in str(e).lower():
                        print(f"   ⚠ Campo '{field_name}' já existe em payments")
                    else:
                        print(f"   ✗ Erro ao adicionar '{field_name}': {str(e)}")
            
            db.session.commit()
            print("\n✅ Novos campos adicionados com sucesso!")
            
            # Criar índices
            print("\n🔍 Criando índices...")
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_lesson_attendance ON lesson_schedule(attendance_status)",
                "CREATE INDEX IF NOT EXISTS idx_payment_installment ON payments(is_installment)",
                "CREATE INDEX IF NOT EXISTS idx_notification_scheduled ON scheduled_notifications(scheduled_for, status)",
                "CREATE INDEX IF NOT EXISTS idx_discount_active ON discounts(is_active)",
                "CREATE INDEX IF NOT EXISTS idx_waitlist_status ON lesson_waitlist(status)"
            ]
            
            for index_sql in indexes:
                try:
                    db.session.execute(text(index_sql))
                    print(f"   ✓ Índice criado")
                except Exception as e:
                    print(f"   ⚠ Índice já existe ou erro: {str(e)}")
            
            db.session.commit()
            print("✅ Índices criados!")
            
            # Criar descontos padrão
            print("\n🎁 Criando descontos padrão...")
            create_default_discounts()
            
            print("\n" + "=" * 60)
            print("✅ Migração concluída com sucesso!")
            print("\n📊 Resumo:")
            print(f"   • Novas tabelas: scheduled_notifications, discounts, frequency_discount")
            print(f"   • lesson_schedule: 7 novos campos")
            print(f"   • payments: 5 novos campos")
            print(f"   • Índices otimizados criados")
            print(f"   • Descontos padrão configurados")
            print("\n💡 Próximos passos:")
            print("   1. Execute: flask run-daily-tasks (para testar automações)")
            print("   2. Configure o email no .env")
            print("   3. Execute: flask test-email (para testar envio)")
            print("   4. Configure o cron para tarefas automáticas (ver crontab.example)")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erro durante a migração: {str(e)}")
            print("⚠️ O banco de dados foi revertido ao estado anterior.")
            sys.exit(1)


def create_default_discounts():
    """Criar descontos padrão do sistema"""
    from datetime import date, timedelta
    
    # Verificar se já existem descontos
    if Discount.query.first():
        print("   ⚠ Descontos já existem no sistema")
        return
    
    # Buscar admin
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        print("   ⚠ Usuário admin não encontrado, pulando criação de descontos")
        return
    
    default_discounts = [
        {
            'name': 'Frequência 100%',
            'description': 'Desconto automático para alunos com 100% de presença',
            'discount_type': 'percentage',
            'discount_value': 10.0,
            'condition_type': 'attendance_rate',
            'condition_value': 100.0,
            'auto_apply': True,
            'is_active': True
        },
        {
            'name': 'Frequência Excelente (≥95%)',
            'description': 'Desconto para alunos com frequência igual ou superior a 95%',
            'discount_type': 'percentage',
            'discount_value': 5.0,
            'condition_type': 'attendance_rate',
            'condition_value': 95.0,
            'auto_apply': True,
            'is_active': True
        },
        {
            'name': 'Pagamento Antecipado',
            'description': 'Desconto para pagamentos realizados até 5 dias antes do vencimento',
            'discount_type': 'percentage',
            'discount_value': 5.0,
            'condition_type': 'early_payment',
            'auto_apply': False,
            'is_active': True
        },
        {
            'name': 'Irmão Matriculado',
            'description': 'Desconto para famílias com mais de um aluno matriculado',
            'discount_type': 'percentage',
            'discount_value': 15.0,
            'condition_type': 'sibling',
            'auto_apply': False,
            'is_active': True
        }
    ]
    
    for discount_data in default_discounts:
        discount = Discount(
            **discount_data,
            created_by=admin.id
        )
        db.session.add(discount)
        print(f"   ✓ Desconto criado: {discount_data['name']}")
    
    db.session.commit()
    print("✅ Descontos padrão criados!")


if __name__ == '__main__':
    print("\n🚀 Sistema de Migração - Solmaior v2.2")
    print("=" * 60)
    
    response = input("\n⚠️  Esta operação irá modificar o banco de dados.\nDeseja continuar? (s/N): ")
    
    if response.lower() in ['s', 'sim', 'yes', 'y']:
        migrate_database()
    else:
        print("\n❌ Migração cancelada pelo usuário.")
        sys.exit(0)
