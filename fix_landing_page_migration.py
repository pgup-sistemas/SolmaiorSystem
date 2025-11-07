
#!/usr/bin/env python3
"""
Script definitivo para corrigir estrutura do banco de dados
Versão robusta - garante todas as colunas e tipos corretos
"""
from app import create_app, db
from sqlalchemy import text, inspect
import traceback

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
        print(f"❌ Erro ao verificar coluna {column_name}: {e}")
        return False

def table_exists(table_name):
    """Verifica se uma tabela existe"""
    try:
        inspector = inspect(db.engine)
        return table_name in inspector.get_table_names()
    except Exception as e:
        print(f"❌ Erro ao verificar tabela {table_name}: {e}")
        return False

def add_column_safe(table_name, column_name, column_type):
    """Adiciona uma coluna de forma segura"""
    if column_exists(table_name, column_name):
        print(f'  ✓ {column_name} já existe')
        return True
    
    print(f'  → Adicionando {column_name}...')
    try:
        with db.engine.begin() as conn:
            sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            conn.execute(text(sql))
        print(f'  ✅ {column_name} adicionada')
        return True
    except Exception as e:
        print(f'  ❌ Erro ao adicionar {column_name}: {e}')
        return False

with app.app_context():
    print('=' * 70)
    print('🔧 CORREÇÃO DEFINITIVA DO BANCO DE DADOS')
    print('=' * 70)
    print()

    try:
        # 1. Criar todas as tabelas que não existem
        print('📋 Passo 1: Criando tabelas faltantes...')
        db.create_all()
        print('✅ Tabelas verificadas/criadas\n')

        # 2. LANDING PAGE CONTENT - Prioridade máxima
        if table_exists('landing_page_content'):
            print('🔄 Passo 2: Corrigindo landing_page_content...')
            
            add_column_safe('landing_page_content', 'background_color', 'VARCHAR(20)')
            add_column_safe('landing_page_content', 'text_color', 'VARCHAR(20)')
            
            # Atualizar valores NULL para default
            try:
                with db.engine.begin() as conn:
                    conn.execute(text("""
                        UPDATE landing_page_content 
                        SET background_color = '#ffffff' 
                        WHERE background_color IS NULL
                    """))
                    conn.execute(text("""
                        UPDATE landing_page_content 
                        SET text_color = '#000000' 
                        WHERE text_color IS NULL
                    """))
                print('  ✅ Valores padrão aplicados')
            except Exception as e:
                print(f'  ⚠️  Aviso ao atualizar valores: {e}')
            
            print()

        # 3. LESSON SCHEDULE
        if table_exists('lesson_schedule'):
            print('🔄 Passo 3: Corrigindo lesson_schedule...')
            
            add_column_safe('lesson_schedule', 'attendance_confirmed', 'BOOLEAN DEFAULT FALSE')
            add_column_safe('lesson_schedule', 'attendance_status', 'VARCHAR(20)')
            add_column_safe('lesson_schedule', 'confirmed_by', 'INTEGER')
            add_column_safe('lesson_schedule', 'confirmed_at', 'TIMESTAMP')
            add_column_safe('lesson_schedule', 'lesson_notes', 'TEXT')
            add_column_safe('lesson_schedule', 'lesson_content', 'TEXT')
            add_column_safe('lesson_schedule', 'homework_assigned', 'TEXT')
            add_column_safe('lesson_schedule', 'student_progress', 'VARCHAR(20)')
            
            print()

        # 4. PAYMENTS
        if table_exists('payments'):
            print('🔄 Passo 4: Corrigindo payments...')
            
            add_column_safe('payments', 'discount_reason', 'VARCHAR(255)')
            add_column_safe('payments', 'is_installment', 'BOOLEAN DEFAULT FALSE')
            add_column_safe('payments', 'installment_number', 'INTEGER')
            add_column_safe('payments', 'installment_total', 'INTEGER')
            add_column_safe('payments', 'parent_payment_id', 'INTEGER')
            add_column_safe('payments', 'stripe_customer_id', 'VARCHAR(255)')
            add_column_safe('payments', 'stripe_payment_intent_id', 'VARCHAR(255)')
            add_column_safe('payments', 'stripe_charge_id', 'VARCHAR(255)')
            add_column_safe('payments', 'stripe_payment_method_id', 'VARCHAR(255)')
            add_column_safe('payments', 'stripe_status', 'VARCHAR(50)')
            add_column_safe('payments', 'stripe_client_secret', 'VARCHAR(500)')
            add_column_safe('payments', 'stripe_webhook_received', 'BOOLEAN DEFAULT FALSE')
            add_column_safe('payments', 'stripe_error_message', 'TEXT')
            
            print()

        # 5. STUDENTS
        if table_exists('students'):
            print('🔄 Passo 5: Corrigindo students...')
            
            add_column_safe('students', 'stripe_customer_id', 'VARCHAR(255)')
            
            print()

        # 6. TRIAL LESSONS
        if table_exists('trial_lessons'):
            print('🔄 Passo 6: Corrigindo trial_lessons...')
            
            add_column_safe('trial_lessons', 'scheduled_date', 'DATE')
            add_column_safe('trial_lessons', 'scheduled_time', 'TIME')
            add_column_safe('trial_lessons', 'assigned_teacher_id', 'INTEGER')
            add_column_safe('trial_lessons', 'room_id', 'INTEGER')
            add_column_safe('trial_lessons', 'duration_minutes', 'INTEGER DEFAULT 60')
            add_column_safe('trial_lessons', 'confirmation_sent', 'BOOLEAN DEFAULT FALSE')
            add_column_safe('trial_lessons', 'notes', 'TEXT')
            add_column_safe('trial_lessons', 'confirmation_token', 'VARCHAR(100)')
            add_column_safe('trial_lessons', 'user_confirmed', 'BOOLEAN DEFAULT FALSE')
            add_column_safe('trial_lessons', 'user_confirmed_at', 'TIMESTAMP')
            add_column_safe('trial_lessons', 'user_declined', 'BOOLEAN DEFAULT FALSE')
            add_column_safe('trial_lessons', 'user_declined_at', 'TIMESTAMP')
            add_column_safe('trial_lessons', 'reminder_sent', 'BOOLEAN DEFAULT FALSE')
            add_column_safe('trial_lessons', 'reminder_sent_at', 'TIMESTAMP')
            
            print()

        # 7. Verificação final
        print('🔍 Passo 7: Verificação final...')
        print()
        
        critical_tables = {
            'landing_page_content': ['background_color', 'text_color'],
            'lesson_schedule': ['attendance_status', 'lesson_notes'],
            'payments': ['stripe_customer_id', 'discount_reason'],
            'students': ['stripe_customer_id'],
        }
        
        all_ok = True
        for table, columns in critical_tables.items():
            if table_exists(table):
                for col in columns:
                    if not column_exists(table, col):
                        print(f'  ❌ {table}.{col} FALTANDO!')
                        all_ok = False
                    else:
                        print(f'  ✓ {table}.{col}')
        
        print()
        print('=' * 70)
        if all_ok:
            print('✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!')
            print('=' * 70)
            print()
            print('🎉 Todas as colunas necessárias foram adicionadas.')
            print('📌 O sistema está pronto para uso.')
            print()
            print('Próximo passo: Reinicie o servidor Flask')
        else:
            print('⚠️  MIGRAÇÃO CONCLUÍDA COM AVISOS')
            print('=' * 70)
            print()
            print('Algumas colunas podem estar faltando.')
            print('Revise os erros acima e tente novamente.')
        print()

    except Exception as e:
        print()
        print('=' * 70)
        print('❌ ERRO CRÍTICO DURANTE A MIGRAÇÃO')
        print('=' * 70)
        print(f'\nErro: {str(e)}')
        print()
        traceback.print_exc()
        print()
        print('Por favor, verifique o erro e tente novamente.')
        print()
