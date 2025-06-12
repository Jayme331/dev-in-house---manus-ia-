from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Tabela de associação entre profissionais e especialidades
profissional_especialidade = db.Table('profissional_especialidade',
    db.Column('profissional_id', db.Integer, db.ForeignKey('usuario.id'), primary_key=True),
    db.Column('especialidade_id', db.Integer, db.ForeignKey('especialidade.id'), primary_key=True)
)

class Usuario(db.Model):
    __tablename__ = 'usuario'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'cliente' ou 'profissional'
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    telefone = db.Column(db.String(20))
    foto_perfil = db.Column(db.String(200))
    
    # Campos específicos para profissionais
    descricao = db.Column(db.Text)
    anos_experiencia = db.Column(db.Integer)
    regiao_atuacao = db.Column(db.String(100))
    disponibilidade = db.Column(db.String(100))
    
    # Campos específicos para clientes
    endereco = db.Column(db.String(200))
    preferencias = db.Column(db.Text)
    
    # Relacionamentos
    especialidades = db.relationship('Especialidade', secondary=profissional_especialidade,
                                    backref=db.backref('profissionais', lazy='dynamic'))
    avaliacoes_recebidas = db.relationship('Avaliacao', foreign_keys='Avaliacao.id_profissional',
                                         backref='profissional', lazy='dynamic')
    avaliacoes_feitas = db.relationship('Avaliacao', foreign_keys='Avaliacao.id_cliente',
                                      backref='cliente', lazy='dynamic')
    portfolio = db.relationship('Portfolio', backref='profissional', lazy='dynamic')
    
    def __init__(self, nome, email, senha, tipo):
        self.nome = nome
        self.email = email
        self.set_senha(senha)
        self.tipo = tipo
    
    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)
        
    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)
    
    def to_dict(self):
        data = {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'tipo': self.tipo,
            'data_cadastro': self.data_cadastro.isoformat(),
            'telefone': self.telefone,
            'foto_perfil': self.foto_perfil
        }
        
        if self.tipo == 'profissional':
            data.update({
                'descricao': self.descricao,
                'anos_experiencia': self.anos_experiencia,
                'regiao_atuacao': self.regiao_atuacao,
                'disponibilidade': self.disponibilidade,
                'especialidades': [e.nome for e in self.especialidades],
                'avaliacao_media': self.get_avaliacao_media()
            })
        elif self.tipo == 'cliente':
            data.update({
                'endereco': self.endereco,
                'preferencias': self.preferencias
            })
            
        return data
    
    def get_avaliacao_media(self):
        avaliacoes = self.avaliacoes_recebidas.all()
        if not avaliacoes:
            return 0
        return sum(a.pontuacao for a in avaliacoes) / len(avaliacoes)


class Especialidade(db.Model):
    __tablename__ = 'especialidade'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'categoria': self.categoria,
            'descricao': self.descricao
        }


class Avaliacao(db.Model):
    __tablename__ = 'avaliacao'
    
    id = db.Column(db.Integer, primary_key=True)
    id_profissional = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    id_cliente = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    pontuacao = db.Column(db.Integer, nullable=False)  # 1-5 estrelas
    comentario = db.Column(db.Text)
    data_avaliacao = db.Column(db.DateTime, default=datetime.utcnow)
    servico_realizado = db.Column(db.String(200))
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_profissional': self.id_profissional,
            'id_cliente': self.id_cliente,
            'nome_cliente': self.cliente.nome,
            'pontuacao': self.pontuacao,
            'comentario': self.comentario,
            'data_avaliacao': self.data_avaliacao.isoformat(),
            'servico_realizado': self.servico_realizado
        }


class Portfolio(db.Model):
    __tablename__ = 'portfolio'
    
    id = db.Column(db.Integer, primary_key=True)
    id_profissional = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    imagem = db.Column(db.String(200), nullable=False)
    data_adicao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_profissional': self.id_profissional,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'imagem': self.imagem,
            'data_adicao': self.data_adicao.isoformat()
        }