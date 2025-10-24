
"""
Script de migração completo para atualizar estrutura do banco de dados
"""
from app import create_app, db
from sqlalchemy import text, inspect

app = create_app()

def column_exists(table_name, column_name):
    """Verifica se uma coluna existe em uma tabela"""
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def migrate_users_table():
    """Adiciona novos campos à tabela users"""
    with app.app_context():
        print('\n🔄 Migrando tabela users...')
        try:
            columns_to_add = [
                ('avatar_url', 'VARCHAR(500)'),
                ('last_login', 'TIMESTAMP'),
            ]
            
            added_count = 0
            for col_name, col_type in columns_to_add:
                if not column_exists('users', col_name):
                    db.session.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                    print(f'  ✓ Coluna {col_name} adicionada')
                    added_count += 1
                else:
                    print(f'  ⊙ Coluna {col_name} já existe')
            
            db.session.commit()
            print(f'✅ Migração da tabela users concluída! ({added_count} colunas adicionadas)')
            return True
        except Exception as e:
            db.session.rollback()
            print(f'✗ Erro na migração de users: {str(e)}')
            return False

def migrate_students_table():
    """Adiciona novos campos à tabela students"""
    with app.app_context():
        print('\n🔄 Migrando tabela students...')
        try:
            columns_to_add = [
                ('guardian_name', 'VARCHAR(200)'),
                ('guardian_phone', 'VARCHAR(20)'),
                ('guardian_email', 'VARCHAR(120)'),
                ('guardian_cpf', 'VARCHAR(14)'),
                ('birth_date', 'DATE'),
                ('cpf', 'VARCHAR(14)'),
                ('rg', 'VARCHAR(20)'),
                ('address', 'VARCHAR(300)'),
                ('city', 'VARCHAR(100)'),
                ('state', 'VARCHAR(2)'),
                ('zip_code', 'VARCHAR(10)'),
                ('course_modality', 'VARCHAR(50)'),
                ('weekly_lessons', 'INTEGER DEFAULT 1'),
                ('lesson_duration', 'INTEGER DEFAULT 60'),
                ('preferred_schedule', 'VARCHAR(100)'),
                ('medical_info', 'TEXT'),
                ('special_needs', 'TEXT'),
                ('previous_experience', 'TEXT'),
                ('goals', 'TEXT'),
                ('photo_url', 'VARCHAR(500)'),
                ('is_active', 'BOOLEAN DEFAULT TRUE'),
                ('notes', 'TEXT'),
                ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ]
            
            added_count = 0
            for col_name, col_type in columns_to_add:
                if not column_exists('students', col_name):
                    db.session.execute(text(f"ALTER TABLE students ADD COLUMN {col_name} {col_type}"))
                    print(f'  ✓ Coluna {col_name} adicionada')
                    added_count += 1
                else:
                    print(f'  ⊙ Coluna {col_name} já existe')
            
            # Criar índice para CPF se não existir
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_student_cpf ON students(cpf)"))
            
            db.session.commit()
            print(f'✅ Migração da tabela students concluída! ({added_count} colunas adicionadas)')
            return True
        except Exception as e:
            db.session.rollback()
            print(f'✗ Erro na migração de students: {str(e)}')
            return False

def migrate_teachers_table():
    """Adiciona novos campos à tabela teachers"""
    with app.app_context():
        print('\n🔄 Migrando tabela teachers...')
        try:
            columns_to_add = [
                ('hourly_rate', 'FLOAT'),
                ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ]
            
            added_count = 0
            for col_name, col_type in columns_to_add:
                if not column_exists('teachers', col_name):
                    db.session.execute(text(f"ALTER TABLE teachers ADD COLUMN {col_name} {col_type}"))
                    print(f'  ✓ Coluna {col_name} adicionada')
                    added_count += 1
                else:
                    print(f'  ⊙ Coluna {col_name} já existe')
            
            db.session.commit()
            print(f'✅ Migração da tabela teachers concluída! ({added_count} colunas adicionadas)')
            return True
        except Exception as e:
            db.session.rollback()
            print(f'✗ Erro na migração de teachers: {str(e)}')
            return False

def migrate_lesson_schedule_table():
    """Adiciona novos campos à tabela lesson_schedule"""
    with app.app_context():
        print('\n🔄 Migrando tabela lesson_schedule...')
        try:
            columns_to_add = [
                ('attendance_confirmed', 'BOOLEAN DEFAULT FALSE'),
                ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ]
            
            added_count = 0
            for col_name, col_type in columns_to_add:
                if not column_exists('lesson_schedule', col_name):
                    db.session.execute(text(f"ALTER TABLE lesson_schedule ADD COLUMN {col_name} {col_type}"))
                    print(f'  ✓ Coluna {col_name} adicionada')
                    added_count += 1
                else:
                    print(f'  ⊙ Coluna {col_name} já existe')
            
            db.session.commit()
            print(f'✅ Migração da tabela lesson_schedule concluída! ({added_count} colunas adicionadas)')
            return True
        except Exception as e:
            db.session.rollback()
            print(f'✗ Erro na migração de lesson_schedule: {str(e)}')
            return False

