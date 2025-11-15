#!/usr/bin/env python3
"""
Script de Inicialização e Validação do Sistema Magnus Wealth v9.0.0

Verifica e prepara o ambiente para execução do sistema completo
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

class InicializadorSistema:
    """
    Inicializa e valida o sistema Magnus Wealth
    """
    
    def __init__(self):
        self.erros = []
        self.avisos = []
        self.sucessos = []
        self.base_dir = Path(__file__).parent
    
    def executar(self):
        """
        Executa todas as verificações e inicializações
        """
        print("=" * 80)
        print("INICIALIZAÇÃO DO SISTEMA MAGNUS WEALTH v9.0.0")
        print("=" * 80)
        print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print()
        
        # Etapa 1: Verificar Python e dependências
        print("\n📦 ETAPA 1: Verificando Python e Dependências")
        print("-" * 80)
        self._verificar_python()
        self._verificar_dependencias()
        
        # Etapa 2: Verificar estrutura de diretórios
        print("\n📁 ETAPA 2: Verificando Estrutura de Diretórios")
        print("-" * 80)
        self._verificar_diretorios()
        
        # Etapa 3: Verificar arquivos de configuração
        print("\n⚙️  ETAPA 3: Verificando Arquivos de Configuração")
        print("-" * 80)
        self._verificar_configuracoes()
        
        # Etapa 4: Verificar variáveis de ambiente
        print("\n🔐 ETAPA 4: Verificando Variáveis de Ambiente")
        print("-" * 80)
        self._verificar_env()
        
        # Etapa 5: Verificar módulos do sistema
        print("\n🐍 ETAPA 5: Verificando Módulos do Sistema")
        print("-" * 80)
        self._verificar_modulos()
        
        # Etapa 6: Verificar portfolio
        print("\n💼 ETAPA 6: Verificando Portfólio")
        print("-" * 80)
        self._verificar_portfolio()
        
        # Relatório final
        print("\n" + "=" * 80)
        print("RELATÓRIO FINAL")
        print("=" * 80)
        self._exibir_relatorio()
        
        return len(self.erros) == 0
    
    def _verificar_python(self):
        """Verifica versão do Python"""
        versao = sys.version_info
        if versao.major == 3 and versao.minor >= 11:
            self.sucessos.append(f"✅ Python {versao.major}.{versao.minor}.{versao.micro}")
        else:
            self.erros.append(f"❌ Python 3.11+ necessário (atual: {versao.major}.{versao.minor}.{versao.micro})")
    
    def _verificar_dependencias(self):
        """Verifica dependências instaladas"""
        dependencias = [
            'yfinance',
            'pandas',
            'numpy',
            'sklearn',
            'joblib',
            'requests',
            'pytz'
        ]
        
        for dep in dependencias:
            try:
                __import__(dep)
                self.sucessos.append(f"✅ {dep}")
            except ImportError:
                self.erros.append(f"❌ {dep} não instalado")
    
    def _verificar_diretorios(self):
        """Verifica e cria diretórios necessários"""
        diretorios = [
            'ml_data_8anos',
            'ml_models',
            'logs'
        ]
        
        for dir_name in diretorios:
            dir_path = self.base_dir / dir_name
            if dir_path.exists():
                self.sucessos.append(f"✅ {dir_name}/")
            else:
                dir_path.mkdir(parents=True, exist_ok=True)
                self.avisos.append(f"⚠️  {dir_name}/ criado")
    
    def _verificar_configuracoes(self):
        """Verifica arquivos de configuração"""
        # portfolio_config.json
        config_path = self.base_dir / 'portfolio_config.json'
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                self.sucessos.append(f"✅ portfolio_config.json válido")
            except json.JSONDecodeError:
                self.erros.append(f"❌ portfolio_config.json inválido")
        else:
            self.erros.append(f"❌ portfolio_config.json não encontrado")
        
        # config_ordens.json
        ordens_path = self.base_dir / 'config_ordens.json'
        if ordens_path.exists():
            try:
                with open(ordens_path, 'r') as f:
                    config = json.load(f)
                self.sucessos.append(f"✅ config_ordens.json válido")
            except json.JSONDecodeError:
                self.erros.append(f"❌ config_ordens.json inválido")
        else:
            self.avisos.append(f"⚠️  config_ordens.json não encontrado (será criado)")
    
    def _verificar_env(self):
        """Verifica variáveis de ambiente"""
        variaveis = [
            'TELEGRAM_BOT_TOKEN',
            'TELEGRAM_CHAT_ID',
            'TELEGRAM_USER_ID'
        ]
        
        # Tentar carregar .env
        env_path = self.base_dir / '.env'
        if env_path.exists():
            self.sucessos.append(f"✅ .env encontrado")
            
            # Verificar variáveis
            with open(env_path, 'r') as f:
                env_content = f.read()
            
            for var in variaveis:
                if var in env_content:
                    # Verificar se não está vazio
                    if f"{var}=" in env_content and not f"{var}=\n" in env_content:
                        self.sucessos.append(f"✅ {var} configurado")
                    else:
                        self.avisos.append(f"⚠️  {var} vazio")
                else:
                    self.avisos.append(f"⚠️  {var} não encontrado")
        else:
            self.erros.append(f"❌ .env não encontrado")
    
    def _verificar_modulos(self):
        """Verifica módulos do sistema"""
        modulos = [
            'portfolio_manager.py',
            'coletor_dados_ml_8anos.py',
            'treinar_modelo_inversao.py',
            'monitor_multitimeframe.py',
            'analisador_criterios.py',
            'executador_ordens.py',
            'sistema_ordens_magnus.py',
            'otimizador_quinzenal_v9.py'
        ]
        
        for modulo in modulos:
            modulo_path = self.base_dir / modulo
            if modulo_path.exists():
                # Verificar se é executável
                if os.access(modulo_path, os.X_OK):
                    self.sucessos.append(f"✅ {modulo} (executável)")
                else:
                    self.avisos.append(f"⚠️  {modulo} (não executável)")
            else:
                self.erros.append(f"❌ {modulo} não encontrado")
    
    def _verificar_portfolio(self):
        """Verifica configuração do portfólio"""
        try:
            from portfolio_manager import PortfolioManager
            
            manager = PortfolioManager()
            criptos_ativas = manager.obter_criptos_ativas()
            stats = manager.obter_estatisticas()
            
            self.sucessos.append(f"✅ Portfolio Manager funcional")
            self.sucessos.append(f"✅ {len(criptos_ativas)} criptomoedas ativas")
            self.sucessos.append(f"✅ Alocação total: {stats['alocacao_total']*100:.0f}%")
            
            # Verificar se há criptos
            if len(criptos_ativas) == 0:
                self.erros.append(f"❌ Nenhuma criptomoeda ativa no portfólio")
            elif len(criptos_ativas) < 5:
                self.avisos.append(f"⚠️  Apenas {len(criptos_ativas)} criptos (mínimo recomendado: 5)")
            
        except Exception as e:
            self.erros.append(f"❌ Erro ao verificar portfolio: {e}")
    
    def _exibir_relatorio(self):
        """Exibe relatório final"""
        print(f"\n✅ SUCESSOS: {len(self.sucessos)}")
        for sucesso in self.sucessos:
            print(f"   {sucesso}")
        
        if self.avisos:
            print(f"\n⚠️  AVISOS: {len(self.avisos)}")
            for aviso in self.avisos:
                print(f"   {aviso}")
        
        if self.erros:
            print(f"\n❌ ERROS: {len(self.erros)}")
            for erro in self.erros:
                print(f"   {erro}")
        
        print("\n" + "=" * 80)
        if len(self.erros) == 0:
            print("✅ SISTEMA PRONTO PARA USO!")
        else:
            print("❌ SISTEMA COM ERROS - CORRIJA ANTES DE USAR")
        print("=" * 80)


def main():
    """
    Função principal
    """
    inicializador = InicializadorSistema()
    sucesso = inicializador.executar()
    
    sys.exit(0 if sucesso else 1)


if __name__ == '__main__':
    main()
