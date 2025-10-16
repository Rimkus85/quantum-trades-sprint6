"""
Processador de arquivos XLSX de carteiras recomendadas.
Extrai informações de alocação das abas AGRESSIVA e MODERADA.
"""

import pandas as pd
import os
import json
from datetime import datetime
from typing import List, Dict, Optional
import re


class XLSXProcessor:
    """Processa arquivos XLSX de carteiras recomendadas."""
    
    def __init__(self, downloads_dir: str = 'downloads/carteiras'):
        """
        Inicializa o processador.
        
        Args:
            downloads_dir: Diretório com arquivos XLSX
        """
        self.downloads_dir = downloads_dir
        self.carteiras = []
    
    def process_all_files(self) -> List[Dict]:
        """
        Processa todos os arquivos XLSX no diretório.
        
        Returns:
            Lista de carteiras processadas
        """
        if not os.path.exists(self.downloads_dir):
            print(f"⚠ Diretório não encontrado: {self.downloads_dir}")
            return []
        
        files = [f for f in os.listdir(self.downloads_dir) if f.endswith('.xlsx')]
        
        print(f"📊 Processando {len(files)} arquivos XLSX...")
        
        for filename in sorted(files, reverse=True):  # Mais recentes primeiro
            filepath = os.path.join(self.downloads_dir, filename)
            try:
                carteira = self.process_file(filepath)
                if carteira:
                    self.carteiras.append(carteira)
            except Exception as e:
                print(f"⚠ Erro ao processar {filename}: {e}")
        
        return self.carteiras
    
    def process_file(self, filepath: str) -> Optional[Dict]:
        """
        Processa um arquivo XLSX individual.
        
        Args:
            filepath: Caminho do arquivo
            
        Returns:
            Dicionário com informações da carteira
        """
        filename = os.path.basename(filepath)
        print(f"\n📄 Processando: {filename}")
        
        # Extrair data do nome do arquivo
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
        if date_match:
            date_str = date_match.group(1)
        else:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        # Extrair tipo de carteira
        carteira_type = "GERAL"
        if "START" in filename.upper() or "MILIONÁRIO" in filename.upper():
            carteira_type = "START_MILIONARIO"
        elif "IFR" in filename.upper():
            carteira_type = "IFR"
        
        try:
            # Ler Excel
            xl = pd.ExcelFile(filepath)
            
            # Procurar abas AGRESSIVA e MODERADA
            carteiras_encontradas = {}
            
            for sheet_name in xl.sheet_names:
                if sheet_name.upper() in ['AGRESSIVA', 'MODERADA']:
                    ativos = self._extract_portfolio_from_sheet(filepath, sheet_name)
                    if ativos:
                        carteiras_encontradas[sheet_name.upper()] = ativos
            
            if not carteiras_encontradas:
                print(f"  ⚠ Nenhuma aba AGRESSIVA ou MODERADA encontrada")
                return None
            
            carteira = {
                'data': date_str,
                'tipo': carteira_type,
                'arquivo': filename,
                'carteiras': carteiras_encontradas,
                'timestamp': datetime.now().isoformat()
            }
            
            # Estatísticas
            for tipo, ativos in carteiras_encontradas.items():
                print(f"  ✓ {tipo}: {len(ativos)} ativos")
                total_percent = sum(a['percentual'] for a in ativos)
                print(f"    Total alocado: {total_percent:.2f}%")
                
                # Top 5
                top_ativos = sorted(ativos, key=lambda x: x['percentual'], reverse=True)[:5]
                print(f"    Top 5:")
                for ativo in top_ativos:
                    print(f"      {ativo['ticker']}: {ativo['percentual']:.2f}%")
            
            return carteira
            
        except Exception as e:
            print(f"  ❌ Erro: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_portfolio_from_sheet(self, filepath: str, sheet_name: str) -> List[Dict]:
        """
        Extrai carteira de uma aba específica.
        
        Args:
            filepath: Caminho do arquivo
            sheet_name: Nome da aba
            
        Returns:
            Lista de ativos
        """
        df = pd.read_excel(filepath, sheet_name=sheet_name, header=None)
        
        ativos = []
        
        # A estrutura é: colunas 4, 5, 6 contêm Nome, Ticker, Percentual
        # Linhas começam em 0
        for idx in range(len(df)):
            try:
                # Tentar extrair ticker da coluna 5
                ticker = str(df.iloc[idx, 5]).strip() if len(df.columns) > 5 else ''
                
                # Validar ticker (formato brasileiro)
                if not re.match(r'^[A-Z]{4}\d{1,2}$', ticker):
                    continue
                
                # Extrair nome (coluna 4)
                nome = str(df.iloc[idx, 4]).strip() if len(df.columns) > 4 else ''
                
                # Extrair percentual (coluna 6)
                percentual = 0.0
                if len(df.columns) > 6:
                    try:
                        percent_val = df.iloc[idx, 6]
                        if pd.notna(percent_val):
                            percent_float = float(percent_val)
                            # Converter para percentual se necessário
                            if percent_float <= 1:
                                percentual = percent_float * 100
                            else:
                                percentual = percent_float
                    except:
                        pass
                
                ativo = {
                    'ticker': ticker,
                    'nome': nome,
                    'percentual': percentual
                }
                
                ativos.append(ativo)
                
            except Exception as e:
                continue
        
        return ativos
    
    def save_to_json(self, output_file: str = 'carteiras_processadas.json'):
        """
        Salva carteiras processadas em JSON.
        
        Args:
            output_file: Arquivo de saída
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.carteiras, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Carteiras salvas em: {output_file}")
    
    def get_latest_portfolio(self, tipo: str = 'AGRESSIVA') -> Optional[Dict]:
        """
        Retorna a carteira mais recente de um tipo específico.
        
        Args:
            tipo: Tipo de carteira (AGRESSIVA ou MODERADA)
            
        Returns:
            Dicionário com a carteira mais recente
        """
        if not self.carteiras:
            return None
        
        # Encontrar carteira mais recente que tenha o tipo solicitado
        for carteira in sorted(self.carteiras, key=lambda x: x['data'], reverse=True):
            if tipo in carteira.get('carteiras', {}):
                return {
                    'data': carteira['data'],
                    'tipo': carteira['tipo'],
                    'arquivo': carteira['arquivo'],
                    'ativos': carteira['carteiras'][tipo]
                }
        
        return None
    
    def get_all_tickers(self, tipo: Optional[str] = None) -> List[str]:
        """
        Retorna lista de todos os tickers únicos.
        
        Args:
            tipo: Filtrar por tipo de carteira (AGRESSIVA ou MODERADA)
            
        Returns:
            Lista de tickers
        """
        tickers = set()
        for carteira in self.carteiras:
            for cart_tipo, ativos in carteira.get('carteiras', {}).items():
                if tipo is None or cart_tipo == tipo:
                    for ativo in ativos:
                        tickers.add(ativo['ticker'])
        
        return sorted(list(tickers))
    
    def get_ticker_history(self, ticker: str, tipo: Optional[str] = None) -> List[Dict]:
        """
        Retorna histórico de um ticker específico.
        
        Args:
            ticker: Ticker do ativo
            tipo: Filtrar por tipo de carteira
            
        Returns:
            Lista com histórico de alocações
        """
        history = []
        
        for carteira in sorted(self.carteiras, key=lambda x: x['data']):
            for cart_tipo, ativos in carteira.get('carteiras', {}).items():
                if tipo is None or cart_tipo == tipo:
                    for ativo in ativos:
                        if ativo['ticker'] == ticker:
                            history.append({
                                'data': carteira['data'],
                                'tipo_arquivo': carteira['tipo'],
                                'tipo_carteira': cart_tipo,
                                'percentual': ativo['percentual'],
                                'nome': ativo['nome']
                            })
                            break
        
        return history


def main():
    """Função principal para teste."""
    processor = XLSXProcessor()
    
    print("=" * 80)
    print("PROCESSADOR DE CARTEIRAS XLSX - VERSÃO 2.0")
    print("=" * 80)
    
    # Processar todos os arquivos
    carteiras = processor.process_all_files()
    
    print(f"\n" + "=" * 80)
    print(f"✅ PROCESSAMENTO CONCLUÍDO")
    print(f"   Total de arquivos: {len(carteiras)}")
    print("=" * 80)
    
    # Salvar em JSON
    processor.save_to_json()
    
    # Estatísticas
    all_tickers_agressiva = processor.get_all_tickers('AGRESSIVA')
    all_tickers_moderada = processor.get_all_tickers('MODERADA')
    
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"   Tickers únicos AGRESSIVA: {len(all_tickers_agressiva)}")
    print(f"   Tickers únicos MODERADA: {len(all_tickers_moderada)}")
    
    # Carteira mais recente
    latest_agressiva = processor.get_latest_portfolio('AGRESSIVA')
    if latest_agressiva:
        print(f"\n📅 CARTEIRA AGRESSIVA MAIS RECENTE:")
        print(f"   Data: {latest_agressiva['data']}")
        print(f"   Arquivo: {latest_agressiva['tipo']}")
        print(f"   Ativos: {len(latest_agressiva['ativos'])}")
        total = sum(a['percentual'] for a in latest_agressiva['ativos'])
        print(f"   Total alocado: {total:.2f}%")
        
        print(f"\n   Top 10 alocações:")
        top = sorted(latest_agressiva['ativos'], key=lambda x: x['percentual'], reverse=True)[:10]
        for ativo in top:
            print(f"     {ativo['ticker']:8} {ativo['percentual']:6.2f}%  {ativo['nome']}")
    
    latest_moderada = processor.get_latest_portfolio('MODERADA')
    if latest_moderada:
        print(f"\n📅 CARTEIRA MODERADA MAIS RECENTE:")
        print(f"   Data: {latest_moderada['data']}")
        print(f"   Ativos: {len(latest_moderada['ativos'])}")
        total = sum(a['percentual'] for a in latest_moderada['ativos'])
        print(f"   Total alocado: {total:.2f}%")
    
    # Exemplo de histórico
    if all_tickers_agressiva:
        ticker_exemplo = all_tickers_agressiva[0]
        history = processor.get_ticker_history(ticker_exemplo, 'AGRESSIVA')
        if history:
            print(f"\n📈 HISTÓRICO DE {ticker_exemplo} (AGRESSIVA):")
            for h in history:
                print(f"   {h['data']}: {h['percentual']:.2f}%")


if __name__ == '__main__':
    main()