def migrate_enrollments_table():
    """Adiciona novos campos à tabela enrollments"""
    with app.app_context():
        print('\n🔄 Migrando tabela enrollments...')
        try:
            columns_to_add = [
                ('cancellation_reason', 'TEXT'),
                ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ]
            
            added_count = 0
            for col_name, col_type in columns_to_add:
                if not column_exists('enrollments', col_name):
                    db.session.execute(text(f"ALTER TABLE enrollments ADD COLUMN {col_name} {col_type}"))
                    print(f'  ✓ Coluna {col_name} adicionada')
                    added_count += 1
                else:
                    print(f'  ⊙ Coluna {col_name} já existe')
            
            db.session.commit()
            print(f'✅ Migração da tabela enrollments concluída! ({added_count} colunas adicionadas)')
            return True
        except Exception as e:
            db.session.rollback()
            print(f'✗ Erro na migração de enrollments: {str(e)}')
            return False

def migrate_news_posts_table():
    """Adiciona novos campos à tabela news_posts"""
    with app.app_context():
        print('\n🔄 Migrando tabela news_posts...')
        try:
            columns_to_add = [
                ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ]
            
            added_count = 0
            for col_name, col_type in columns_to_add:
                if not column_exists('news_posts', col_name):
                    db.session.execute(text(f"ALTER TABLE news_posts ADD COLUMN {col_name} {col_type}"))
                    print(f'  ✓ Coluna {col_name} adicionada')
                    added_count += 1
                else:
                    print(f'  ⊙ Coluna {col_name} já existe')
            
            db.session.commit()
            print(f'✅ Migração da tabela news_posts concluída! ({added_count} colunas adicionadas)')
            return True
        except Exception as e:
            db.session.rollback()
            print(f'✗ Erro na migração de news_posts: {str(e)}')
            return False

def migrate_payments_table():
    """Adiciona novos campos à tabela payments"""
    with app.app_context():
        print('\n🔄 Migrando tabela payments...')
        try:
            columns_to_add = [
                ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ]
            
            added_count = 0
            for col_name, col_type in columns_to_add:
                if not column_exists('payments', col_name):
                    db.session.execute(text(f"ALTER TABLE payments ADD COLUMN {col_name} {col_type}"))
                    print(f'  ✓ Coluna {col_name} adicionada')
                    added_count += 1
                else:
                    print(f'  ⊙ Coluna {col_name} já existe')
            
            db.session.commit()
            print(f'✅ Migração da tabela payments concluída! ({added_count} colunas adicionadas)')
            return True
        except Exception as e:
            db.session.rollback()
            print(f'✗ Erro na migração de payments: {str(e)}')
            return False

def migrate_rooms_table():
    """Adiciona novos campos à tabela rooms"""
    with app.app_context():
        print('\n🔄 Migrando tabela rooms...')
        try:
            columns_to_add = [
                ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ]
            
            added_count = 0
            for col_name, col_type in columns_to_add:
                if not column_exists('rooms', col_name):
                    db.session.execute(text(f"ALTER TABLE rooms ADD COLUMN {col_name} {col_type}"))
                    print(f'  ✓ Coluna {col_name} adicionada')
                    added_count += 1
                else:
                    print(f'  ⊙ Coluna {col_name} já existe')
            
            db.session.commit()
            print(f'✅ Migração da tabela rooms concluída! ({added_count} colunas adicionadas)')
            return True
        except Exception as e:
            db.session.rollback()
            print(f'✗ Erro na migração de rooms: {str(e)}')
            return False

def migrate_recitals_table():
    """Adiciona novos campos à tabela recitals"""
    with app.app_context():
        print('\n🔄 Migrando tabela recitals...')
        try:
            columns_to_add = [
                ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ]
            
            added_count = 0
            for col_name, col_type in columns_to_add:
                if not column_exists('recitals', col_name):
                    db.session.execute(text(f"ALTER TABLE recitals ADD COLUMN {col_name} {col_type}"))
                    print(f'  ✓ Coluna {col_name} adicionada')
                    added_count += 1
                else:
                    print(f'  ⊙ Coluna {col_name} já existe')
            
            db.session.commit()
            print(f'✅ Migração da tabela recitals concluída! ({added_count} colunas adicionadas)')
            return True
        except Exception as e:
            db.session.rollback()
            print(f'✗ Erro na migração de recitals: {str(e)}')
            return False

