
#!/usr/bin/env python3
"""
Script definitivo para corrigir estrutura do banco de dados
Adiciona colunas faltantes na tabela landing_page_content usando SQL direto
"""
import psycopg2
import os
from urllib.parse import urlparse

def get_db_connection():
    """Obter conexão direta com PostgreSQL"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise Exception('DATABASE_URL não configurada')
    
    # Parse da URL
    url = urlparse(database_url)
    
    return psycopg2.connect(
        host=url.hostname,
        port=url.port,
        user=url.username,
        password=url.password,
        database=url.path[1:]
    )

def run_migration():
    """Executa a migração adicionando as colunas faltantes"""
    print('=' * 70)
    print('🔧 CORREÇÃO DO BANCO DE DADOS - LANDING PAGE')
    print('=' * 70)
    print()

    conn = None
    try:
        # Conectar ao banco
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verificar se a tabela existe
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'landing_page_content'
            );
        """)
        
        if not cur.fetchone()[0]:
            print('❌ Tabela landing_page_content não existe!')
            print('Execute primeiro: python update_database.py')
            return False

        print('✅ Tabela landing_page_content encontrada')
        print()

        # Adicionar coluna background_color se não existir
        print('🔄 Adicionando coluna background_color...')
        try:
            cur.execute("""
                ALTER TABLE landing_page_content 
                ADD COLUMN IF NOT EXISTS background_color VARCHAR(20);
            """)
            conn.commit()
            print('✅ Coluna background_color adicionada')
        except Exception as e:
            conn.rollback()
            print(f'⚠️  Aviso background_color: {e}')

        # Adicionar coluna text_color se não existir
        print('🔄 Adicionando coluna text_color...')
        try:
            cur.execute("""
                ALTER TABLE landing_page_content 
                ADD COLUMN IF NOT EXISTS text_color VARCHAR(20);
            """)
            conn.commit()
            print('✅ Coluna text_color adicionada')
        except Exception as e:
            conn.rollback()
            print(f'⚠️  Aviso text_color: {e}')

        # Verificar se as colunas foram criadas
        print()
        print('🔍 Verificando colunas...')
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'landing_page_content'
            AND column_name IN ('background_color', 'text_color');
        """)

        columns = [row[0] for row in cur.fetchall()]

        if 'background_color' in columns:
            print('  ✅ background_color existe')
        else:
            print('  ❌ background_color NÃO existe')
            return False

        if 'text_color' in columns:
            print('  ✅ text_color existe')
        else:
            print('  ❌ text_color NÃO existe')
            return False

        print()
        print('=' * 70)
        print('✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!')
        print('=' * 70)
        print()
        print('Próximo passo: Reinicie o servidor Flask')
        print('Use CTRL+C e clique no botão Run novamente')
        
        cur.close()
        return True

    except Exception as e:
        if conn:
            conn.rollback()
        print()
        print('=' * 70)
        print('❌ ERRO DURANTE A MIGRAÇÃO')
        print('=' * 70)
        print(f'\nErro: {str(e)}')
        import traceback
        traceback.print_exc()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    success = run_migration()
    exit(0 if success else 1)
