import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from models.models import db, Usuario, Especialidade, Avaliacao, Portfolio

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Configurar SQLite em vez de MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///construmarket.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Importar e registrar blueprints
from src.routes.auth import auth_bp
from src.routes.profissionais import profissionais_bp
from src.routes.avaliacoes import avaliacoes_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(profissionais_bp, url_prefix='/api/profissionais')
app.register_blueprint(avaliacoes_bp, url_prefix='/api/avaliacoes')

# Criar tabelas na base de dados
with app.app_context():
    db.create_all()
    
    # Verificar se já existem especialidades cadastradas
    if Especialidade.query.count() == 0:
        # Adicionar especialidades iniciais
        especialidades = [
            Especialidade(nome='Pedreiro', categoria='Construção', descricao='Profissional especializado em alvenaria e construção'),
            Especialidade(nome='Eletricista', categoria='Instalações', descricao='Profissional especializado em instalações elétricas'),
            Especialidade(nome='Encanador', categoria='Instalações', descricao='Profissional especializado em instalações hidráulicas'),
            Especialidade(nome='Pintor', categoria='Acabamento', descricao='Profissional especializado em pintura'),
            Especialidade(nome='Carpinteiro', categoria='Acabamento', descricao='Profissional especializado em trabalhos com madeira'),
            Especialidade(nome='Serralheiro', categoria='Acabamento', descricao='Profissional especializado em trabalhos com metal'),
            Especialidade(nome='Gesseiro', categoria='Acabamento', descricao='Profissional especializado em trabalhos com gesso'),
            Especialidade(nome='Jardineiro', categoria='Exterior', descricao='Profissional especializado em jardinagem'),
            Especialidade(nome='Arquiteto', categoria='Projeto', descricao='Profissional especializado em projetos arquitetônicos'),
            Especialidade(nome='Engenheiro Civil', categoria='Projeto', descricao='Profissional especializado em projetos de engenharia')
        ]
        for esp in especialidades:
            db.session.add(esp)
        db.session.commit()

# Rota para a API principal
@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'online',
        'name': 'ConstruMarket API',
        'version': '1.0.0'
    })

# Rotas para servir arquivos estáticos
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)