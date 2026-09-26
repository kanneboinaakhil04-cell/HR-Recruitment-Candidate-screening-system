import os
from flask import Flask, render_template, session
from config import Config
from models import db
from routes.auth import auth_bp
from routes.hr import hr_bp
from routes.candidate import candidate_bp
from routes.screening import screening_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize SQLAlchemy database engine
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(hr_bp)
    app.register_blueprint(candidate_bp)
    app.register_blueprint(screening_bp)

    # Ensure Upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.context_processor
    def inject_user():
        return dict(
            user_id=session.get('user_id'),
            role=session.get('role'),
            full_name=session.get('full_name')
        )

    # Create tables inside application context
    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    print("Starting HR Recruitment & Candidate Screening System...")
    print("Access application at: http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