def migrate_documents_table():
    """Adiciona novos campos à tabela documents"""
    with app.app_context():
        print('\n🔄 Migrando tabela documents...')
        try:
            columns_to_add = [
                ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ]
            
            added_count = 0
            for col_name, col_type in columns_to_add:
                if not column_exists('documents', col_name):
                    db.session.execute(text(f"ALTER TABLE documents ADD COLUMN {col_name} {col_type}"))
                    print(f'  ✓ Coluna {col_name} adicionada')
                    added_count += 1
                else:
                    print(f'  ⊙ Coluna {col_name} já existe')
            
            db.session.commit()
            print(f'✅ Migração da tabela documents concluída! ({added_count} colunas adicionadas)')
            return True
        except Exception as e:
            db.session.rollback()
            print(f'✗ Erro na migração de documents: {str(e)}')
            return False

def migrate_trial_lessons_table():
    """Adiciona novos campos à tabela trial_lessons"""
    with app.app_context():
        print('\n🔄 Migrando tabela trial_lessons...')
        try:
            columns_to_add = [
                ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ]
            
            added_count = 0
            for col_name, col_type in columns_to_add:
                if not column_exists('trial_lessons', col_name):
                    db.session.execute(text(f"ALTER TABLE trial_lessons ADD COLUMN {col_name} {col_type}"))
                    print(f'  ✓ Coluna {col_name} adicionada')
                    added_count += 1
                else:
                    print(f'  ⊙ Coluna {col_name} já existe')
            
            db.session.commit()
            print(f'✅ Migração da tabela trial_lessons concluída! ({added_count} colunas adicionadas)')
            return True
        except Exception as e:
            db.session.rollback()
            print(f'✗ Erro na migração de trial_lessons: {str(e)}')
            return False

def migrate_other_tables():
    """Adiciona novos campos às demais tabelas"""
    with app.app_context():
        print('\n🔄 Migrando tabelas auxiliares...')
        try:
            tables_columns = [
                ('teacher_availability', [('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')]),
                ('recital_performances', [('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')]),
                ('recital_participants', [('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')]),
                ('makeup_lessons', [('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'), ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')]),
            ]
            
            total_added = 0
            for table_name, columns in tables_columns:
                for col_name, col_type in columns:
                    if not column_exists(table_name, col_name):
                        db.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"))
                        print(f'  ✓ Coluna {table_name}.{col_name} adicionada')
                        total_added += 1
                    else:
                        print(f'  ⊙ Coluna {table_name}.{col_name} já existe')
            
            db.session.commit()
            print(f'✅ Migração das tabelas auxiliares concluída! ({total_added} colunas adicionadas)')
            return True
        except Exception as e:
            db.session.rollback()
            print(f'✗ Erro na migração das tabelas auxiliares: {str(e)}')
            return False

def verify_migrations():
    """Verifica se as migrações foram aplicadas corretamente"""
    with app.app_context():
        print('\n🔍 Verificando migrações...')
        
        checks = [
            ('users', 'avatar_url'),
            ('users', 'last_login'),
            ('students', 'guardian_name'),
            ('students', 'cpf'),
            ('students', 'is_active'),
            ('students', 'created_at'),
            ('teachers', 'hourly_rate'),
            ('teachers', 'created_at'),
            ('lesson_schedule', 'attendance_confirmed'),
            ('lesson_schedule', 'created_at'),
            ('enrollments', 'cancellation_reason'),
            ('enrollments', 'created_at'),
        ]
        
        all_good = True
        for table, column in checks:
            exists = column_exists(table, column)
            status = '✓' if exists else '✗'
            print(f'  {status} {table}.{column}')
            if not exists:
                all_good = False
        
        return all_good

if __name__ == '__main__':
    print('=' * 60)
    print('🚀 Iniciando migração completa do banco de dados...')
    print('=' * 60)
    
    success = True
    
    # Executar todas as migrações
    migrations = [
        migrate_users_table,
        migrate_students_table,
        migrate_teachers_table,
        migrate_lesson_schedule_table,
        migrate_enrollments_table,
        migrate_news_posts_table,
        migrate_payments_table,
        migrate_rooms_table,
        migrate_recitals_table,
        migrate_documents_table,
        migrate_trial_lessons_table,
        migrate_other_tables,
    ]
    
    for migration in migrations:
        if not migration():
            success = False
    
    # Verificar resultado
    print('\n' + '=' * 60)
    if success:
        print('✅ TODAS AS MIGRAÇÕES FORAM APLICADAS COM SUCESSO!')
    else:
        print('⚠️  ALGUMAS MIGRAÇÕES FALHARAM!')
    print('=' * 60)
    
    if not success:
        exit(1)
