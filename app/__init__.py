import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from config import DevelopmentConfig, ProductionConfig

db = SQLAlchemy()
login_manager = LoginManager()
jwt = JWTManager()
mail = Mail()
csrf = CSRFProtect()

def create_app(config_class=None):
    app = Flask(__name__)
    
    if config_class is None:
        if os.environ.get('FLASK_ENV') == 'production':
            config_class = ProductionConfig
        else:
            config_class = DevelopmentConfig
    
    app.config.from_object(config_class)
    
    db.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    
    from app.routes import auth, public, admin, teacher, student, secretary, financial, documents, profile, trial_lessons, payments
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(public.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(teacher.bp)
    app.register_blueprint(student.bp)
    app.register_blueprint(secretary.bp)
    app.register_blueprint(financial.bp)
    app.register_blueprint(documents.bp)
    app.register_blueprint(profile.bp)
    app.register_blueprint(trial_lessons.bp)
    app.register_blueprint(payments.bp)
    
    return app
