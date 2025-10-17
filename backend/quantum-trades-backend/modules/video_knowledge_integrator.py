"""
Módulo de Integração de Conhecimento de Vídeos
Integra o conhecimento extraído dos vídeos do YouTube ao sistema Magnus Learning
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class VideoKnowledgeIntegrator:
    """Integra conhecimento de vídeos ao Magnus Learning"""
    
    def __init__(self, knowledge_dir: str = None):
        """
        Inicializa o integrador
        
        Args:
            knowledge_dir: Diretório com conhecimento dos vídeos
        """
        if knowledge_dir is None:
            base_dir = Path(__file__).parent.parent
            knowledge_dir = base_dir / 'youtube_knowledge'
        
        self.knowledge_dir = Path(knowledge_dir)
        self.summary_file = self.knowledge_dir / 'summary.json'
        
    def load_summary(self) -> Dict[str, Any]:
        """Carrega resumo do processamento de vídeos"""
        if not self.summary_file.exists():
            return {
                'total_videos': 0,
                'videos': [],
                'average_relevance': 0,
                'total_words': 0
            }
        
        with open(self.summary_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_video_knowledge(self, video_id: str) -> Dict[str, Any]:
        """Carrega conhecimento de um vídeo específico"""
        video_file = self.knowledge_dir / f"{video_id}.json"
        
        if not video_file.exists():
            return None
        
        with open(video_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def extract_strategies(self, videos: List[Dict]) -> List[Dict]:
        """
        Extrai estratégias de investimento dos vídeos
        
        Returns:
            Lista de estratégias identificadas
        """
        strategies = []
        
        for video in videos:
            title = video.get('title', '').lower()
            transcription = video.get('transcription', '').lower()
            
            # Identificar tipo de estratégia
            strategy_type = None
            
            if 'carteira' in title or 'portfolio' in title:
                strategy_type = 'portfolio'
            elif 'aposentar' in title or 'renda' in title:
                strategy_type = 'retirement'
            elif 'etf' in title:
                strategy_type = 'etf'
            elif 'tendência' in title or 'surfar' in title:
                strategy_type = 'trend_following'
            elif 'opção' in title or 'opcoes' in title:
                strategy_type = 'options'
            elif 'queda' in title or 'proteção' in title:
                strategy_type = 'protection'
            
            if strategy_type:
                strategies.append({
                    'type': strategy_type,
                    'video_id': video.get('video_id'),
                    'title': video.get('title'),
                    'relevance': video.get('relevance_score', 0),
                    'keywords': video.get('keyword_count', 0),
                    'source': 'youtube_video',
                    'processed_at': video.get('processed_at')
                })
        
        return strategies
    
    def extract_tickers(self, videos: List[Dict]) -> Dict[str, List[str]]:
        """
        Extrai tickers mencionados nos vídeos
        
        Returns:
            Dicionário com tickers por vídeo
        """
        tickers_by_video = {}
        
        # Padrões comuns de tickers
        ticker_patterns = [
            'PETR4', 'VALE3', 'ITUB4', 'BBDC4', 'ABEV3',
            'MGLU3', 'WEGE3', 'RENT3', 'LREN3', 'GGBR4'
        ]
        
        for video in videos:
            video_id = video.get('video_id')
            transcription = video.get('transcription', '')
            
            found_tickers = []
            for ticker in ticker_patterns:
                if ticker in transcription.upper():
                    found_tickers.append(ticker)
            
            if found_tickers:
                tickers_by_video[video_id] = found_tickers
        
        return tickers_by_video
    
    def extract_concepts(self, videos: List[Dict]) -> List[Dict]:
        """
        Extrai conceitos de investimento dos vídeos
        
        Returns:
            Lista de conceitos identificados
        """
        concepts = []
        
        concept_keywords = {
            'diversificacao': ['diversificação', 'diversificar', 'portfolio', 'carteira'],
            'risco': ['risco', 'volatilidade', 'proteção', 'hedge'],
            'retorno': ['retorno', 'lucro', 'ganho', 'rentabilidade'],
            'analise_tecnica': ['suporte', 'resistência', 'tendência', 'indicador'],
            'analise_fundamentalista': ['valuation', 'lucro', 'receita', 'ebitda'],
            'opcoes': ['call', 'put', 'strike', 'vencimento'],
            'dividendos': ['dividendo', 'provento', 'jscp', 'yield']
        }
        
        for video in videos:
            transcription = video.get('transcription', '').lower()
            
            for concept, keywords in concept_keywords.items():
                count = sum(1 for kw in keywords if kw in transcription)
                
                if count > 0:
                    concepts.append({
                        'concept': concept,
                        'video_id': video.get('video_id'),
                        'title': video.get('title'),
                        'mentions': count,
                        'relevance': video.get('relevance_score', 0)
                    })
        
        return concepts
    
    def generate_magnus_knowledge_base(self) -> Dict[str, Any]:
        """
        Gera base de conhecimento para o Magnus
        
        Returns:
            Base de conhecimento estruturada
        """
        summary = self.load_summary()
        videos = summary.get('videos', [])
        
        # Extrair informações
        strategies = self.extract_strategies(videos)
        tickers = self.extract_tickers(videos)
        concepts = self.extract_concepts(videos)
        
        # Estatísticas
        total_videos = len(videos)
        avg_relevance = summary.get('average_relevance', 0)
        total_words = summary.get('total_words', 0)
        
        # Top vídeos
        top_videos = sorted(videos, key=lambda x: x.get('relevance_score', 0), reverse=True)[:5]
        
        knowledge_base = {
            'metadata': {
                'total_videos_processed': total_videos,
                'total_words_extracted': total_words,
                'average_relevance': avg_relevance,
                'last_update': datetime.now().isoformat(),
                'source': 'telegram_youtube_videos'
            },
            'strategies': {
                'total': len(strategies),
                'by_type': self._group_by_type(strategies),
                'list': strategies
            },
            'tickers': {
                'total_videos_with_tickers': len(tickers),
                'tickers_by_video': tickers
            },
            'concepts': {
                'total': len(concepts),
                'by_concept': self._group_by_concept(concepts),
                'list': concepts
            },
            'top_videos': [
                {
                    'video_id': v.get('video_id'),
                    'title': v.get('title'),
                    'relevance': v.get('relevance_score'),
                    'words': v.get('word_count'),
                    'keywords': v.get('keyword_count')
                }
                for v in top_videos
            ],
            'recommendations': self._generate_recommendations(videos, strategies, concepts)
        }
        
        return knowledge_base
    
    def _group_by_type(self, strategies: List[Dict]) -> Dict[str, int]:
        """Agrupa estratégias por tipo"""
        grouped = {}
        for strategy in strategies:
            strategy_type = strategy.get('type', 'unknown')
            grouped[strategy_type] = grouped.get(strategy_type, 0) + 1
        return grouped
    
    def _group_by_concept(self, concepts: List[Dict]) -> Dict[str, int]:
        """Agrupa conceitos"""
        grouped = {}
        for concept in concepts:
            concept_name = concept.get('concept', 'unknown')
            grouped[concept_name] = grouped.get(concept_name, 0) + concept.get('mentions', 0)
        return grouped
    
    def _generate_recommendations(self, videos: List[Dict], strategies: List[Dict], concepts: List[Dict]) -> List[str]:
        """Gera recomendações baseadas no conhecimento"""
        recommendations = []
        
        # Baseado em estratégias
        strategy_types = [s.get('type') for s in strategies]
        
        if 'portfolio' in strategy_types:
            recommendations.append("Considere diversificar seu portfólio com base nas carteiras recomendadas analisadas")
        
        if 'retirement' in strategy_types:
            recommendations.append("Planeje sua aposentadoria com estratégias de renda passiva identificadas nos vídeos")
        
        if 'trend_following' in strategy_types:
            recommendations.append("Utilize estratégias de seguir tendências para maximizar retornos")
        
        if 'protection' in strategy_types:
            recommendations.append("Implemente proteção de portfólio contra quedas de mercado")
        
        # Baseado em conceitos
        concept_names = [c.get('concept') for c in concepts]
        
        if 'opcoes' in concept_names:
            recommendations.append("Explore estratégias com opções para alavancagem e proteção")
        
        if 'dividendos' in concept_names:
            recommendations.append("Foque em ações pagadoras de dividendos para renda passiva")
        
        return recommendations
    
    def save_knowledge_base(self, output_file: str = None) -> str:
        """
        Salva base de conhecimento em arquivo
        
        Args:
            output_file: Caminho do arquivo de saída
            
        Returns:
            Caminho do arquivo salvo
        """
        if output_file is None:
            output_file = self.knowledge_dir / 'magnus_knowledge_base.json'
        
        knowledge_base = self.generate_magnus_knowledge_base()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge_base, f, indent=2, ensure_ascii=False)
        
        return str(output_file)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do conhecimento"""
        summary = self.load_summary()
        videos = summary.get('videos', [])
        
        return {
            'total_videos': len(videos),
            'total_words': summary.get('total_words', 0),
            'average_relevance': f"{summary.get('average_relevance', 0):.1%}",
            'total_errors': summary.get('total_errors', 0),
            'success_rate': f"{len(videos) / (len(videos) + summary.get('total_errors', 0)):.1%}" if len(videos) > 0 else "0%"
        }


if __name__ == "__main__":
    # Teste do integrador
    integrator = VideoKnowledgeIntegrator()
    
    print("="*60)
    print("Magnus - Integrador de Conhecimento de Vídeos")
    print("="*60)
    print()
    
    # Estatísticas
    stats = integrator.get_statistics()
    print("📊 Estatísticas:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    print()
    
    # Gerar base de conhecimento
    print("🧠 Gerando base de conhecimento...")
    knowledge_file = integrator.save_knowledge_base()
    print(f"✅ Base de conhecimento salva: {knowledge_file}")
    print()
    
    # Mostrar resumo
    kb = integrator.generate_magnus_knowledge_base()
    print("📚 Resumo da Base de Conhecimento:")
    print(f"   Estratégias: {kb['strategies']['total']}")
    print(f"   Conceitos: {kb['concepts']['total']}")
    print(f"   Top Vídeos: {len(kb['top_videos'])}")
    print(f"   Recomendações: {len(kb['recommendations'])}")
    print()
    
    print("✅ Integração concluída!")

