
#!/usr/bin/env python3
"""
Script para criar o usuário administrador
"""
from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    print('👤 Criando usuário administrador...\n')
    
    # Verificar se admin já existe
    admin = User.query.filter_by(email='admin@solmaior.com').first()
    
    if admin:
        print('⚠️  Admin já existe!')
        print(f'   Email: {admin.email}')
        print(f'   Nome: {admin.full_name}')
        print(f'   Ativo: {admin.is_active}')
        print('\n🔄 Resetando senha...')
        
        # Resetar senha
        admin.set_password('admin123')
        admin.is_active = True
        db.session.commit()
        
        print('✅ Senha resetada para: admin123')
    else:
        # Criar novo admin
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
        
        print('✅ Admin criado com sucesso!')
        print(f'   Email: admin@solmaior.com')
        print(f'   Senha: admin123')
    
    print('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    print('🎉 Pronto! Você pode fazer login agora em:')
    print('   http://192.168.100.10:5000/login')
    print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')
