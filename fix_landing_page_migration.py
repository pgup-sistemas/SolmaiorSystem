#!/usr/bin/env python3
"""
Script para corrigir a estrutura da tabela landing_page_content
Versão corrigida - força a criação das colunas
"""
from app import create_app, db
from sqlalchemy import text, inspect

app = create_app()

def column_exists(table_name, column_name):
    """Verifica se uma coluna existe em uma tabela"""
    try:
        with db.engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='{table_name}' 
                AND column_name='{column_name}'
            """))
            return result.fetchone() is not None
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

def add_column_if_not_exists(table_name, column_name, column_type):
    """Adiciona uma coluna se ela não existir"""
    if not column_exists(table_name, column_name):
        print(f'  → Adicionando {column_name}...')
        try:
            with db.engine.connect() as conn:
                conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
                conn.commit()
            print(f'  ✅ {column_name} adicionada com sucesso')
            return True
        except Exception as e:
            print(f'  ❌ Erro ao adicionar {column_name}: {e}')
            return False
    else:
        print(f'  ✓ {column_name} já existe')
        return True

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

        # 2. Verificar e corrigir landing_page_content
        if table_exists('landing_page_content'):
            print('🔄 Passo 2: Corrigindo landing_page_content...')

            # Adicionar background_color
            add_column_if_not_exists('landing_page_content', 'background_color', 'VARCHAR(20)')

            # Adicionar text_color
            add_column_if_not_exists('landing_page_content', 'text_color', 'VARCHAR(20)')

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
                add_column_if_not_exists('lesson_schedule', col_name, col_type)

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
                add_column_if_not_exists('payments', col_name, col_type)

            print()

        # 5. Verificar students
        if table_exists('students'):
            print('🔄 Passo 5: Verificando students...')

            add_column_if_not_exists('students', 'stripe_customer_id', 'VARCHAR(255)')

            print()

        print('=' * 60)
        print('✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!')
        print('=' * 60)
        print()
        print('Você pode agora acessar a aplicação normalmente.')
        print()

    except Exception as e:
        print()
        print('=' * 60)
        print('❌ ERRO DURANTE A MIGRAÇÃO')
        print('=' * 60)
        print(f'\nErro: {str(e)}')
        print()
        import traceback
        traceback.print_exc()