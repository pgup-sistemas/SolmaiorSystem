
"""
Script de migração para adicionar novos campos no banco de dados
"""
from app import create_app, db
from sqlalchemy import text, inspect
import sys

app = create_app()

def column_exists(table_name, column_name):
    """Verifica se uma coluna existe em uma tabela"""
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def migrate_students_table():
    """Adiciona novos campos à tabela students"""
    with app.app_context():
        try:
            print('\n🔄 Migrando tabela students...')
            
            # Lista de colunas a adicionar
            columns_to_add = {
                'guardian_name': 'VARCHAR(200)',
                'guardian_phone': 'VARCHAR(20)',
                'guardian_email': 'VARCHAR(120)',
                'guardian_cpf': 'VARCHAR(14)',
                'birth_date': 'DATE',
                'cpf': 'VARCHAR(14)',
                'rg': 'VARCHAR(20)',
                'address': 'VARCHAR(300)',
                'city': 'VARCHAR(100)',
                'state': 'VARCHAR(2)',
                'zip_code': 'VARCHAR(10)',
                'course_modality': 'VARCHAR(50)',
                'weekly_lessons': 'INTEGER DEFAULT 1',
                'lesson_duration': 'INTEGER DEFAULT 60',
                'preferred_schedule': 'VARCHAR(100)',
                'medical_info': 'TEXT',
                'special_needs': 'TEXT',
                'previous_experience': 'TEXT',
                'goals': 'TEXT',
                'photo_url': 'VARCHAR(500)',
                'is_active': 'BOOLEAN DEFAULT TRUE',
                'notes': 'TEXT'
            }
            
            added_count = 0
            for column_name, column_type in columns_to_add.items():
                if not column_exists('students', column_name):
                    db.session.execute(text(f"""
                        ALTER TABLE students 
                        ADD COLUMN {column_name} {column_type};
                    """))
                    print(f'  ✓ Coluna {column_name} adicionada')
                    added_count += 1
                else:
                    print(f'  ⊙ Coluna {column_name} já existe')
            
            db.session.commit()
            print(f'✅ Migração da tabela students concluída! ({added_count} colunas adicionadas)')
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f'❌ Erro na migração da tabela students: {str(e)}')
            return False

def migrate_users_table():
    """Adiciona campo de avatar à tabela users"""
    with app.app_context():
        try:
            print('\n🔄 Migrando tabela users...')
            
            if not column_exists('users', 'avatar_url'):
                db.session.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN avatar_url VARCHAR(500);
                """))
                db.session.commit()
                print('  ✓ Coluna avatar_url adicionada')
                print('✅ Migração da tabela users concluída!')
            else:
                print('  ⊙ Coluna avatar_url já existe')
                print('✅ Tabela users já está atualizada!')
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f'❌ Erro na migração da tabela users: {str(e)}')
            return False

def verify_migrations():
    """Verifica se as migrações foram aplicadas corretamente"""
    with app.app_context():
        print('\n🔍 Verificando migrações...')
        
        students_columns = ['guardian_name', 'guardian_email', 'birth_date', 'cpf', 
                          'course_modality', 'medical_info', 'photo_url', 'is_active']
        
        all_good = True
        for col in students_columns:
            exists = column_exists('students', col)
            status = '✓' if exists else '✗'
            print(f'  {status} students.{col}')
            if not exists:
                all_good = False
        
        users_exists = column_exists('users', 'avatar_url')
        status = '✓' if users_exists else '✗'
        print(f'  {status} users.avatar_url')
        if not users_exists:
            all_good = False
        
        return all_good

if __name__ == '__main__':
    print('=' * 60)
    print('🚀 Iniciando migração do banco de dados...')
    print('=' * 60)
    
    success = True
    
    # Migrar tabelas
    if not migrate_students_table():
        success = False
    
    if not migrate_users_table():
        success = False
    
    # Verificar migrações
    print('\n' + '=' * 60)
    if verify_migrations():
        print('✅ TODAS AS MIGRAÇÕES FORAM APLICADAS COM SUCESSO!')
    else:
        print('⚠️  ALGUMAS MIGRAÇÕES FALHARAM!')
        success = False
    
    print('=' * 60)
    
    sys.exit(0 if success else 1)
