
"""
Script de migração para adicionar novos campos na tabela students
"""
from app import create_app, db
from sqlalchemy import text

app = create_app()

def migrate_students_table():
    """Adiciona novos campos à tabela students"""
    with app.app_context():
        try:
            # Adicionar colunas de responsável
            db.session.execute(text("""
                ALTER TABLE students 
                ADD COLUMN IF NOT EXISTS guardian_name VARCHAR(200),
                ADD COLUMN IF NOT EXISTS guardian_phone VARCHAR(20),
                ADD COLUMN IF NOT EXISTS guardian_email VARCHAR(120),
                ADD COLUMN IF NOT EXISTS guardian_cpf VARCHAR(14);
            """))
            
            # Adicionar dados pessoais
            db.session.execute(text("""
                ALTER TABLE students 
                ADD COLUMN IF NOT EXISTS birth_date DATE,
                ADD COLUMN IF NOT EXISTS cpf VARCHAR(14),
                ADD COLUMN IF NOT EXISTS rg VARCHAR(20),
                ADD COLUMN IF NOT EXISTS address VARCHAR(300),
                ADD COLUMN IF NOT EXISTS city VARCHAR(100),
                ADD COLUMN IF NOT EXISTS state VARCHAR(2),
                ADD COLUMN IF NOT EXISTS zip_code VARCHAR(10);
            """))
            
            # Adicionar informações do curso
            db.session.execute(text("""
                ALTER TABLE students 
                ADD COLUMN IF NOT EXISTS course_modality VARCHAR(50),
                ADD COLUMN IF NOT EXISTS weekly_lessons INTEGER DEFAULT 1,
                ADD COLUMN IF NOT EXISTS lesson_duration INTEGER DEFAULT 60,
                ADD COLUMN IF NOT EXISTS preferred_schedule VARCHAR(100);
            """))
            
            # Adicionar outras informações
            db.session.execute(text("""
                ALTER TABLE students 
                ADD COLUMN IF NOT EXISTS medical_info TEXT,
                ADD COLUMN IF NOT EXISTS special_needs TEXT,
                ADD COLUMN IF NOT EXISTS previous_experience TEXT,
                ADD COLUMN IF NOT EXISTS goals TEXT,
                ADD COLUMN IF NOT EXISTS photo_url VARCHAR(500),
                ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE,
                ADD COLUMN IF NOT EXISTS notes TEXT;
            """))
            
            db.session.commit()
            print('✓ Migração da tabela students concluída com sucesso!')
            
        except Exception as e:
            db.session.rollback()
            print(f'✗ Erro na migração: {str(e)}')
            raise

if __name__ == '__main__':
    print('Iniciando migração do banco de dados...')
    migrate_students_table()
    print('Migração finalizada!')
