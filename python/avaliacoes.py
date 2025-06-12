from flask import Blueprint, request, jsonify
from src.models.models import db, Avaliacao, Usuario
from src.routes.auth import token_required

avaliacoes_bp = Blueprint('avaliacoes', __name__)

# Rota para criar uma nova avaliação
@avaliacoes_bp.route('/', methods=['POST'])
@token_required
def criar_avaliacao(usuario_atual):
    # Verificar se o usuário é um cliente
    if usuario_atual.tipo != 'cliente':
        return jsonify({'erro': 'Apenas clientes podem criar avaliações'}), 403
    
    data = request.get_json()
    
    # Verificar se todos os campos obrigatórios estão presentes
    if not all(k in data for k in ['id_profissional', 'pontuacao']):
        return jsonify({'erro': 'Dados incompletos'}), 400
    
    # Verificar se a pontuação é válida (1-5)
    if not 1 <= data['pontuacao'] <= 5:
        return jsonify({'erro': 'Pontuação deve ser entre 1 e 5'}), 400
    
    # Verificar se o profissional existe
    profissional = Usuario.query.filter_by(id=data['id_profissional'], tipo='profissional').first()
    if not profissional:
        return jsonify({'erro': 'Profissional não encontrado'}), 404
    
    # Verificar se o cliente já avaliou este profissional
    avaliacao_existente = Avaliacao.query.filter_by(
        id_cliente=usuario_atual.id,
        id_profissional=data['id_profissional']
    ).first()
    
    if avaliacao_existente:
        return jsonify({'erro': 'Você já avaliou este profissional'}), 400
    
    # Criar nova avaliação
    nova_avaliacao = Avaliacao(
        id_profissional=data['id_profissional'],
        id_cliente=usuario_atual.id,
        pontuacao=data['pontuacao'],
        comentario=data.get('comentario', ''),
        servico_realizado=data.get('servico_realizado', '')
    )
    
    # Salvar na base de dados
    db.session.add(nova_avaliacao)
    db.session.commit()
    
    return jsonify({
        'mensagem': 'Avaliação criada com sucesso',
        'avaliacao': nova_avaliacao.to_dict()
    }), 201

# Rota para obter avaliações de um profissional
@avaliacoes_bp.route('/profissional/<int:profissional_id>', methods=['GET'])
def obter_avaliacoes_profissional(profissional_id):
    # Verificar se o profissional existe
    profissional = Usuario.query.filter_by(id=profissional_id, tipo='profissional').first()
    if not profissional:
        return jsonify({'erro': 'Profissional não encontrado'}), 404
    
    # Obter avaliações
    avaliacoes = profissional.avaliacoes_recebidas.all()
    resultado = [a.to_dict() for a in avaliacoes]
    
    # Calcular média
    media = profissional.get_avaliacao_media()
    
    return jsonify({
        'avaliacoes': resultado,
        'total': len(resultado),
        'media': media
    }), 200

# Rota para obter avaliações feitas por um cliente
@avaliacoes_bp.route('/cliente', methods=['GET'])
@token_required
def obter_avaliacoes_cliente(usuario_atual):
    # Verificar se o usuário é um cliente
    if usuario_atual.tipo != 'cliente':
        return jsonify({'erro': 'Apenas clientes podem acessar suas avaliações'}), 403
    
    # Obter avaliações
    avaliacoes = usuario_atual.avaliacoes_feitas.all()
    resultado = [a.to_dict() for a in avaliacoes]
    
    return jsonify({
        'avaliacoes': resultado,
        'total': len(resultado)
    }), 200

# Rota para atualizar uma avaliação
@avaliacoes_bp.route('/<int:avaliacao_id>', methods=['PUT'])
@token_required
def atualizar_avaliacao(usuario_atual, avaliacao_id):
    # Verificar se o usuário é um cliente
    if usuario_atual.tipo != 'cliente':
        return jsonify({'erro': 'Apenas clientes podem atualizar avaliações'}), 403
    
    # Verificar se a avaliação existe e pertence ao cliente
    avaliacao = Avaliacao.query.filter_by(id=avaliacao_id, id_cliente=usuario_atual.id).first()
    if not avaliacao:
        return jsonify({'erro': 'Avaliação não encontrada ou não pertence a este cliente'}), 404
    
    data = request.get_json()
    
    # Atualizar campos
    if 'pontuacao' in data:
        if not 1 <= data['pontuacao'] <= 5:
            return jsonify({'erro': 'Pontuação deve ser entre 1 e 5'}), 400
        avaliacao.pontuacao = data['pontuacao']
    
    if 'comentario' in data:
        avaliacao.comentario = data['comentario']
    
    if 'servico_realizado' in data:
        avaliacao.servico_realizado = data['servico_realizado']
    
    # Salvar alterações
    db.session.commit()
    
    return jsonify({
        'mensagem': 'Avaliação atualizada com sucesso',
        'avaliacao': avaliacao.to_dict()
    }), 200

# Rota para excluir uma avaliação
@avaliacoes_bp.route('/<int:avaliacao_id>', methods=['DELETE'])
@token_required
def excluir_avaliacao(usuario_atual, avaliacao_id):
    # Verificar se o usuário é um cliente
    if usuario_atual.tipo != 'cliente':
        return jsonify({'erro': 'Apenas clientes podem excluir avaliações'}), 403
    
    # Verificar se a avaliação existe e pertence ao cliente
    avaliacao = Avaliacao.query.filter_by(id=avaliacao_id, id_cliente=usuario_atual.id).first()
    if not avaliacao:
        return jsonify({'erro': 'Avaliação não encontrada ou não pertence a este cliente'}), 404
    
    # Excluir avaliação
    db.session.delete(avaliacao)
    db.session.commit()
    
    return jsonify({
        'mensagem': 'Avaliação excluída com sucesso'
    }), 200