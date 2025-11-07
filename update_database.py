"""
Script de atualização do banco de dados
Adiciona as novas tabelas e dados iniciais para:
- Landing Page Dinâmica
- Recitals Completos (convites e certificados)
- Analytics do sistema
"""

from app import create_app, db
from app.models import LandingPageContent, LandingPageFeature
from datetime import datetime

app = create_app()

def create_tables():
    """Cria todas as tabelas do banco de dados"""
    with app.app_context():
        print('🔄 Criando novas tabelas...')
        db.create_all()
        print('✅ Tabelas criadas com sucesso!')

def seed_landing_page_content():
    """Popula conteúdo inicial da landing page"""
    with app.app_context():
        print('🔄 Populando conteúdo inicial da landing page...')
        
        # Verificar se já existe conteúdo
        if LandingPageContent.query.first():
            print('ℹ️  Conteúdo da landing page já existe. Pulando...')
            return
        
        # Seção Hero
        hero = LandingPageContent(
            section='hero',
            title='Bem-vindo à Escola de Música Sol Maior',
            subtitle='Excelência no ensino musical com professores qualificados, aulas personalizadas e uma estrutura completa para seu desenvolvimento artístico.',
            button_text='Agendar Aula Experimental',
            button_link='/trial-lesson',
            is_active=True,
            display_order=1
        )
        db.session.add(hero)
        
        # Seção About
        about = LandingPageContent(
            section='about',
            title='Por que escolher a Sol Maior?',
            subtitle='Descubra os diferenciais que fazem da Sol Maior a melhor escola de música',
            is_active=True,
            display_order=2
        )
        db.session.add(about)
        
        # Seção CTA
        cta = LandingPageContent(
            section='cta',
            title='Pronto para começar sua jornada musical?',
            subtitle='Agende agora uma aula experimental gratuita e descubra o músico que existe em você!',
            button_text='Agendar Aula Experimental',
            button_link='/trial-lesson',
            is_active=True,
            display_order=3
        )
        db.session.add(cta)
        
        db.session.commit()
        print('✅ Conteúdo da landing page criado!')

def seed_landing_page_features():
    """Popula features iniciais da landing page"""
    with app.app_context():
        print('🔄 Populando features da landing page...')
        
        # Verificar se já existem features
        if LandingPageFeature.query.first():
            print('ℹ️  Features da landing page já existem. Pulando...')
            return
        
        features_data = [
            {
                'icon': 'fas fa-guitar',
                'title': 'Diversos Instrumentos',
                'description': 'Piano, violão, guitarra, bateria, canto, violino e muito mais. Encontre o instrumento perfeito para você.',
                'display_order': 1
            },
            {
                'icon': 'fas fa-chalkboard-teacher',
                'title': 'Professores Qualificados',
                'description': 'Equipe experiente com formação acadêmica sólida e paixão pelo ensino musical.',
                'display_order': 2
            },
            {
                'icon': 'fas fa-calendar-alt',
                'title': 'Horários Flexíveis',
                'description': 'Escolha os melhores horários para suas aulas. Manhã, tarde ou noite - você decide!',
                'display_order': 3
            },
            {
                'icon': 'fas fa-users',
                'title': 'Aulas Individuais',
                'description': 'Ensino personalizado focado no seu ritmo e objetivos musicais. Atenção total do professor.',
                'display_order': 4
            },
            {
                'icon': 'fas fa-trophy',
                'title': 'Recitais e Apresentações',
                'description': 'Oportunidades regulares para apresentar seu progresso e ganhar experiência de palco.',
                'display_order': 5
            },
            {
                'icon': 'fas fa-map-marker-alt',
                'title': 'Localização Privilegiada',
                'description': 'Fácil acesso por transporte público e privado. Estrutura completa e confortável.',
                'display_order': 6
            }
        ]
        
        for feature_data in features_data:
            feature = LandingPageFeature(
                icon=feature_data['icon'],
                title=feature_data['title'],
                description=feature_data['description'],
                display_order=feature_data['display_order'],
                is_active=True
            )
            db.session.add(feature)
        
        db.session.commit()
        print(f'✅ {len(features_data)} features criadas!')

def main():
    """Executa todas as migrações"""
    print('=' * 60)
    print('ATUALIZAÇÃO DO BANCO DE DADOS - NOVAS FUNCIONALIDADES')
    print('=' * 60)
    print()
    
    create_tables()
    print()
    
    seed_landing_page_content()
    print()
    
    seed_landing_page_features()
    print()
    
    print('=' * 60)
    print('✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!')
    print('=' * 60)
    print()
    print('Novas funcionalidades disponíveis:')
    print('  ✓ Landing Page Dinâmica (editável pelo admin)')
    print('  ✓ Sistema completo de Recitais (PDFs, certificados, convites)')
    print('  ✓ Dashboard com Analytics e Gráficos')
    print('  ✓ Visualizador de Conflitos de Agenda')
    print()

if __name__ == '__main__':
    main()
