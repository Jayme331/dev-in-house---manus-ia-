// Função para lidar com registro
function handleRegister(e) {
    e.preventDefault();
    
    const nome = document.getElementById('nome').value;
    const email = document.getElementById('email').value;
    const senha = document.getElementById('senha').value;
    const confirmarSenha = document.getElementById('confirmar-senha').value;
    const tipo = document.querySelector('input[name="tipo"]:checked')?.value;
    
    // Validação básica
    if (!nome || !email || !senha || !confirmarSenha || !tipo) {
        const errorElement = document.getElementById('register-error');
        if (errorElement) {
            errorElement.textContent = 'Por favor, preencha todos os campos.';
            errorElement.style.display = 'block';
        }
        return;
    }
    
    if (senha !== confirmarSenha) {
        const errorElement = document.getElementById('register-error');
        if (errorElement) {
            errorElement.textContent = 'As senhas não coincidem.';
            errorElement.style.display = 'block';
        }
        return;
    }
    
    // Simulação de registro
    setTimeout(function() {
        // Simular dados do usuário
        const userData = {
            id: 1,
            nome: nome,
            email: email,
            tipo: tipo
        };
        
        // Salvar token e dados do usuário
        localStorage.setItem('auth_token', 'token_simulado_' + Date.now());
        localStorage.setItem('user_data', JSON.stringify(userData));
        
        // Redirecionar para a página inicial
        window.location.href = '/';
    }, 1000);
}

// Função para lidar com contato
function handleContact(e) {
    e.preventDefault();
    
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const message = document.getElementById('message').value;
    
    // Validação básica
    if (!name || !email || !message) {
        const errorElement = document.getElementById('form-error');
        if (errorElement) {
            errorElement.textContent = 'Por favor, preencha todos os campos obrigatórios.';
            errorElement.style.display = 'block';
        }
        return;
    }
    
    // Simulação de envio
    setTimeout(function() {
        const successElement = document.getElementById('form-success');
        if (successElement) {
            successElement.style.display = 'block';
            document.getElementById('contact-form').reset();
            
            // Ocultar mensagem após 5 segundos
            setTimeout(function() {
                successElement.style.display = 'none';
            }, 5000);
        }
    }, 1000);
}

// Função para logout
function logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    window.location.href = '/';
}

// Função para criar estrelas de avaliação
function createRatingStars(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
    
    let starsHTML = '';
    
    // Estrelas cheias
    for (let i = 0; i < fullStars; i++) {
        starsHTML += '<i class="fas fa-star"></i>';
    }
    
    // Meia estrela
    if (hasHalfStar) {
        starsHTML += '<i class="fas fa-star-half-alt"></i>';
    }
    
    // Estrelas vazias
    for (let i = 0; i < emptyStars; i++) {
        starsHTML += '<i class="far fa-star"></i>';
    }
    
    return starsHTML;
}

// Função para carregar especialidades
function loadSpecialties() {
    // Em um ambiente real, isso seria uma chamada de API
    const specialties = [
        { id: 1, nome: 'Pedreiro', categoria: 'Construção' },
        { id: 2, nome: 'Eletricista', categoria: 'Instalações' },
        { id: 3, nome: 'Encanador', categoria: 'Instalações' },
        { id: 4, nome: 'Pintor', categoria: 'Acabamento' },
        { id: 5, nome: 'Carpinteiro', categoria: 'Acabamento' },
        { id: 6, nome: 'Serralheiro', categoria: 'Acabamento' },
        { id: 7, nome: 'Gesseiro', categoria: 'Acabamento' },
        { id: 8, nome: 'Jardineiro', categoria: 'Exterior' },
        { id: 9, nome: 'Arquiteto', categoria: 'Projeto' },
        { id: 10, nome: 'Engenheiro Civil', categoria: 'Projeto' }
    ];
    
    const specialtySelect = document.getElementById('filter-specialty');
    
    if (specialtySelect) {
        specialties.forEach(specialty => {
            const option = document.createElement('option');
            option.value = specialty.id;
            option.textContent = specialty.nome;
            specialtySelect.appendChild(option);
        });
    }
}

// Função para carregar profissionais simulados
function loadProfessionals(filters = {}, page = 1, sortBy = 'relevancia') {
    // Em um ambiente real, isso seria uma chamada de API
    const professionals = [
        {
            id: 1,
            nome: 'João Silva',
            foto_perfil: 'https://images.unsplash.com/photo-1560250097-0b93528c311a?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
            especialidades: ['Pedreiro', 'Construção'],
            avaliacao_media: 4.5,
            regiao_atuacao: 'Lisboa',
            anos_experiencia: 15,
            descricao: 'Especialista em construção e reformas com mais de 15 anos de experiência. Trabalho com alvenaria, fundações e acabamentos.'
        },
        {
            id: 2,
            nome: 'Ana Oliveira',
            foto_perfil: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
            especialidades: ['Arquiteta', 'Projeto'],
            avaliacao_media: 5.0,
            regiao_atuacao: 'Porto',
            anos_experiencia: 8,
            descricao: 'Arquiteta com foco em projetos residenciais e comerciais. Especialista em design de interiores e otimização de espaços.'
        },
        {
            id: 3,
            nome: 'Carlos Santos',
            foto_perfil: 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
            especialidades: ['Eletricista', 'Instalações'],
            avaliacao_media: 4.0,
            regiao_atuacao: 'Braga',
            anos_experiencia: 10,
            descricao: 'Eletricista certificado com experiência em instalações residenciais e comerciais. Especialista em instalações elétricas e manutenção.'
        }
    ];
    
    // Simular filtros
    let filteredProfessionals = [...professionals];
    
    // Aplicar filtros
    if (filters.especialidade) {
        // Simulação simples
        if (filters.especialidade === '1') {
            filteredProfessionals = filteredProfessionals.filter(p => p.especialidades.includes('Pedreiro'));
        } else if (filters.especialidade === '2') {
            filteredProfessionals = filteredProfessionals.filter(p => p.especialidades.includes('Eletricista'));
        }
    }
    
    if (filters.regiao && filters.regiao.trim() !== '') {
        filteredProfessionals = filteredProfessionals.filter(p => 
            p.regiao_atuacao.toLowerCase().includes(filters.regiao.toLowerCase())
        );
    }
    
    if (filters.avaliacao_min) {
        filteredProfessionals = filteredProfessionals.filter(p => 
            p.avaliacao_media >= parseInt(filters.avaliacao_min)
        );
    }
    
    // Ordenar profissionais
    if (sortBy === 'avaliacao') {
        filteredProfessionals.sort((a, b) => b.avaliacao_media - a.avaliacao_media);
    } else if (sortBy === 'experiencia') {
        filteredProfessionals.sort((a, b) => b.anos_experiencia - a.anos_experiencia);
    }
    
    // Simular paginação
    const itemsPerPage = 10;
    const startIndex = (page - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedProfessionals = filteredProfessionals.slice(startIndex, endIndex);
    
    return {
        profissionais: paginatedProfessionals,
        total: filteredProfessionals.length
    };
}