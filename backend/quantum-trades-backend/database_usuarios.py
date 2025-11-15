#!/usr/bin/env python3
"""
Banco de Dados de Usuários - Magnus Wealth v9.0.0
Gerencia usuários cadastrados e autorizados
"""

import json
import os
from datetime import datetime
from typing import Optional, Dict, List
import hashlib
import secrets

# Arquivo de banco de dados
DB_FILE = 'usuarios_magnus.json'

class DatabaseUsuarios:
    """
    Gerencia usuários cadastrados no Magnus Wealth
    """
    
    def __init__(self, db_file: str = DB_FILE):
        self.db_file = db_file
        self.usuarios = self._carregar_db()
    
    def _carregar_db(self) -> Dict:
        """Carrega banco de dados do arquivo"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {'usuarios': [], 'codigos_pendentes': {}}
        return {'usuarios': [], 'codigos_pendentes': {}}
    
    def _salvar_db(self):
        """Salva banco de dados no arquivo"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.usuarios, f, indent=2, ensure_ascii=False)
    
    def gerar_codigo_acesso(self, nome: str, email: str, plano: str = 'basico') -> str:
        """
        Gera código de acesso único para novo usuário
        
        Args:
            nome: Nome do usuário
            email: Email do usuário
            plano: Plano contratado (basico, premium, vip)
        
        Returns:
            Código de acesso (ex: MAGNUS-A1B2C3D4)
        """
        # Gerar código único
        codigo = f"MAGNUS-{secrets.token_hex(4).upper()}"
        
        # Verificar se código já existe
        while codigo in self.usuarios['codigos_pendentes']:
            codigo = f"MAGNUS-{secrets.token_hex(4).upper()}"
        
        # Salvar código pendente
        self.usuarios['codigos_pendentes'][codigo] = {
            'nome': nome,
            'email': email,
            'plano': plano,
            'data_geracao': datetime.now().isoformat(),
            'usado': False
        }
        
        self._salvar_db()
        
        return codigo
    
    def validar_codigo(self, codigo: str, telegram_user_id: int, username: str = None) -> bool:
        """
        Valida código de acesso e cadastra usuário
        
        Args:
            codigo: Código de acesso (ex: MAGNUS-A1B2C3D4)
            telegram_user_id: ID do usuário no Telegram
            username: Username do Telegram (opcional)
        
        Returns:
            True se código válido e usuário cadastrado
        """
        # Verificar se código existe e não foi usado
        if codigo not in self.usuarios['codigos_pendentes']:
            return False
        
        codigo_info = self.usuarios['codigos_pendentes'][codigo]
        
        if codigo_info['usado']:
            return False
        
        # Verificar se user_id já está cadastrado
        if self.usuario_existe(telegram_user_id):
            return False
        
        # Cadastrar usuário
        usuario = {
            'telegram_user_id': telegram_user_id,
            'telegram_username': username,
            'nome': codigo_info['nome'],
            'email': codigo_info['email'],
            'plano': codigo_info['plano'],
            'codigo_usado': codigo,
            'data_cadastro': datetime.now().isoformat(),
            'ativo': True,
            'grupo_adicionado': False
        }
        
        self.usuarios['usuarios'].append(usuario)
        
        # Marcar código como usado
        self.usuarios['codigos_pendentes'][codigo]['usado'] = True
        self.usuarios['codigos_pendentes'][codigo]['telegram_user_id'] = telegram_user_id
        self.usuarios['codigos_pendentes'][codigo]['data_uso'] = datetime.now().isoformat()
        
        self._salvar_db()
        
        return True
    
    def usuario_existe(self, telegram_user_id: int) -> bool:
        """Verifica se usuário já está cadastrado"""
        for usuario in self.usuarios['usuarios']:
            if usuario['telegram_user_id'] == telegram_user_id:
                return True
        return False
    
    def usuario_autorizado(self, telegram_user_id: int) -> bool:
        """Verifica se usuário está autorizado (cadastrado e ativo)"""
        for usuario in self.usuarios['usuarios']:
            if usuario['telegram_user_id'] == telegram_user_id:
                return usuario.get('ativo', False)
        return False
    
    def obter_usuario(self, telegram_user_id: int) -> Optional[Dict]:
        """Obtém informações do usuário"""
        for usuario in self.usuarios['usuarios']:
            if usuario['telegram_user_id'] == telegram_user_id:
                return usuario
        return None
    
    def marcar_grupo_adicionado(self, telegram_user_id: int):
        """Marca que usuário foi adicionado ao grupo"""
        for usuario in self.usuarios['usuarios']:
            if usuario['telegram_user_id'] == telegram_user_id:
                usuario['grupo_adicionado'] = True
                usuario['data_adicao_grupo'] = datetime.now().isoformat()
                break
        self._salvar_db()
    
    def desativar_usuario(self, telegram_user_id: int):
        """Desativa usuário"""
        for usuario in self.usuarios['usuarios']:
            if usuario['telegram_user_id'] == telegram_user_id:
                usuario['ativo'] = False
                usuario['data_desativacao'] = datetime.now().isoformat()
                break
        self._salvar_db()
    
    def listar_usuarios(self, apenas_ativos: bool = False) -> List[Dict]:
        """Lista todos os usuários"""
        if apenas_ativos:
            return [u for u in self.usuarios['usuarios'] if u.get('ativo', False)]
        return self.usuarios['usuarios']
    
    def listar_codigos_pendentes(self) -> List[Dict]:
        """Lista códigos ainda não usados"""
        pendentes = []
        for codigo, info in self.usuarios['codigos_pendentes'].items():
            if not info['usado']:
                pendentes.append({'codigo': codigo, **info})
        return pendentes
    
    def estatisticas(self) -> Dict:
        """Retorna estatísticas do banco de dados"""
        total_usuarios = len(self.usuarios['usuarios'])
        usuarios_ativos = len([u for u in self.usuarios['usuarios'] if u.get('ativo', False)])
        total_codigos = len(self.usuarios['codigos_pendentes'])
        codigos_usados = len([c for c in self.usuarios['codigos_pendentes'].values() if c['usado']])
        codigos_pendentes = total_codigos - codigos_usados
        
        return {
            'total_usuarios': total_usuarios,
            'usuarios_ativos': usuarios_ativos,
            'usuarios_inativos': total_usuarios - usuarios_ativos,
            'total_codigos_gerados': total_codigos,
            'codigos_usados': codigos_usados,
            'codigos_pendentes': codigos_pendentes
        }


