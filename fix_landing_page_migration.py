#!/usr/bin/env python3
"""
Script definitivo para corrigir estrutura do banco de dados
Versão robusta - adiciona colunas faltantes na tabela landing_page_content
"""
from app import create_app, db
from sqlalchemy import text
import sys

app = create_app()

def run_migration():
    """Executa a migração adicionando as colunas faltantes"""
    with app.app_context():
        print('=' * 70)
        print('🔧 CORREÇÃO DO BANCO DE DADOS - LANDING PAGE')
        print('=' * 70)
        print()

        try:
            # Conectar ao banco
            with db.engine.connect() as conn:
                # Verificar se a tabela existe
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'landing_page_content'
                    );
                """))

                if not result.scalar():
                    print('❌ Tabela landing_page_content não existe!')
                    print('Execute primeiro: python update_database.py')
                    sys.exit(1)

                print('✅ Tabela landing_page_content encontrada')
                print()

                # Adicionar coluna background_color se não existir
                print('🔄 Adicionando coluna background_color...')
                try:
                    conn.execute(text("""
                        ALTER TABLE landing_page_content 
                        ADD COLUMN IF NOT EXISTS background_color VARCHAR(20);
                    """))
                    conn.commit()
                    print('✅ Coluna background_color adicionada')
                except Exception as e:
                    print(f'⚠️  Aviso: {e}')

                # Adicionar coluna text_color se não existir
                print('🔄 Adicionando coluna text_color...')
                try:
                    conn.execute(text("""
                        ALTER TABLE landing_page_content 
                        ADD COLUMN IF NOT EXISTS text_color VARCHAR(20);
                    """))
                    conn.commit()
                    print('✅ Coluna text_color adicionada')
                except Exception as e:
                    print(f'⚠️  Aviso: {e}')

                # Verificar se as colunas foram criadas
                print()
                print('🔍 Verificando colunas...')
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'landing_page_content'
                    AND column_name IN ('background_color', 'text_color');
                """))

                columns = [row[0] for row in result]

                if 'background_color' in columns:
                    print('  ✅ background_color existe')
                else:
                    print('  ❌ background_color NÃO existe')
                    sys.exit(1)

                if 'text_color' in columns:
                    print('  ✅ text_color existe')
                else:
                    print('  ❌ text_color NÃO existe')
                    sys.exit(1)

                print()
                print('=' * 70)
                print('✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!')
                print('=' * 70)
                print()
                print('Próximo passo: Reinicie o servidor Flask')
                print('Use CTRL+C e clique no botão Run novamente')

        except Exception as e:
            print()
            print('=' * 70)
            print('❌ ERRO DURANTE A MIGRAÇÃO')
            print('=' * 70)
            print(f'\nErro: {str(e)}')
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    run_migration()