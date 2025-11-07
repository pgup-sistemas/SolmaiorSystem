#!/usr/bin/env python3
from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Criar todas as tabelas
    db.create_all()
    print('✓ Tabelas criadas')
    
    # Verificar se admin existe
    admin = User.query.filter_by(email='admin@solmaior.com').first()
    
    if admin:
        print('✓ Admin já existe')
        print(f'  Email: {admin.email}')
        print(f'  Nome: {admin.full_name}')
        print(f'  Ativo: {admin.is_active}')
        
        # Resetar senha
        admin.set_password('admin123')
        db.session.commit()
        print('✓ Senha do admin resetada para: admin123')
    else:
        # Criar admin
        admin = User(
            email='admin@solmaior.com',
            full_name='Administrador',
            role='admin',
            phone='(11) 99999-9999',
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        
        print('✓ Admin criado com sucesso!')
        print('  Email: admin@solmaior.com')
        print('  Senha: admin123')
    
    print('\n✅ Pronto! Você pode fazer login agora.')
