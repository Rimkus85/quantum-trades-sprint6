"""
Integrador de carteiras do Telegram com Magnus Learning.
Processa carteiras XLSX e alimenta o sistema de aprendizado.
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from modules.xlsx_processor import XLSXProcessor
from modules.magnus_advanced_learning import MagnusAdvancedLearning, Position


class CarteiraIntegrator:
    """Integra carteiras do Telegram ao Magnus Learning."""
    
    def __init__(self):
        """Inicializa o integrador."""
        self.processor = XLSXProcessor()
        self.magnus = MagnusAdvancedLearning()
        self.carteiras_processadas = []
    
    def process_and_integrate(self) -> Dict:
        """
        Processa carteiras e integra ao Magnus Learning.
        
        Returns:
            Estatísticas do processamento
        """
        print("=" * 80)
        print("INTEGRAÇÃO: CARTEIRAS TELEGRAM → MAGNUS LEARNING")
        print("=" * 80)
        
        # Processar arquivos XLSX
        print("\n📊 Fase 1: Processando arquivos XLSX...")
        self.carteiras_processadas = self.processor.process_all_files()
        
        if not self.carteiras_processadas:
            print("⚠ Nenhuma carteira processada")
            return {}
        
        # Integrar ao Magnus
        print(f"\n🧠 Fase 2: Integrando ao Magnus Learning...")
        stats = self._integrate_to_magnus()
        
        # Salvar estado
        print(f"\n💾 Fase 3: Salvando estado...")
        self.magnus.save_state('magnus_carteiras_state.json')
        self.processor.save_to_json('carteiras_processadas.json')
        
        print(f"\n" + "=" * 80)
        print("✅ INTEGRAÇÃO CONCLUÍDA")
        print("=" * 80)
        
        return stats
    
    def _integrate_to_magnus(self) -> Dict:
        """
        Integra carteiras ao Magnus Learning.
        
        Returns:
            Estatísticas da integração
        """
        stats = {
            'total_carteiras': 0,
            'total_posicoes_criadas': 0,
            'tickers_unicos': set(),
            'carteiras_por_tipo': {}
        }
        
        for carteira_file in self.carteiras_processadas:
            data = carteira_file['data']
            tipo_arquivo = carteira_file['tipo']
            
            for tipo_carteira, ativos in carteira_file.get('carteiras', {}).items():
                stats['total_carteiras'] += 1
                
                # Contabilizar por tipo
                key = f"{tipo_arquivo}_{tipo_carteira}"
                if key not in stats['carteiras_por_tipo']:
                    stats['carteiras_por_tipo'][key] = 0
                stats['carteiras_por_tipo'][key] += 1
                
                print(f"\n  📁 {data} - {tipo_arquivo} - {tipo_carteira}")
                print(f"     {len(ativos)} ativos")
                
                # Criar posições no Magnus
                for ativo in ativos:
                    ticker = ativo['ticker']
                    percentual = ativo['percentual']
                    nome = ativo['nome']
                    
                    stats['tickers_unicos'].add(ticker)
                    
                    # Criar posição
                    position = self._create_position_from_ativo(
                        ticker=ticker,
                        nome=nome,
                        percentual=percentual,
                        data=data,
                        tipo_carteira=tipo_carteira
                    )
                    
                    if position:
                        self.magnus.performance_tracker.add_position(position)
                        stats['total_posicoes_criadas'] += 1
        
        # Converter set para int
        stats['tickers_unicos'] = len(stats['tickers_unicos'])
        
        print(f"\n  ✓ {stats['total_posicoes_criadas']} posições criadas")
        print(f"  ✓ {stats['tickers_unicos']} tickers únicos")
        
        return stats
    
    def _create_position_from_ativo(
        self,
        ticker: str,
        nome: str,
        percentual: float,
        data: str,
        tipo_carteira: str
    ) -> Optional[Position]:
        """
        Cria uma posição do Magnus a partir de um ativo da carteira.
        
        Args:
            ticker: Ticker do ativo
            nome: Nome do ativo
            percentual: Percentual de alocação
            data: Data da carteira
            tipo_carteira: Tipo (AGRESSIVA ou MODERADA)
            
        Returns:
            Position ou None
        """
        try:
            # Data de entrada
            entry_date = datetime.strptime(data, '%Y-%m-%d')
            
            # Validade: 90 dias (3 meses)
            validity_date = entry_date + timedelta(days=90)
            
            # Preço de entrada (simulado - seria obtido de API)
            entry_price = 100.0
            
            # Quantidade baseada no percentual
            # Assumindo carteira de R$ 100.000
            capital_total = 100000.0
            valor_alocado = capital_total * (percentual / 100)
            quantity = int(valor_alocado / entry_price)
            
            # Meta: +20% em 3 meses
            target_price = entry_price * 1.20
            
            # Stop loss: -10%
            stop_loss = entry_price * 0.90
            
            # Setor (seria obtido de API)
            sector = self._get_sector_from_ticker(ticker)
            
            position = Position(
                ticker=ticker,
                entry_date=entry_date.isoformat(),
                entry_price=entry_price,
                quantity=quantity,
                target_price=target_price,
                stop_loss=stop_loss,
                expected_return=20.0,
                timeframe_days=90,
                validity_date=validity_date.isoformat(),
                reason=f"Carteira {tipo_carteira} - {nome} ({percentual:.2f}%)",
                sector=sector
            )
            
            return position
            
        except Exception as e:
            print(f"    ⚠ Erro ao criar posição para {ticker}: {e}")
            return None
    
    def _get_sector_from_ticker(self, ticker: str) -> str:
        """
        Identifica setor baseado no ticker.
        
        Args:
            ticker: Ticker do ativo
            
        Returns:
            Nome do setor
        """
        # Mapeamento simplificado
        setores = {
            'PETR': 'petroleo',
            'VALE': 'mineracao',
            'ITUB': 'financeiro',
            'BBDC': 'financeiro',
            'BBAS': 'financeiro',
            'ABEV': 'consumo',
            'WEGE': 'industrial',
            'IVVB': 'etf_internacional',
            'LFTB': 'renda_fixa',
            'USIM': 'siderurgia',
            'GOAU': 'siderurgia',
            'PRIO': 'petroleo',
            'BRAP': 'mineracao',
            'SMTO': 'agronegocio',
        }
        
        # Extrair código base (primeiros 4 caracteres)
        codigo_base = ticker[:4]
        
        return setores.get(codigo_base, 'outros')
    
    def get_recommendations(self) -> List[Dict]:
        """
        Gera recomendações baseadas nas carteiras integradas.
        
        Returns:
            Lista de recomendações
        """
        recommendations = []
        
        # Obter carteira mais recente
        latest_agressiva = self.processor.get_latest_portfolio('AGRESSIVA')
        latest_moderada = self.processor.get_latest_portfolio('MODERADA')
        
        if latest_agressiva:
            recommendations.append({
                'tipo': 'AGRESSIVA',
                'data': latest_agressiva['data'],
                'ativos': latest_agressiva['ativos'],
                'total_alocado': sum(a['percentual'] for a in latest_agressiva['ativos'])
            })
        
        if latest_moderada:
            recommendations.append({
                'tipo': 'MODERADA',
                'data': latest_moderada['data'],
                'ativos': latest_moderada['ativos'],
                'total_alocado': sum(a['percentual'] for a in latest_moderada['ativos'])
            })
        
        return recommendations


def main():
    """Função principal para teste."""
    integrator = CarteiraIntegrator()
    
    # Processar e integrar
    stats = integrator.process_and_integrate()
    
    # Mostrar estatísticas
    print(f"\n📊 ESTATÍSTICAS FINAIS:")
    print(f"   Total de carteiras: {stats.get('total_carteiras', 0)}")
    print(f"   Posições criadas: {stats.get('total_posicoes_criadas', 0)}")
    print(f"   Tickers únicos: {stats.get('tickers_unicos', 0)}")
    
    print(f"\n   Carteiras por tipo:")
    for tipo, count in stats.get('carteiras_por_tipo', {}).items():
        print(f"     {tipo}: {count}")
    
    # Gerar recomendações
    print(f"\n📈 RECOMENDAÇÕES ATUAIS:")
    recommendations = integrator.get_recommendations()
    
    for rec in recommendations:
        print(f"\n   {rec['tipo']} ({rec['data']}):")
        print(f"     Total alocado: {rec['total_alocado']:.2f}%")
        print(f"     Top 5 ativos:")
        top5 = sorted(rec['ativos'], key=lambda x: x['percentual'], reverse=True)[:5]
        for ativo in top5:
            print(f"       {ativo['ticker']:8} {ativo['percentual']:6.2f}%  {ativo['nome']}")


if __name__ == '__main__':
    main()

