from flask import Blueprint, request, jsonify
from models import db, Usuario, Especialidade
from .routes.auth import token_required

profissionais_bp = Blueprint('profissionais', __name__)

# Rota para listar todos os profissionais
@profissionais_bp.route('/', methods=['GET'])
def listar_profissionais():
    # Parâmetros de filtro
    especialidade_id = request.args.get('especialidade_id', type=int)
    regiao = request.args.get('regiao')
    avaliacao_min = request.args.get('avaliacao_min', type=float)
    
    # Query base
    query = Usuario.query.filter_by(tipo='profissional')
    
    # Aplicar filtros
    if especialidade_id:
        query = query.filter(Usuario.especialidades.any(id=especialidade_id))
    
    if regiao:
        query = query.filter(Usuario.regiao_atuacao.like(f'%{regiao}%'))
    
    # Executar query
    profissionais = query.all()
    
    # Filtrar por avaliação mínima (feito após a query pois requer cálculo)
    if avaliacao_min:
        profissionais = [p for p in profissionais if p.get_avaliacao_media() >= avaliacao_min]
    
    # Converter para dicionários
    resultado = [p.to_dict() for p in profissionais]
    
    return jsonify({
        'profissionais': resultado,
        'total': len(resultado)
    }), 200

# Rota para obter detalhes de um profissional específico
@profissionais_bp.route('/<int:profissional_id>', methods=['GET'])
def obter_profissional(profissional_id):
    profissional = Usuario.query.filter_by(id=profissional_id, tipo='profissional').first()
    
    if not profissional:
        return jsonify({'erro': 'Profissional não encontrado'}), 404
    
    # Obter detalhes completos
    detalhes = profissional.to_dict()
    
    # Adicionar avaliações
    avaliacoes = [a.to_dict() for a in profissional.avaliacoes_recebidas.all()]
    detalhes['avaliacoes'] = avaliacoes
    
    # Adicionar portfólio
    portfolio = [p.to_dict() for p in profissional.portfolio.all()]
    detalhes['portfolio'] = portfolio
    
    return jsonify(detalhes), 200

# Rota para listar todas as especialidades
@profissionais_bp.route('/especialidades', methods=['GET'])
def listar_especialidades():
    especialidades = Especialidade.query.all()
    resultado = [e.to_dict() for e in especialidades]
    
    return jsonify({
        'especialidades': resultado,
        'total': len(resultado)
    }), 200

# Rota para busca de profissionais por termo
@profissionais_bp.route('/busca', methods=['GET'])
def buscar_profissionais():
    termo = request.args.get('q', '')
    
    if not termo:
        return jsonify({'erro': 'Termo de busca não fornecido'}), 400
    
    # Buscar por nome, descrição ou especialidades
    profissionais = Usuario.query.filter(
        Usuario.tipo == 'profissional',
        (
            Usuario.nome.like(f'%{termo}%') |
            Usuario.descricao.like(f'%{termo}%') |
            Usuario.especialidades.any(Especialidade.nome.like(f'%{termo}%'))
        )
    ).all()
    
    resultado = [p.to_dict() for p in profissionais]
    
    return jsonify({
        'profissionais': resultado,
        'total': len(resultado),
        'termo': termo
    }), 200

# Rota para adicionar especialidade a um profissional
@profissionais_bp.route('/especialidades/<int:especialidade_id>', methods=['POST'])
@token_required
def adicionar_especialidade(usuario_atual, especialidade_id):
    # Verificar se o usuário é um profissional
    if usuario_atual.tipo != 'profissional':
        return jsonify({'erro': 'Apenas profissionais podem adicionar especialidades'}), 403
    
    # Verificar se a especialidade existe
    especialidade = Especialidade.query.get(especialidade_id)
    if not especialidade:
        return jsonify({'erro': 'Especialidade não encontrada'}), 404
    
    # Verificar se o profissional já possui esta especialidade
    if especialidade in usuario_atual.especialidades:
        return jsonify({'erro': 'Especialidade já adicionada'}), 400
    
    # Adicionar especialidade ao profissional
    usuario_atual.especialidades.append(especialidade)
    db.session.commit()
    
    return jsonify({
        'mensagem': 'Especialidade adicionada com sucesso',
        'especialidades': [e.to_dict() for e in usuario_atual.especialidades]
    }), 200

# Rota para remover especialidade de um profissional
@profissionais_bp.route('/especialidades/<int:especialidade_id>', methods=['DELETE'])
@token_required
def remover_especialidade(usuario_atual, especialidade_id):
    # Verificar se o usuário é um profissional
    if usuario_atual.tipo != 'profissional':
        return jsonify({'erro': 'Apenas profissionais podem remover especialidades'}), 403
    
    # Verificar se a especialidade existe
    especialidade = Especialidade.query.get(especialidade_id)
    if not especialidade:
        return jsonify({'erro': 'Especialidade não encontrada'}), 404
    
    # Verificar se o profissional possui esta especialidade
    if especialidade not in usuario_atual.especialidades:
        return jsonify({'erro': 'Especialidade não encontrada no perfil'}), 400
    
    # Remover especialidade do profissional
    usuario_atual.especialidades.remove(especialidade)
    db.session.commit()
    
    return jsonify({
        'mensagem': 'Especialidade removida com sucesso',
        'especialidades': [e.to_dict() for e in usuario_atual.especialidades]
    }), 200