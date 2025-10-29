"""
Análise Fundamental de Criptomoedas - Magnus Wealth v8.4.0
Integra dados on-chain, desenvolvimento do projeto e métricas fundamentalistas
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
import json

class AnaliseFundamental:
    """
    Análise fundamental de criptomoedas
    Combina métricas on-chain e desenvolvimento do projeto
    """
    
    def __init__(self):
        # APIs gratuitas (sem necessidade de chave)
        self.coingecko_api = "https://api.coingecko.com/api/v3"
        self.github_api = "https://api.github.com"
        
        # Mapeamento de criptos para IDs CoinGecko
        self.coingecko_ids = {
            'Bitcoin': 'bitcoin',
            'Ethereum': 'ethereum',
            'Binance Coin': 'binancecoin',
            'Solana': 'solana',
            'Chainlink': 'chainlink',
            'Uniswap': 'uniswap',
            'Algorand': 'algorand',
            'VeChain': 'vechain',
            'Cardano': 'cardano',
            'Avalanche': 'avalanche-2',
            'Polygon': 'matic-network',
            'Polkadot': 'polkadot',
            'Litecoin': 'litecoin',
            'Cosmos': 'cosmos',
            'Stellar': 'stellar',
            'Filecoin': 'filecoin',
            'Hedera': 'hedera-hashgraph',
            'Cronos': 'crypto-com-chain',
            'Near Protocol': 'near',
            'Aptos': 'aptos',
            'Arbitrum': 'arbitrum',
            'Optimism': 'optimism',
            'Immutable': 'immutable-x'
        }
        
        # Mapeamento para repositórios GitHub principais
        self.github_repos = {
            'Bitcoin': 'bitcoin/bitcoin',
            'Ethereum': 'ethereum/go-ethereum',
            'Solana': 'solana-labs/solana',
            'Chainlink': 'smartcontractkit/chainlink',
            'Uniswap': 'Uniswap/v3-core',
            'Algorand': 'algorand/go-algorand',
            'VeChain': 'vechain/thor',
            'Cardano': 'input-output-hk/cardano-node',
            'Avalanche': 'ava-labs/avalanchego',
            'Polygon': 'maticnetwork/bor',
            'Polkadot': 'paritytech/polkadot',
            'Cosmos': 'cosmos/cosmos-sdk',
            'Near Protocol': 'near/nearcore',
            'Aptos': 'aptos-labs/aptos-core'
        }
    
    def buscar_dados_coingecko(self, cripto_name: str) -> Dict:
        """
        Busca dados fundamentais do CoinGecko
        """
        try:
            coin_id = self.coingecko_ids.get(cripto_name)
            if not coin_id:
                print(f"   ⚠️  {cripto_name} não mapeado no CoinGecko")
                return None
            
            # Dados gerais
            url = f"{self.coingecko_api}/coins/{coin_id}"
            params = {
                'localization': 'false',
                'tickers': 'false',
                'community_data': 'true',
                'developer_data': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                print(f"   ❌ Erro CoinGecko: {response.status_code}")
                return None
            
            data = response.json()
            
            # Extrair métricas relevantes
            market_data = data.get('market_data', {})
            community = data.get('community_data', {})
            developer = data.get('developer_data', {})
            
            metricas = {
                # Métricas de mercado
                'market_cap': market_data.get('market_cap', {}).get('usd', 0),
                'market_cap_rank': data.get('market_cap_rank', 0),
                'volume_24h': market_data.get('total_volume', {}).get('usd', 0),
                'volume_market_cap_ratio': 0,
                
                # Métricas de preço
                'ath': market_data.get('ath', {}).get('usd', 0),
                'ath_change_pct': market_data.get('ath_change_percentage', {}).get('usd', 0),
                'atl': market_data.get('atl', {}).get('usd', 0),
                'atl_change_pct': market_data.get('atl_change_percentage', {}).get('usd', 0),
                
                # Métricas de comunidade
                'twitter_followers': community.get('twitter_followers', 0),
                'reddit_subscribers': community.get('reddit_subscribers', 0),
                'telegram_users': community.get('telegram_channel_user_count', 0),
                
                # Métricas de desenvolvimento
                'github_forks': developer.get('forks', 0),
                'github_stars': developer.get('stars', 0),
                'github_subscribers': developer.get('subscribers', 0),
                'github_commits_4w': developer.get('commit_count_4_weeks', 0),
                'github_contributors': developer.get('total_issues', 0),
                
                # Sentimento
                'sentiment_votes_up_pct': data.get('sentiment_votes_up_percentage', 0),
                'sentiment_votes_down_pct': data.get('sentiment_votes_down_percentage', 0)
            }
            
            # Calcular ratio volume/market cap
            if metricas['market_cap'] > 0:
                metricas['volume_market_cap_ratio'] = metricas['volume_24h'] / metricas['market_cap']
            
            return metricas
            
        except Exception as e:
            print(f"   ❌ Erro ao buscar CoinGecko: {str(e)[:100]}")
            return None
    
    def buscar_dados_github(self, cripto_name: str) -> Dict:
        """
        Busca dados de desenvolvimento do GitHub
        """
        try:
            repo = self.github_repos.get(cripto_name)
            if not repo:
                return None
            
            # Dados do repositório
            url = f"{self.github_api}/repos/{repo}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            # Commits recentes (últimos 30 dias)
            since = (datetime.now() - timedelta(days=30)).isoformat()
            commits_url = f"{self.github_api}/repos/{repo}/commits"
            commits_response = requests.get(commits_url, params={'since': since}, timeout=10)
            
            num_commits_30d = len(commits_response.json()) if commits_response.status_code == 200 else 0
            
            return {
                'stars': data.get('stargazers_count', 0),
                'forks': data.get('forks_count', 0),
                'watchers': data.get('watchers_count', 0),
                'open_issues': data.get('open_issues_count', 0),
                'commits_30d': num_commits_30d,
                'last_update': data.get('updated_at', ''),
                'language': data.get('language', '')
            }
            
        except Exception as e:
            print(f"   ⚠️  Erro ao buscar GitHub: {str(e)[:50]}")
            return None
    
    def calcular_score_fundamental(self, metricas: Dict) -> float:
        """
        Calcula score fundamental (0-100)
        """
        if not metricas:
            return 0
        
        score = 0
        
        # 1. Market Cap Rank (20 pontos)
        rank = metricas.get('market_cap_rank', 100)
        if rank <= 10:
            score += 20
        elif rank <= 30:
            score += 15
        elif rank <= 50:
            score += 10
        elif rank <= 100:
            score += 5
        
        # 2. Liquidez (Volume/Market Cap) (15 pontos)
        ratio = metricas.get('volume_market_cap_ratio', 0)
        if ratio > 0.1:  # > 10%
            score += 15
        elif ratio > 0.05:
            score += 10
        elif ratio > 0.02:
            score += 5
        
        # 3. Desenvolvimento GitHub (25 pontos)
        commits = metricas.get('github_commits_4w', 0)
        if commits > 100:
            score += 15
        elif commits > 50:
            score += 10
        elif commits > 20:
            score += 5
        
        stars = metricas.get('github_stars', 0)
        if stars > 10000:
            score += 10
        elif stars > 5000:
            score += 5
        
        # 4. Comunidade (20 pontos)
        twitter = metricas.get('twitter_followers', 0)
        if twitter > 1000000:
            score += 10
        elif twitter > 500000:
            score += 7
        elif twitter > 100000:
            score += 4
        
        reddit = metricas.get('reddit_subscribers', 0)
        if reddit > 500000:
            score += 10
        elif reddit > 100000:
            score += 7
        elif reddit > 50000:
            score += 4
        
        # 5. Sentimento (10 pontos)
        sentiment = metricas.get('sentiment_votes_up_pct', 0)
        if sentiment > 70:
            score += 10
        elif sentiment > 60:
            score += 7
        elif sentiment > 50:
            score += 4
        
        # 6. Distância do ATH (10 pontos)
        ath_change = metricas.get('ath_change_pct', 0)
        if ath_change > -20:  # Menos de 20% abaixo do ATH
            score += 10
        elif ath_change > -50:
            score += 7
        elif ath_change > -70:
            score += 4
        
        return min(score, 100)
    
    def analisar_cripto(self, cripto_name: str) -> Dict:
        """
        Análise fundamental completa de uma criptomoeda
        """
        print(f"\n🔍 Analisando {cripto_name}...")
        
        # Buscar dados
        metricas_cg = self.buscar_dados_coingecko(cripto_name)
        metricas_gh = self.buscar_dados_github(cripto_name)
        
        if not metricas_cg:
            return None
        
        # Combinar métricas
        if metricas_gh:
            metricas_cg.update({
                'github_stars_atual': metricas_gh['stars'],
                'github_commits_30d': metricas_gh['commits_30d'],
                'github_open_issues': metricas_gh['open_issues']
            })
        
        # Calcular score
        score = self.calcular_score_fundamental(metricas_cg)
        
        return {
            'cripto': cripto_name,
            'score_fundamental': score,
            'metricas': metricas_cg,
            'data_analise': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def gerar_relatorio(self, resultado: Dict) -> str:
        """Gera relatório de análise fundamental"""
        if not resultado:
            return "❌ Sem dados disponíveis"
        
        msg = f"\n{'='*60}\n"
        msg += f"📊 ANÁLISE FUNDAMENTAL: {resultado['cripto']}\n"
        msg += f"{'='*60}\n\n"
        
        msg += f"**SCORE FUNDAMENTAL:** {resultado['score_fundamental']:.1f}/100\n\n"
        
        metricas = resultado['metricas']
        
        msg += "**MERCADO:**\n"
        msg += f"   • Rank: #{metricas.get('market_cap_rank', 'N/A')}\n"
        msg += f"   • Market Cap: ${metricas.get('market_cap', 0):,.0f}\n"
        msg += f"   • Volume 24h: ${metricas.get('volume_24h', 0):,.0f}\n"
        msg += f"   • Volume/MCap: {metricas.get('volume_market_cap_ratio', 0)*100:.2f}%\n\n"
        
        msg += "**PREÇO:**\n"
        msg += f"   • ATH: ${metricas.get('ath', 0):,.2f}\n"
        msg += f"   • Distância ATH: {metricas.get('ath_change_pct', 0):.1f}%\n"
        msg += f"   • ATL: ${metricas.get('atl', 0):,.6f}\n"
        msg += f"   • Distância ATL: {metricas.get('atl_change_pct', 0):.1f}%\n\n"
        
        msg += "**DESENVOLVIMENTO:**\n"
        msg += f"   • GitHub Stars: {metricas.get('github_stars', 0):,}\n"
        msg += f"   • GitHub Forks: {metricas.get('github_forks', 0):,}\n"
        msg += f"   • Commits (4 semanas): {metricas.get('github_commits_4w', 0):,}\n"
        if 'github_commits_30d' in metricas:
            msg += f"   • Commits (30 dias): {metricas['github_commits_30d']:,}\n"
        msg += "\n"
        
        msg += "**COMUNIDADE:**\n"
        msg += f"   • Twitter: {metricas.get('twitter_followers', 0):,} seguidores\n"
        msg += f"   • Reddit: {metricas.get('reddit_subscribers', 0):,} membros\n"
        telegram = metricas.get('telegram_users') or 0
        if telegram > 0:
            msg += f"   • Telegram: {telegram:,} usuários\n"
        msg += "\n"
        
        msg += "**SENTIMENTO:**\n"
        msg += f"   • Positivo: {metricas.get('sentiment_votes_up_pct', 0):.1f}%\n"
        msg += f"   • Negativo: {metricas.get('sentiment_votes_down_pct', 0):.1f}%\n"
        
        msg += f"\n{'='*60}\n"
        
        return msg

if __name__ == "__main__":
    print("\n" + "="*60)
    print("ANÁLISE FUNDAMENTAL - Magnus Wealth v8.4.0")
    print("="*60)
    
    analise = AnaliseFundamental()
    
    # Analisar Bitcoin
    resultado = analise.analisar_cripto('Bitcoin')
    if resultado:
        print(analise.gerar_relatorio(resultado))
    
    # Analisar Solana
    resultado = analise.analisar_cripto('Solana')
    if resultado:
        print(analise.gerar_relatorio(resultado))
