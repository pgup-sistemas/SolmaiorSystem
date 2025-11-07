
#!/usr/bin/env python3
"""
Script para corrigir a estrutura da tabela landing_page_content
"""
from app import create_app, db
from sqlalchemy import text, inspect

app = create_app()

def column_exists(table_name, column_name):
    """Verifica se uma coluna existe em uma tabela"""
    try:
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        return column_name in columns
    except Exception as e:
        print(f"Erro ao verificar coluna {column_name}: {e}")
        return False

def table_exists(table_name):
    """Verifica se uma tabela existe"""
    try:
        inspector = inspect(db.engine)
        return table_name in inspector.get_table_names()
    except Exception as e:
        print(f"Erro ao verificar tabela {table_name}: {e}")
        return False

with app.app_context():
    print('=' * 60)
    print('🔧 CORRIGINDO ESTRUTURA DO BANCO DE DADOS')
    print('=' * 60)
    print()
    
    try:
        # 1. Criar todas as tabelas que não existem
        print('📋 Passo 1: Criando tabelas faltantes...')
        db.create_all()
        print('✅ Tabelas criadas/verificadas\n')
        
        # 2. Adicionar colunas faltantes na landing_page_content
        if table_exists('landing_page_content'):
            print('🔄 Passo 2: Verificando landing_page_content...')
            
            # Adicionar background_color
            if not column_exists('landing_page_content', 'background_color'):
                print('  → Adicionando background_color...')
                try:
                    db.session.execute(text(
                        "ALTER TABLE landing_page_content ADD COLUMN background_color VARCHAR(20)"
                    ))
                    db.session.commit()
                    print('  ✅ background_color adicionada')
                except Exception as e:
                    db.session.rollback()
                    print(f'  ⚠ Erro ao adicionar background_color: {e}')
            else:
                print('  ✓ background_color já existe')
            
            # Adicionar text_color
            if not column_exists('landing_page_content', 'text_color'):
                print('  → Adicionando text_color...')
                try:
                    db.session.execute(text(
                        "ALTER TABLE landing_page_content ADD COLUMN text_color VARCHAR(20)"
                    ))
                    db.session.commit()
                    print('  ✅ text_color adicionada')
                except Exception as e:
                    db.session.rollback()
                    print(f'  ⚠ Erro ao adicionar text_color: {e}')
            else:
                print('  ✓ text_color já existe')
            
            print()
        else:
            print('⚠ Tabela landing_page_content não existe, criando...')
            db.create_all()
            print('✅ Tabela criada\n')
        
        # 3. Verificar lesson_schedule
        if table_exists('lesson_schedule'):
            print('🔄 Passo 3: Verificando lesson_schedule...')
            
            lesson_columns = {
                'attendance_confirmed': 'BOOLEAN DEFAULT FALSE',
                'attendance_status': 'VARCHAR(20)',
                'confirmed_by': 'INTEGER',
                'confirmed_at': 'TIMESTAMP',
                'lesson_notes': 'TEXT',
                'lesson_content': 'TEXT',
                'homework_assigned': 'TEXT',
                'student_progress': 'VARCHAR(20)'
            }
            
            for col_name, col_type in lesson_columns.items():
                if not column_exists('lesson_schedule', col_name):
                    print(f'  → Adicionando {col_name}...')
                    try:
                        db.session.execute(text(
                            f"ALTER TABLE lesson_schedule ADD COLUMN {col_name} {col_type}"
                        ))
                        db.session.commit()
                        print(f'  ✅ {col_name} adicionada')
                    except Exception as e:
                        db.session.rollback()
                        if 'already exists' not in str(e).lower():
                            print(f'  ⚠ Erro: {e}')
                else:
                    print(f'  ✓ {col_name} já existe')
            print()
        
        # 4. Verificar payments
        if table_exists('payments'):
            print('🔄 Passo 4: Verificando payments...')
            
            payment_columns = {
                'discount_reason': 'VARCHAR(255)',
                'is_installment': 'BOOLEAN DEFAULT FALSE',
                'installment_number': 'INTEGER',
                'installment_total': 'INTEGER',
                'parent_payment_id': 'INTEGER',
                'stripe_customer_id': 'VARCHAR(255)',
                'stripe_payment_intent_id': 'VARCHAR(255)',
                'stripe_charge_id': 'VARCHAR(255)',
                'stripe_payment_method_id': 'VARCHAR(255)',
                'stripe_status': 'VARCHAR(50)',
                'stripe_client_secret': 'VARCHAR(500)',
                'stripe_webhook_received': 'BOOLEAN DEFAULT FALSE',
                'stripe_error_message': 'TEXT'
            }
            
            for col_name, col_type in payment_columns.items():
                if not column_exists('payments', col_name):
                    print(f'  → Adicionando {col_name}...')
                    try:
                        db.session.execute(text(
                            f"ALTER TABLE payments ADD COLUMN {col_name} {col_type}"
                        ))
                        db.session.commit()
                        print(f'  ✅ {col_name} adicionada')
                    except Exception as e:
                        db.session.rollback()
                        if 'already exists' not in str(e).lower():
                            print(f'  ⚠ Erro: {e}')
                else:
                    print(f'  ✓ {col_name} já existe')
            print()
        
        # 5. Verificar students
        if table_exists('students'):
            print('🔄 Passo 5: Verificando students...')
            
            if not column_exists('students', 'stripe_customer_id'):
                print('  → Adicionando stripe_customer_id...')
                try:
                    db.session.execute(text(
                        "ALTER TABLE students ADD COLUMN stripe_customer_id VARCHAR(255)"
                    ))
                    db.session.commit()
                    print('  ✅ stripe_customer_id adicionada')
                except Exception as e:
                    db.session.rollback()
                    if 'already exists' not in str(e).lower():
                        print(f'  ⚠ Erro: {e}')
            else:
                print('  ✓ stripe_customer_id já existe')
            print()
        
        print('=' * 60)
        print('✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!')
        print('=' * 60)
        print()
        print('Próximo passo: Execute os seguintes comandos:')
        print('  1. python create_admin_user.py')
        print('  2. python update_database.py')
        print()
        
    except Exception as e:
        db.session.rollback()
        print()
        print('=' * 60)
        print('❌ ERRO DURANTE A MIGRAÇÃO')
        print('=' * 60)
        print(f'\nErro: {str(e)}')
        print()
        import traceback
        traceback.print_exc()
