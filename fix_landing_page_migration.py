
#!/usr/bin/env python3
"""
Script para corrigir a estrutura da tabela landing_page_content
"""
from app import create_app, db
from sqlalchemy import text, inspect

app = create_app()

def column_exists(table_name, column_name):
    """Verifica se uma coluna existe em uma tabela"""
    inspector = inspect(db.engine)
    try:
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        return column_name in columns
    except Exception:
        return False

def table_exists(table_name):
    """Verifica se uma tabela existe"""
    inspector = inspect(db.engine)
    return table_name in inspector.get_table_names()

with app.app_context():
    print('🔧 Corrigindo estrutura do banco de dados...\n')
    
    try:
        # 1. Criar todas as tabelas que não existem
        print('📋 Criando tabelas faltantes...')
        db.create_all()
        print('✅ Tabelas criadas\n')
        
        # 2. Adicionar colunas faltantes na landing_page_content
        if table_exists('landing_page_content'):
            print('🔄 Adicionando colunas faltantes em landing_page_content...')
            
            columns_to_add = [
                ('background_color', 'VARCHAR(20)'),
                ('text_color', 'VARCHAR(20)')
            ]
            
            for col_name, col_type in columns_to_add:
                if not column_exists('landing_page_content', col_name):
                    try:
                        db.session.execute(text(
                            f"ALTER TABLE landing_page_content ADD COLUMN {col_name} {col_type}"
                        ))
                        print(f'  ✓ Coluna {col_name} adicionada')
                    except Exception as e:
                        print(f'  ⚠ Coluna {col_name}: {str(e)}')
                else:
                    print(f'  ✓ Coluna {col_name} já existe')
            
            db.session.commit()
            print('✅ Estrutura da landing_page_content corrigida\n')
        
        # 3. Adicionar colunas faltantes em outras tabelas
        print('🔄 Verificando outras tabelas...')
        
        # lesson_schedule
        if table_exists('lesson_schedule'):
            lesson_columns = [
                ('attendance_confirmed', 'BOOLEAN DEFAULT FALSE'),
                ('attendance_status', 'VARCHAR(20)'),
                ('confirmed_by', 'INTEGER'),
                ('confirmed_at', 'TIMESTAMP'),
                ('lesson_notes', 'TEXT'),
                ('lesson_content', 'TEXT'),
                ('homework_assigned', 'TEXT'),
                ('student_progress', 'VARCHAR(20)')
            ]
            
            for col_name, col_type in lesson_columns:
                if not column_exists('lesson_schedule', col_name):
                    try:
                        db.session.execute(text(
                            f"ALTER TABLE lesson_schedule ADD COLUMN {col_name} {col_type}"
                        ))
                        print(f'  ✓ lesson_schedule.{col_name} adicionada')
                    except Exception as e:
                        if 'already exists' not in str(e):
                            print(f'  ⚠ lesson_schedule.{col_name}: {str(e)}')
        
        # payments
        if table_exists('payments'):
            payment_columns = [
                ('discount_reason', 'VARCHAR(255)'),
                ('is_installment', 'BOOLEAN DEFAULT FALSE'),
                ('installment_number', 'INTEGER'),
                ('installment_total', 'INTEGER'),
                ('parent_payment_id', 'INTEGER'),
                ('stripe_customer_id', 'VARCHAR(255)'),
                ('stripe_payment_intent_id', 'VARCHAR(255)'),
                ('stripe_charge_id', 'VARCHAR(255)'),
                ('stripe_payment_method_id', 'VARCHAR(255)'),
                ('stripe_status', 'VARCHAR(50)'),
                ('stripe_client_secret', 'VARCHAR(500)'),
                ('stripe_webhook_received', 'BOOLEAN DEFAULT FALSE'),
                ('stripe_error_message', 'TEXT')
            ]
            
            for col_name, col_type in payment_columns:
                if not column_exists('payments', col_name):
                    try:
                        db.session.execute(text(
                            f"ALTER TABLE payments ADD COLUMN {col_name} {col_type}"
                        ))
                        print(f'  ✓ payments.{col_name} adicionada')
                    except Exception as e:
                        if 'already exists' not in str(e):
                            print(f'  ⚠ payments.{col_name}: {str(e)}')
        
        # students
        if table_exists('students'):
            if not column_exists('students', 'stripe_customer_id'):
                try:
                    db.session.execute(text(
                        "ALTER TABLE students ADD COLUMN stripe_customer_id VARCHAR(255)"
                    ))
                    print('  ✓ students.stripe_customer_id adicionada')
                except Exception as e:
                    if 'already exists' not in str(e):
                        print(f'  ⚠ students.stripe_customer_id: {str(e)}')
        
        db.session.commit()
        print('\n✅ Migração do banco de dados concluída com sucesso!')
        
    except Exception as e:
        db.session.rollback()
        print(f'\n❌ Erro durante a migração: {str(e)}')
        import traceback
        traceback.print_exc()
