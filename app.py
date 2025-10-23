from app import create_app, db
from app.models import User, Teacher, Student

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Teacher': Teacher, 'Student': Student}

@app.cli.command()
def init_db():
    """Initialize the database with sample data."""
    db.create_all()
    
    if not User.query.filter_by(email='admin@solmaior.com').first():
        admin = User(
            email='admin@solmaior.com',
            full_name='Administrador',
            role='admin',
            phone='(11) 99999-9999'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        print('✓ Usuário admin criado')
        print('  Email: admin@solmaior.com')
        print('  Senha: admin123')
    
    db.session.commit()
    print('✓ Banco de dados inicializado!')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
