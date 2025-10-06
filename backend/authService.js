/**
 * Serviço de Autenticação - Quantum Finance
 * Gerencia login, logout, sessões e validações de usuário
 */

class AuthService {
    constructor() {
        this.currentUser = null;
        this.sessionKey = 'quantum_trades_session';
        this.userKey = 'quantum_trades_user';
        this.rememberKey = 'quantum_trades_remember';
        
        // Usuários de demonstração
        this.demoUsers = [
            {
                id: 1,
                name: 'Administrador',
                email: 'admin@quantumtrades.com',
                password: 'admin123',
                role: 'admin',
                avatar: 'src/assets/avatars/admin.png'
            },
            {
                id: 2,
                name: 'Usuário Demo',
                email: 'demo@quantumtrades.com',
                password: 'demo123',
                role: 'user',
                avatar: 'src/assets/avatars/user.png'
            },
            {
                id: 3,
                name: 'Investidor',
                email: 'user@quantumtrades.com',
                password: 'user123',
                role: 'investor',
                avatar: 'src/assets/avatars/investor.png'
            }
        ];
        
        this.loadUserFromStorage();
    }

    /**
     * Realiza login do usuário
     * @param {string} email 
     * @param {string} password 
     * @param {boolean} rememberMe 
     * @returns {Promise<Object>}
     */
    async login(email, password, rememberMe = false) {
        try {
            // Simular delay de rede
            await this.delay(1000);
            
            // Validar credenciais
            const user = this.demoUsers.find(u => 
                u.email.toLowerCase() === email.toLowerCase() && 
                u.password === password
            );
            
            if (!user) {
                throw new Error('E-mail ou senha incorretos');
            }
            
            // Criar sessão
            const sessionData = {
                user: {
                    id: user.id,
                    name: user.name,
                    email: user.email,
                    role: user.role,
                    avatar: user.avatar
                },
                loginTime: new Date().toISOString(),
                expiresAt: new Date(Date.now() + (rememberMe ? 30 * 24 * 60 * 60 * 1000 : 24 * 60 * 60 * 1000)).toISOString()
            };
            
            // Salvar sessão
            localStorage.setItem(this.sessionKey, JSON.stringify(sessionData));
            
            if (rememberMe) {
                localStorage.setItem(this.rememberKey, 'true');
                localStorage.setItem(this.userKey, JSON.stringify(sessionData.user));
            } else {
                localStorage.removeItem(this.rememberKey);
                sessionStorage.setItem(this.userKey, JSON.stringify(sessionData.user));
            }
            
            this.currentUser = sessionData.user;
            
            return {
                success: true,
                user: sessionData.user,
                message: `Bem-vindo, ${user.name}!`
            };
            
        } catch (error) {
            return {
                success: false,
                message: error.message
            };
        }
    }

    /**
     * Realiza logout do usuário
     */
    logout() {
        this.currentUser = null;
        localStorage.removeItem(this.sessionKey);
        localStorage.removeItem(this.userKey);
        sessionStorage.removeItem(this.userKey);
        
        // Redirecionar para login
        window.location.href = 'login.html';
    }

    /**
     * Verifica se o usuário está logado
     * @returns {boolean}
     */
    isLoggedIn() {
        if (!this.currentUser) {
            return false;
        }
        
        const session = this.getSession();
        if (!session) {
            return false;
        }
        
        // Verificar se a sessão expirou
        if (new Date() > new Date(session.expiresAt)) {
            this.logout();
            return false;
        }
        
        return true;
    }

    /**
     * Obtém dados da sessão atual
     * @returns {Object|null}
     */
    getSession() {
        try {
            const sessionData = localStorage.getItem(this.sessionKey);
            return sessionData ? JSON.parse(sessionData) : null;
        } catch (error) {
            console.error('Erro ao carregar sessão:', error);
            return null;
        }
    }

    /**
     * Obtém usuário atual
     * @returns {Object|null}
     */
    getCurrentUser() {
        return this.currentUser;
    }

