
#!/usr/bin/env python3
"""
Script SQL direto para adicionar colunas faltantes
"""
import os
import sys

def run_migration():
    """Executa SQL direto via psql"""
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print('❌ DATABASE_URL não configurada!')
        return False
    
    print('=' * 70)
    print('🔧 CORREÇÃO DO BANCO DE DADOS - LANDING PAGE')
    print('=' * 70)
    print()
    
    # SQL commands
    sql_commands = """
-- Adicionar coluna background_color se não existir
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'landing_page_content' 
        AND column_name = 'background_color'
    ) THEN
        ALTER TABLE landing_page_content ADD COLUMN background_color VARCHAR(20);
        RAISE NOTICE 'Coluna background_color adicionada';
    ELSE
        RAISE NOTICE 'Coluna background_color já existe';
    END IF;
END $$;

-- Adicionar coluna text_color se não existir
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'landing_page_content' 
        AND column_name = 'text_color'
    ) THEN
        ALTER TABLE landing_page_content ADD COLUMN text_color VARCHAR(20);
        RAISE NOTICE 'Coluna text_color adicionada';
    ELSE
        RAISE NOTICE 'Coluna text_color já existe';
    END IF;
END $$;

-- Verificar se as colunas existem
SELECT 
    column_name,
    data_type
FROM information_schema.columns 
WHERE table_name = 'landing_page_content'
AND column_name IN ('background_color', 'text_color')
ORDER BY column_name;
"""
    
    # Salvar SQL em arquivo temporário
    sql_file = '/tmp/fix_landing_page.sql'
    with open(sql_file, 'w') as f:
        f.write(sql_commands)
    
    print('📄 Arquivo SQL criado em:', sql_file)
    print()
    print('🔄 Executando SQL...')
    print()
    
    # Executar psql
    import subprocess
    
    try:
        result = subprocess.run(
            ['psql', database_url, '-f', sql_file],
            capture_output=True,
            text=True,
            check=True
        )
        
        print('✅ SQL executado com sucesso!')
        print()
        print('Saída:')
        print(result.stdout)
        
        if result.stderr:
            print('Avisos:')
            print(result.stderr)
        
        print()
        print('=' * 70)
        print('✅ MIGRAÇÃO CONCLUÍDA!')
        print('=' * 70)
        print()
        print('Próximo passo: Reinicie o servidor Flask')
        print('Use CTRL+C e clique no botão Run novamente')
        
        return True
        
    except subprocess.CalledProcessError as e:
        print('❌ Erro ao executar SQL!')
        print()
        print('Saída:', e.stdout)
        print('Erro:', e.stderr)
        return False
    except FileNotFoundError:
        print('❌ Comando psql não encontrado!')
        print()
        print('Tentando método alternativo...')
        return run_migration_alternative()

def run_migration_alternative():
    """Método alternativo usando Python puro"""
    import psycopg2
    from urllib.parse import urlparse
    
    database_url = os.environ.get('DATABASE_URL')
    url = urlparse(database_url)
    
    print('🔄 Usando conexão Python direta...')
    print()
    
    try:
        conn = psycopg2.connect(
            host=url.hostname,
            port=url.port,
            user=url.username,
            password=url.password,
            database=url.path[1:]
        )
        
        conn.autocommit = True
        cur = conn.cursor()
        
        # Adicionar background_color
        print('🔄 Adicionando coluna background_color...')
        try:
            cur.execute("""
                ALTER TABLE landing_page_content 
                ADD COLUMN IF NOT EXISTS background_color VARCHAR(20)
            """)
            print('✅ Coluna background_color adicionada')
        except Exception as e:
            print(f'⚠️  {e}')
        
        # Adicionar text_color
        print('🔄 Adicionando coluna text_color...')
        try:
            cur.execute("""
                ALTER TABLE landing_page_content 
                ADD COLUMN IF NOT EXISTS text_color VARCHAR(20)
            """)
            print('✅ Coluna text_color adicionada')
        except Exception as e:
            print(f'⚠️  {e}')
        
        # Verificar
        print()
        print('🔍 Verificando colunas...')
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns 
            WHERE table_name = 'landing_page_content'
            AND column_name IN ('background_color', 'text_color')
            ORDER BY column_name
        """)
        
        rows = cur.fetchall()
        
        if len(rows) == 2:
            print('✅ Ambas colunas existem:')
            for row in rows:
                print(f'  - {row[0]} ({row[1]})')
            
            cur.close()
            conn.close()
            
            print()
            print('=' * 70)
            print('✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!')
            print('=' * 70)
            print()
            print('Próximo passo: Reinicie o servidor Flask')
            print('Use CTRL+C e clique no botão Run novamente')
            
            return True
        else:
            print('❌ Colunas não foram criadas corretamente')
            cur.close()
            conn.close()
            return False
            
    except Exception as e:
        print(f'❌ Erro: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
