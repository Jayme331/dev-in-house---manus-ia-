// Função para mostrar a página correta
        function mostrarPagina(id) {
            document.querySelectorAll(".pagina").forEach(p => p.classList.remove("ativa"));
            document.getElementById(id).classList.add("ativa");
            document.querySelectorAll(".nav-menu a").forEach(a => a.classList.remove("active"));
            const navLink = document.getElementById("nav-" + id);
            if (navLink) navLink.classList.add("active");
            window.scrollTo(0, 0);
        }

        // Função para atualizar a UI com base no estado de login
        function atualizarUIAutenticacao() {
            const loggedInUser = JSON.parse(localStorage.getItem("loggedInUser"));
            const navButtons = document.querySelector(".nav-buttons");
            const userMenu = document.querySelector(".user-menu");

            if (loggedInUser) {
                navButtons.style.display = "none";
                userMenu.style.display = "flex";
                document.getElementById("user-name").textContent = loggedInUser.nome;
            } else {
                navButtons.style.display = "flex";
                userMenu.style.display = "none";
            }
        }

        // Função de Logout
        function logout() {
            localStorage.removeItem("loggedInUser");
            atualizarUIAutenticacao();
            mostrarPagina("inicio"); // Volta para a página inicial
        }

        // Função para lidar com o registo
        function handleRegister(event) {
            event.preventDefault();
            const nome = document.getElementById("register-nome").value;
            const email = document.getElementById("register-email").value;
            const senha = document.getElementById("register-senha").value;
            const confirmarSenha = document.getElementById("register-confirmar-senha").value;
            const tipo = document.querySelector("input[name=\"tipo\"]:checked").value;
            const errorElement = document.getElementById("register-error");

            errorElement.style.display = "none"; // Esconde erro anterior

            if (senha !== confirmarSenha) {
                errorElement.textContent = "As senhas não coincidem.";
                errorElement.style.display = "block";
                return;
            }

            let users = JSON.parse(localStorage.getItem("users")) || [];

            // Verificar se o email já existe
            if (users.some(user => user.email === email)) {
                errorElement.textContent = "Este email já está registado.";
                errorElement.style.display = "block";
                return;
            }

            // Adicionar novo utilizador (simulação de hash de senha)
            const newUser = { id: Date.now(), nome, email, senha, tipo }; // Em produção, a senha deve ser hasheada
            users.push(newUser);
            localStorage.setItem("users", JSON.stringify(users));

            // Login automático após registo
            localStorage.setItem("loggedInUser", JSON.stringify(newUser));
            atualizarUIAutenticacao();
            mostrarPagina("inicio"); // Redireciona para a página inicial
        }

        // Função para lidar com o login
        function handleLogin(event) {
            event.preventDefault();
            const email = document.getElementById("login-email").value;
            const senha = document.getElementById("login-senha").value;
            const errorElement = document.getElementById("login-error");

            errorElement.style.display = "none"; // Esconde erro anterior

            let users = JSON.parse(localStorage.getItem("users")) || [];
            const user = users.find(u => u.email === email && u.senha === senha); // Comparação direta de senha (NÃO SEGURO)

            if (user) {
                localStorage.setItem("loggedInUser", JSON.stringify(user));
                atualizarUIAutenticacao();
                mostrarPagina("inicio"); // Redireciona para a página inicial
            } else {
                errorElement.textContent = "Email ou senha inválidos.";
                errorElement.style.display = "block";
            }
        }

        // Configuração inicial e event listeners
        document.addEventListener("DOMContentLoaded", function() {
            // Configuração do menu mobile
            const mobileMenuBtn = document.querySelector(".mobile-menu-btn");
            const navMenu = document.querySelector(".nav-menu");
            if (mobileMenuBtn && navMenu) {
                mobileMenuBtn.addEventListener("click", function() {
                    navMenu.classList.toggle("active");
                });
            }

            // Configurar formulário de contacto
            const contactForm = document.getElementById("contact-form");
            if (contactForm) {
                contactForm.addEventListener("submit", function(e) {
                    e.preventDefault();
                    setTimeout(function() {
                        document.getElementById("form-success").style.display = "block";
                        contactForm.reset();
                        setTimeout(function() {
                            document.getElementById("form-success").style.display = "none";
                        }, 5000);
                    }, 1000);
                });
            }

            // Configurar formulário de registo
            const registerForm = document.getElementById("register-form");
            if (registerForm) {
                registerForm.addEventListener("submit", handleRegister);
            }

            // Configurar formulário de login
            const loginForm = document.getElementById("login-form");
            if (loginForm) {
                loginForm.addEventListener("submit", handleLogin);
            }

            // Atualizar UI com base no estado de login ao carregar a página
            atualizarUIAutenticacao();
        });