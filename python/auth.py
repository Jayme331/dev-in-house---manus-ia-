from flask import Blueprint, request, jsonify
from models import db, Usuario
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os
import base64
import hashlib

auth_bp = Blueprint('auth', __name__)

# Chave secreta para tokens
SECRET_KEY = os.environ.get('SECRET_KEY', 'chave_secreta_temporaria')

# Função para gerar token simples
def gerar_token(usuario_id):
    expiry = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    expiry_str = expiry.strftime("%Y-%m-%d %H:%M:%S")
    
    # Criar payload simples
    payload = f"{usuario_id}|{expiry_str}"
    
    # Codificar e assinar com hash simples
    signature = hashlib.sha256((payload + SECRET_KEY).encode()).hexdigest()
    token = base64.b64encode(f"{payload}|{signature}".encode()).decode()
    
    return token

# Função para verificar token
def verificar_token(token):
    try:
        # Decodificar token
        decoded = base64.b64decode(token.encode()).decode()
        payload, signature = decoded.rsplit('|', 1)
        
        # Verificar assinatura
        if signature != hashlib.sha256((payload + SECRET_KEY).encode()).hexdigest():
            return None
        
        # Extrair dados
        usuario_id, expiry_str = payload.split('|')
        expiry = datetime.datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S")
        
        # Verificar expiração
        if expiry < datetime.datetime.utcnow():
            return None
        
        return int(usuario_id)
    except Exception:
        return None

# Rota de registro
@auth_bp.route('/registar', methods=['POST'])
def registar():
    data = request.get_json()
    
    # Verificar se todos os campos obrigatórios estão presentes
    if not all(k in data for k in ['nome', 'email', 'senha', 'tipo']):
        return jsonify({'erro': 'Dados incompletos'}), 400
    
    # Verificar se o email já está em uso
    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'erro': 'Email já registado'}), 400
    
    # Verificar se o tipo de usuário é válido
    if data['tipo'] not in ['cliente', 'profissional']:
        return jsonify({'erro': 'Tipo de usuário inválido'}), 400
    
    # Criar novo usuário
    novo_usuario = Usuario(
        nome=data['nome'],
        email=data['email'],
        senha=data['senha'],
        tipo=data['tipo']
    )
    
    # Adicionar campos específicos conforme o tipo de usuário
    if data['tipo'] == 'profissional':
        novo_usuario.descricao = data.get('descricao', '')
        novo_usuario.anos_experiencia = data.get('anos_experiencia', 0)
        novo_usuario.regiao_atuacao = data.get('regiao_atuacao', '')
        novo_usuario.disponibilidade = data.get('disponibilidade', '')
    elif data['tipo'] == 'cliente':
        novo_usuario.endereco = data.get('endereco', '')
        novo_usuario.preferencias = data.get('preferencias', '')
    
    # Adicionar telefone e foto de perfil se fornecidos
    if 'telefone' in data:
        novo_usuario.telefone = data['telefone']
    if 'foto_perfil' in data:
        novo_usuario.foto_perfil = data['foto_perfil']
    
    # Salvar na base de dados
    db.session.add(novo_usuario)
    db.session.commit()
    
    # Gerar token
    token = gerar_token(novo_usuario.id)
    
    return jsonify({
        'mensagem': 'Usuário registado com sucesso',
        'token': token,
        'usuario': novo_usuario.to_dict()
    }), 201

# Rota de login
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Verificar se email e senha foram fornecidos
    if not all(k in data for k in ['email', 'senha']):
        return jsonify({'erro': 'Email e senha são obrigatórios'}), 400
    
    # Buscar usuário pelo email
    usuario = Usuario.query.filter_by(email=data['email']).first()
    
    # Verificar se o usuário existe e a senha está correta
    if not usuario or not usuario.check_senha(data['senha']):
        return jsonify({'erro': 'Email ou senha incorretos'}), 401
    
    # Gerar token
    token = gerar_token(usuario.id)
    
    return jsonify({
        'mensagem': 'Login realizado com sucesso',
        'token': token,
        'usuario': usuario.to_dict()
    }), 200

# Middleware para verificar token
def token_required(f):
    def decorated(*args, **kwargs):
        token = None
        
        # Verificar se o token está no cabeçalho Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'erro': 'Token não fornecido'}), 401
        
        # Verificar token
        usuario_id = verificar_token(token)
        if not usuario_id:
            return jsonify({'erro': 'Token inválido ou expirado'}), 401
        
        # Buscar usuário pelo ID
        usuario_atual = Usuario.query.get(usuario_id)
        if not usuario_atual:
            return jsonify({'erro': 'Usuário não encontrado'}), 401
        
        return f(usuario_atual, *args, **kwargs)
    
    # Renomear a função para evitar problemas com decoradores
    decorated.__name__ = f.__name__
    return decorated

# Rota para obter informações do usuário atual
@auth_bp.route('/perfil', methods=['GET'])
@token_required
def perfil(usuario_atual):
    return jsonify({
        'usuario': usuario_atual.to_dict()
    }), 200

# Rota para atualizar informações do usuário
@auth_bp.route('/perfil', methods=['PUT'])
@token_required
def atualizar_perfil(usuario_atual):
    data = request.get_json()
    
    # Atualizar campos básicos
    if 'nome' in data:
        usuario_atual.nome = data['nome']
    if 'telefone' in data:
        usuario_atual.telefone = data['telefone']
    if 'foto_perfil' in data:
        usuario_atual.foto_perfil = data['foto_perfil']
    
    # Atualizar campos específicos conforme o tipo de usuário
    if usuario_atual.tipo == 'profissional':
        if 'descricao' in data:
            usuario_atual.descricao = data['descricao']
        if 'anos_experiencia' in data:
            usuario_atual.anos_experiencia = data['anos_experiencia']
        if 'regiao_atuacao' in data:
            usuario_atual.regiao_atuacao = data['regiao_atuacao']
        if 'disponibilidade' in data:
            usuario_atual.disponibilidade = data['disponibilidade']
    elif usuario_atual.tipo == 'cliente':
        if 'endereco' in data:
            usuario_atual.endereco = data['endereco']
        if 'preferencias' in data:
            usuario_atual.preferencias = data['preferencias']
    
    # Salvar alterações
    db.session.commit()
    
    return jsonify({
        'mensagem': 'Perfil atualizado com sucesso',
        'usuario': usuario_atual.to_dict()
    }), 200