
#!/usr/bin/env python3
from app import create_app, db
from app.models import (
    PublicAnnouncement, LandingPageTestimonial, 
    LandingPageGallery, LandingPageContent
)

app = create_app()

with app.app_context():
    print('🔄 Criando novas tabelas para gestão de conteúdo...')
    
    # Criar todas as tabelas
    db.create_all()
    
    print('✅ Tabelas criadas com sucesso!')
    print('\nNovas tabelas adicionadas:')
    print('  - public_announcements (Avisos e anúncios)')
    print('  - landing_page_testimonials (Depoimentos)')
    print('  - landing_page_gallery (Galeria de fotos)')
    print('\n✨ Sistema de gestão de conteúdo pronto!')