# Funções de conveniência
def gerar_codigo(nome: str, email: str, plano: str = 'basico') -> str:
    """Gera código de acesso"""
    db = DatabaseUsuarios()
    return db.gerar_codigo_acesso(nome, email, plano)


def validar_codigo(codigo: str, telegram_user_id: int, username: str = None) -> bool:
    """Valida código e cadastra usuário"""
    db = DatabaseUsuarios()
    return db.validar_codigo(codigo, telegram_user_id, username)


def usuario_autorizado(telegram_user_id: int) -> bool:
    """Verifica se usuário está autorizado"""
    db = DatabaseUsuarios()
    return db.usuario_autorizado(telegram_user_id)


if __name__ == '__main__':
    """
    Teste e gerenciamento do banco de dados
    """
    import sys
    
    db = DatabaseUsuarios()
    
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        
        if comando == 'gerar':
            # Gerar código
            if len(sys.argv) < 4:
                print("Uso: python3 database_usuarios.py gerar <nome> <email> [plano]")
                sys.exit(1)
            
            nome = sys.argv[2]
            email = sys.argv[3]
            plano = sys.argv[4] if len(sys.argv) > 4 else 'basico'
            
            codigo = db.gerar_codigo_acesso(nome, email, plano)
            print(f"\n✅ Código gerado com sucesso!")
            print(f"📋 Código: {codigo}")
            print(f"👤 Nome: {nome}")
            print(f"📧 Email: {email}")
            print(f"💎 Plano: {plano}")
            print(f"\n📤 Envie este código para o usuário usar no bot do Telegram")
        
        elif comando == 'listar':
            # Listar usuários
            usuarios = db.listar_usuarios()
            print(f"\n📊 USUÁRIOS CADASTRADOS ({len(usuarios)})")
            print("=" * 80)
            for u in usuarios:
                status = "✅ Ativo" if u.get('ativo') else "❌ Inativo"
                print(f"\n👤 {u['nome']}")
                print(f"   Telegram ID: {u['telegram_user_id']}")
                print(f"   Username: @{u.get('telegram_username', 'N/A')}")
                print(f"   Email: {u['email']}")
                print(f"   Plano: {u['plano']}")
                print(f"   Status: {status}")
                print(f"   Cadastro: {u['data_cadastro'][:10]}")
        
        elif comando == 'pendentes':
            # Listar códigos pendentes
            pendentes = db.listar_codigos_pendentes()
            print(f"\n📋 CÓDIGOS PENDENTES ({len(pendentes)})")
            print("=" * 80)
            for p in pendentes:
                print(f"\n🔑 {p['codigo']}")
                print(f"   Nome: {p['nome']}")
                print(f"   Email: {p['email']}")
                print(f"   Plano: {p['plano']}")
                print(f"   Gerado em: {p['data_geracao'][:10]}")
        
        elif comando == 'stats':
            # Estatísticas
            stats = db.estatisticas()
            print(f"\n📊 ESTATÍSTICAS DO SISTEMA")
            print("=" * 80)
            print(f"👥 Total de usuários: {stats['total_usuarios']}")
            print(f"✅ Usuários ativos: {stats['usuarios_ativos']}")
            print(f"❌ Usuários inativos: {stats['usuarios_inativos']}")
            print(f"🔑 Códigos gerados: {stats['total_codigos_gerados']}")
            print(f"✅ Códigos usados: {stats['codigos_usados']}")
            print(f"⏳ Códigos pendentes: {stats['codigos_pendentes']}")
        
        else:
            print(f"❌ Comando desconhecido: {comando}")
            print("\nComandos disponíveis:")
            print("  gerar <nome> <email> [plano]  - Gerar código de acesso")
            print("  listar                         - Listar usuários cadastrados")
            print("  pendentes                      - Listar códigos pendentes")
            print("  stats                          - Estatísticas do sistema")
    
    else:
        # Modo interativo
        print("=" * 80)
        print("GERENCIADOR DE USUÁRIOS - MAGNUS WEALTH")
        print("=" * 80)
        
        stats = db.estatisticas()
        print(f"\n📊 Estatísticas:")
        print(f"   👥 Usuários: {stats['total_usuarios']} ({stats['usuarios_ativos']} ativos)")
        print(f"   🔑 Códigos: {stats['codigos_pendentes']} pendentes")
        
        print("\n" + "=" * 80)
        print("COMANDOS DISPONÍVEIS")
        print("=" * 80)
        print("\n1. Gerar código de acesso:")
        print("   python3 database_usuarios.py gerar 'João Silva' 'joao@email.com' premium")
        print("\n2. Listar usuários:")
        print("   python3 database_usuarios.py listar")
        print("\n3. Listar códigos pendentes:")
        print("   python3 database_usuarios.py pendentes")
        print("\n4. Ver estatísticas:")
        print("   python3 database_usuarios.py stats")
