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


@app.cli.command()
def run_daily_tasks():
    """Execute daily automated tasks (reminders, absences)"""
    from app.tasks import run_daily_tasks
    print('🔄 Executando tarefas diárias...')
    results = run_daily_tasks()
    print(f'✅ Concluído: {results}')


@app.cli.command()
def run_hourly_tasks():
    """Execute hourly automated tasks (process notifications)"""
    from app.tasks import run_hourly_tasks
    print('🔄 Executando tarefas horárias...')
    results = run_hourly_tasks()
    print(f'✅ Concluído: {results}')


@app.cli.command()
def test_email():
    """Test email configuration"""
    from app.tasks import send_email
    test_recipient = input('Digite o email de destino para teste: ')
    success = send_email(
        test_recipient,
        'Teste de Email - Solmaior',
        'Este é um email de teste do sistema Solmaior.\n\nSe você recebeu esta mensagem, a configuração está correta!'
    )
    if success:
        print('✅ Email enviado com sucesso!')
    else:
        print('❌ Falha ao enviar email. Verifique as configurações no .env')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