    /**
     * Carrega usuário do storage
     */
    loadUserFromStorage() {
        try {
            const session = this.getSession();
            if (session && new Date() <= new Date(session.expiresAt)) {
                this.currentUser = session.user;
            } else {
                // Tentar carregar de remember me
                const rememberMe = localStorage.getItem(this.rememberKey);
                if (rememberMe === 'true') {
                    const userData = localStorage.getItem(this.userKey);
                    if (userData) {
                        this.currentUser = JSON.parse(userData);
                    }
                }
            }
        } catch (error) {
            console.error('Erro ao carregar usuário:', error);
            this.currentUser = null;
        }
    }

    /**
     * Valida formato de email
     * @param {string} email 
     * @returns {boolean}
     */
    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    /**
     * Valida força da senha
     * @param {string} password 
     * @returns {Object}
     */
    validatePassword(password) {
        const minLength = 6;
        const hasUpperCase = /[A-Z]/.test(password);
        const hasLowerCase = /[a-z]/.test(password);
        const hasNumbers = /\d/.test(password);
        const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
        
        const score = [
            password.length >= minLength,
            hasUpperCase,
            hasLowerCase,
            hasNumbers,
            hasSpecialChar
        ].filter(Boolean).length;
        
        let strength = 'weak';
        if (score >= 4) strength = 'strong';
        else if (score >= 3) strength = 'medium';
        
        return {
            isValid: password.length >= minLength,
            strength,
            score,
            requirements: {
                minLength: password.length >= minLength,
                hasUpperCase,
                hasLowerCase,
                hasNumbers,
                hasSpecialChar
            }
        };
    }

    /**
     * Simula delay de rede
     * @param {number} ms 
     * @returns {Promise}
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Recuperação de senha (simulada)
     * @param {string} email 
     * @returns {Promise<Object>}
     */
    async forgotPassword(email) {
        try {
            await this.delay(1500);
            
            const user = this.demoUsers.find(u => 
                u.email.toLowerCase() === email.toLowerCase()
            );
            
            if (!user) {
                throw new Error('E-mail não encontrado em nossa base de dados');
            }
            
            // Simular envio de email
            return {
                success: true,
                message: 'Instruções de recuperação enviadas para seu e-mail'
            };
            
        } catch (error) {
            return {
                success: false,
                message: error.message
            };
        }
    }

    /**
     * Registro de novo usuário (simulado)
     * @param {Object} userData 
     * @returns {Promise<Object>}
     */
    async register(userData) {
        try {
            await this.delay(1500);
            
            // Verificar se email já existe
            const existingUser = this.demoUsers.find(u => 
                u.email.toLowerCase() === userData.email.toLowerCase()
            );
            
            if (existingUser) {
                throw new Error('Este e-mail já está cadastrado');
            }
            
            // Validar dados
            if (!this.validateEmail(userData.email)) {
                throw new Error('E-mail inválido');
            }
            
            const passwordValidation = this.validatePassword(userData.password);
            if (!passwordValidation.isValid) {
                throw new Error('Senha deve ter pelo menos 6 caracteres');
            }
            
            // Simular criação de usuário
            const newUser = {
                id: this.demoUsers.length + 1,
                name: userData.name,
                email: userData.email,
                password: userData.password,
                role: 'user',
                avatar: 'src/assets/avatars/default.png'
            };
            
            this.demoUsers.push(newUser);
            
            return {
                success: true,
                message: 'Conta criada com sucesso! Faça login para continuar.'
            };
            
        } catch (error) {
            return {
                success: false,
                message: error.message
            };
        }
    }

    /**
     * Atualiza dados do usuário
     * @param {Object} userData 
     * @returns {Promise<Object>}
     */
    async updateProfile(userData) {
        try {
            await this.delay(1000);
            
            if (!this.isLoggedIn()) {
                throw new Error('Usuário não autenticado');
            }
            
            // Atualizar dados do usuário atual
            this.currentUser = { ...this.currentUser, ...userData };
            
            // Atualizar storage
            const session = this.getSession();
            if (session) {
                session.user = this.currentUser;
                localStorage.setItem(this.sessionKey, JSON.stringify(session));
            }
            
            return {
                success: true,
                user: this.currentUser,
                message: 'Perfil atualizado com sucesso!'
            };
            
        } catch (error) {
            return {
                success: false,
                message: error.message
            };
        }
    }
}

// Instância global do serviço de autenticação
window.authService = new AuthService();

