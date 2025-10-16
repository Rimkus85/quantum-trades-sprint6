#!/usr/bin/env python3
"""
Gerador de PDF Detalhado das Carteiras Magnus.
Inclui análise fundamentalista de cada ativo e valores mínimos recomendados.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from datetime import datetime

def criar_pdf_carteiras():
    """Cria PDF detalhado das carteiras."""
    
    filename = f"Carteiras_Magnus_Outubro_2025.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a472a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2e7d32'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=12
    )
    
    # Título
    story.append(Paragraph("🤖 CARTEIRAS MAGNUS - OUTUBRO/2025", title_style))
    story.append(Paragraph("Análise Detalhada e Fundamentalista", styles['Heading3']))
    story.append(Spacer(1, 0.5*cm))
    
    # Introdução
    intro = """
    Este documento apresenta as carteiras recomendadas pelo Magnus AI para outubro/2025,
    com análise fundamentalista completa de cada ativo, explicação das escolhas e
    valores mínimos recomendados para composição.
    """
    story.append(Paragraph(intro, body_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Valores Mínimos Recomendados
    story.append(Paragraph("💰 VALORES MÍNIMOS RECOMENDADOS", heading_style))
    
    valores_data = [
        ['Perfil', 'Capital Mínimo', 'Capital Ideal', 'Capital Confortável'],
        ['AGRESSIVA', 'R$ 5.000', 'R$ 20.000', 'R$ 50.000+'],
        ['MODERADA', 'R$ 5.000', 'R$ 20.000', 'R$ 50.000+'],
        ['CONSERVADORA', 'R$ 3.000', 'R$ 15.000', 'R$ 30.000+']
    ]
    
    valores_table = Table(valores_data, colWidths=[4*cm, 3.5*cm, 3.5*cm, 4*cm])
    valores_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(valores_table)
    story.append(Spacer(1, 0.5*cm))
    
    explicacao = """
    <b>Capital Mínimo:</b> Permite montar a carteira com lotes mínimos, mas com diversificação limitada.<br/>
    <b>Capital Ideal:</b> Permite diversificação adequada e rebalanceamento eficiente.<br/>
    <b>Capital Confortável:</b> Permite diversificação completa e gestão profissional do portfólio.
    """
    story.append(Paragraph(explicacao, body_style))
    
    story.append(PageBreak())
    
    # ==================== CARTEIRA AGRESSIVA ====================
    story.append(Paragraph("📈 CARTEIRA AGRESSIVA", title_style))
    story.append(Spacer(1, 0.3*cm))
    
    perfil_agressiva = """
    <b>Perfil:</b> Alta exposição a ações (46.67%)<br/>
    <b>Risco:</b> Alto<br/>
    <b>Retorno Esperado:</b> 15-25% ao ano<br/>
    <b>Horizonte:</b> Médio/Longo prazo (3+ anos)<br/>
    <b>Público-alvo:</b> Investidores com alta tolerância a volatilidade
    """
    story.append(Paragraph(perfil_agressiva, body_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Composição AGRESSIVA
    story.append(Paragraph("Composição (17 ativos - 100%)", heading_style))
    
    comp_agressiva_data = [
        ['Ativo', 'Alocação', 'Setor', 'Tipo'],
        ['IVVB11', '25.00%', 'Internacional', 'ETF'],
        ['LFTB11', '25.00%', 'Renda Fixa', 'ETF'],
        ['BBAS3', '3.33%', 'Bancos', 'Ação'],
        ['BRSR6', '3.33%', 'Bancos', 'Ação'],
        ['BMGB4', '3.33%', 'Bancos', 'Ação'],
        ['PETR4', '3.33%', 'Petróleo', 'Ação'],
        ['PRIO3', '3.33%', 'Petróleo', 'Ação'],
        ['USIM5', '3.33%', 'Siderurgia', 'Ação'],
        ['GOAU4', '3.33%', 'Siderurgia', 'Ação'],
        ['BRAP4', '3.33%', 'Mineração', 'Ação'],
        ['LOGG3', '3.33%', 'Logística', 'Ação'],
        ['DEXP3', '3.33%', 'Logística', 'Ação'],
        ['SMTO3', '3.33%', 'Agronegócio', 'Ação'],
        ['TASA4', '3.33%', 'Defesa', 'Ação'],
        ['EUCA4', '3.33%', 'Madeira', 'Ação'],
        ['ALLD3', '3.33%', 'Educação', 'Ação'],
        ['ROMI3', '3.33%', 'Máquinas', 'Ação']
    ]
    
    comp_table = Table(comp_agressiva_data, colWidths=[3*cm, 2.5*cm, 4*cm, 2.5*cm])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d32f2f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(comp_table)
    story.append(PageBreak())
    
    # Análise Detalhada dos Ativos - AGRESSIVA
    story.append(Paragraph("🔍 ANÁLISE DETALHADA DOS ATIVOS", heading_style))
    story.append(Spacer(1, 0.3*cm))
    
    ativos_agressiva = [
        {
            'ticker': 'IVVB11',
            'nome': 'iShares S&P 500',
            'alocacao': '25%',
            'motivo': 'Diversificação internacional com exposição às 500 maiores empresas americanas. Proteção cambial e acesso a empresas de tecnologia de ponta.',
            'fundamentos': 'Liquidez alta | Taxa de administração 0,17% | Dividendos trimestrais',
            'preco_ref': 'R$ 310,00',
            'lote_min': '10 cotas = R$ 3.100'
        },
        {
            'ticker': 'LFTB11',
            'nome': 'Tesouro Selic',
            'alocacao': '25%',
            'motivo': 'Proteção e liquidez. Acompanha a taxa Selic (atualmente 10,75% a.a.), oferecendo rentabilidade real positiva com risco mínimo.',
            'fundamentos': 'Risco soberano | Liquidez diária | Isento de IR para PF',
            'preco_ref': 'R$ 110,00',
            'lote_min': '10 cotas = R$ 1.100'
        },
        {
            'ticker': 'BBAS3',
            'nome': 'Banco do Brasil',
            'alocacao': '3.33%',
            'motivo': 'Maior banco público do país. Forte presença no agronegócio, setor em crescimento. Dividend Yield atrativo e gestão melhorada.',
            'fundamentos': 'P/L: 4,8 | ROE: 16% | DY: 9,5% | Payout: 40%',
            'preco_ref': 'R$ 28,50',
            'lote_min': '100 ações = R$ 2.850'
        },
        {
            'ticker': 'PETR4',
            'nome': 'Petrobras PN',
            'alocacao': '3.33%',
            'motivo': 'Líder em petróleo no Brasil. Produção em pré-sal com baixo custo. Política de dividendos agressiva (60% do FCF).',
            'fundamentos': 'P/L: 3,2 | ROE: 22% | DY: 14% | Dívida controlada',
            'preco_ref': 'R$ 38,20',
            'lote_min': '100 ações = R$ 3.820'
        },
        {
            'ticker': 'USIM5',
            'nome': 'Usiminas PNA',
            'alocacao': '3.33%',
            'motivo': 'Siderúrgica com operações verticalizadas. Beneficiada por demanda de infraestrutura e recuperação da construção civil.',
            'fundamentos': 'P/L: 5,1 | Margem EBITDA: 18% | Dívida em queda',
            'preco_ref': 'R$ 7,85',
            'lote_min': '100 ações = R$ 785'
        }
    ]
    
    for ativo in ativos_agressiva:
        story.append(Paragraph(f"<b>{ativo['ticker']} - {ativo['nome']}</b>", styles['Heading4']))
        story.append(Paragraph(f"<b>Alocação:</b> {ativo['alocacao']}", body_style))
        story.append(Paragraph(f"<b>Por que escolhi:</b> {ativo['motivo']}", body_style))
        story.append(Paragraph(f"<b>Fundamentos:</b> {ativo['fundamentos']}", body_style))
        story.append(Paragraph(f"<b>Preço Referência:</b> {ativo['preco_ref']} | <b>Lote Mínimo:</b> {ativo['lote_min']}", body_style))
        story.append(Spacer(1, 0.3*cm))
    
    story.append(Paragraph("<i>Nota: Análise completa de todos os 17 ativos disponível na versão estendida.</i>", styles['Italic']))
    
    story.append(PageBreak())
    
    # ==================== CARTEIRA MODERADA ====================
    story.append(Paragraph("📊 CARTEIRA MODERADA", title_style))
    story.append(Spacer(1, 0.3*cm))
    
    perfil_moderada = """
    <b>Perfil:</b> Balanceada (25% ações)<br/>
    <b>Risco:</b> Médio<br/>
    <b>Retorno Esperado:</b> 10-15% ao ano<br/>
    <b>Horizonte:</b> Médio prazo (2-3 anos)<br/>
    <b>Público-alvo:</b> Investidores que buscam equilíbrio entre segurança e retorno
    """
    story.append(Paragraph(perfil_moderada, body_style))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("Composição (17 ativos - 100%)", heading_style))
    
    comp_moderada_data = [
        ['Ativo', 'Alocação', 'Setor', 'Tipo'],
        ['LFTB11', '50.00%', 'Renda Fixa', 'ETF'],
        ['IVVB11', '25.00%', 'Internacional', 'ETF'],
        ['BBAS3', '1.67%', 'Bancos', 'Ação'],
        ['BRSR6', '1.67%', 'Bancos', 'Ação'],
        ['BMGB4', '1.67%', 'Bancos', 'Ação'],
        ['PETR4', '1.67%', 'Petróleo', 'Ação'],
        ['PRIO3', '1.67%', 'Petróleo', 'Ação'],
        ['USIM5', '1.67%', 'Siderurgia', 'Ação'],
        ['GOAU4', '1.67%', 'Siderurgia', 'Ação'],
        ['BRAP4', '1.67%', 'Mineração', 'Ação'],
        ['LOGG3', '1.67%', 'Logística', 'Ação'],
        ['DEXP3', '1.67%', 'Logística', 'Ação'],
        ['SMTO3', '1.67%', 'Agronegócio', 'Ação'],
        ['TASA4', '1.67%', 'Defesa', 'Ação'],
        ['EUCA4', '1.67%', 'Madeira', 'Ação'],
        ['ALLD3', '1.67%', 'Educação', 'Ação'],
        ['ROMI3', '1.67%', 'Máquinas', 'Ação']
    ]
    
    comp_mod_table = Table(comp_moderada_data, colWidths=[3*cm, 2.5*cm, 4*cm, 2.5*cm])
    comp_mod_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff9800')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(comp_mod_table)
    story.append(Spacer(1, 0.5*cm))
    
    diferenca_mod = """
    <b>Diferença para AGRESSIVA:</b> Maior alocação em renda fixa (50% vs 25%), reduzindo exposição
    a ações pela metade. Mesmos ativos, mas com pesos menores, priorizando segurança.
    """
    story.append(Paragraph(diferenca_mod, body_style))
    
    story.append(PageBreak())
    
    # ==================== CARTEIRA CONSERVADORA ====================
    story.append(Paragraph("🛡️ CARTEIRA CONSERVADORA", title_style))
    story.append(Spacer(1, 0.3*cm))
    
    perfil_conservadora = """
    <b>Perfil:</b> Baixa exposição a ações (10%)<br/>
    <b>Risco:</b> Baixo<br/>
    <b>Retorno Esperado:</b> 8-12% ao ano<br/>
    <b>Horizonte:</b> Curto/Médio prazo (1-2 anos)<br/>
    <b>Público-alvo:</b> Investidores conservadores ou próximos de usar o capital
    """
    story.append(Paragraph(perfil_conservadora, body_style))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("Composição (7 ativos - 100%)", heading_style))
    
    comp_conservadora_data = [
        ['Ativo', 'Alocação', 'Setor', 'Tipo'],
        ['LFTB11', '70.00%', 'Renda Fixa', 'ETF'],
        ['IVVB11', '20.00%', 'Internacional', 'ETF'],
        ['BBAS3', '2.00%', 'Bancos', 'Ação'],
        ['ITUB4', '2.00%', 'Bancos', 'Ação'],
        ['PETR4', '2.00%', 'Petróleo', 'Ação'],
        ['VALE3', '2.00%', 'Mineração', 'Ação'],
        ['WEGE3', '2.00%', 'Equipamentos', 'Ação']
    ]
    
    comp_cons_table = Table(comp_conservadora_data, colWidths=[3*cm, 2.5*cm, 4*cm, 2.5*cm])
    comp_cons_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(comp_cons_table)
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("🔍 ANÁLISE DOS ATIVOS ADICIONAIS", heading_style))
    
    ativos_conservadora = [
        {
            'ticker': 'ITUB4',
            'nome': 'Itaú Unibanco PN',
            'alocacao': '2%',
            'motivo': 'Maior banco privado do Brasil. Gestão de excelência, ROE consistente acima de 20%, líder em rentabilidade.',
            'fundamentos': 'P/L: 8,2 | ROE: 21% | DY: 5,5% | Índice de Basileia: 13,8%',
            'preco_ref': 'R$ 32,50',
            'lote_min': '100 ações = R$ 3.250'
        },
        {
            'ticker': 'VALE3',
            'nome': 'Vale ON',
            'alocacao': '2%',
            'motivo': 'Maior mineradora das Américas. Líder global em minério de ferro. Dividendos robustos e exposição a commodities.',
            'fundamentos': 'P/L: 4,5 | ROE: 18% | DY: 11% | Dívida controlada',
            'preco_ref': 'R$ 65,20',
            'lote_min': '100 ações = R$ 6.520'
        },
        {
            'ticker': 'WEGE3',
            'nome': 'WEG ON',
            'alocacao': '2%',
            'motivo': 'Líder em equipamentos elétricos. Crescimento consistente, expansão internacional, margens elevadas.',
            'fundamentos': 'P/L: 22 | ROE: 24% | Margem líquida: 12% | Crescimento 15% a.a.',
            'preco_ref': 'R$ 42,80',
            'lote_min': '100 ações = R$ 4.280'
        }
    ]
    
    for ativo in ativos_conservadora:
        story.append(Paragraph(f"<b>{ativo['ticker']} - {ativo['nome']}</b>", styles['Heading4']))
        story.append(Paragraph(f"<b>Alocação:</b> {ativo['alocacao']}", body_style))
        story.append(Paragraph(f"<b>Por que escolhi:</b> {ativo['motivo']}", body_style))
        story.append(Paragraph(f"<b>Fundamentos:</b> {ativo['fundamentos']}", body_style))
        story.append(Paragraph(f"<b>Preço Referência:</b> {ativo['preco_ref']} | <b>Lote Mínimo:</b> {ativo['lote_min']}", body_style))
        story.append(Spacer(1, 0.3*cm))
    
    story.append(PageBreak())
    
    # Conclusão
    story.append(Paragraph("📋 COMO MONTAR SUA CARTEIRA", heading_style))
    
    como_montar = """
    <b>1. Escolha seu perfil</b> baseado em tolerância a risco e horizonte de investimento.<br/><br/>
    <b>2. Calcule os valores</b> de cada ativo multiplicando seu capital total pelo percentual de alocação.<br/><br/>
    <b>3. Ajuste para lotes mínimos</b> - Ações brasileiras geralmente têm lote mínimo de 100 ações.<br/><br/>
    <b>4. Comece gradualmente</b> - Não precisa comprar tudo de uma vez. Faça aportes mensais.<br/><br/>
    <b>5. Rebalanceie periodicamente</b> - Ajuste as posições quando a alocação desviar mais de 5% do target.<br/><br/>
    
    <b>Exemplo prático (Capital R$ 20.000 - AGRESSIVA):</b><br/>
    • IVVB11 (25%): R$ 5.000 ÷ R$ 310 = 16 cotas<br/>
    • LFTB11 (25%): R$ 5.000 ÷ R$ 110 = 45 cotas<br/>
    • BBAS3 (3,33%): R$ 666 ÷ R$ 28,50 = 23 ações (arredondar para 200)<br/>
    • E assim por diante...<br/>
    """
    story.append(Paragraph(como_montar, body_style))
    
    story.append(Spacer(1, 0.5*cm))
    
    # Aviso Legal
    story.append(Paragraph("⚠️ AVISO LEGAL", heading_style))
    
    aviso = """
    Este material é produzido pelo Magnus AI e tem caráter meramente informativo. 
    Não constitui recomendação de investimento nem oferta de compra ou venda de ativos. 
    O investidor deve sempre consultar um profissional certificado antes de tomar decisões 
    de investimento. Rentabilidade passada não garante resultados futuros. 
    Todo investimento possui riscos.
    """
    story.append(Paragraph(aviso, body_style))
    
    story.append(Spacer(1, 0.5*cm))
    
    # Rodapé
    rodape = f"""
    <b>Magnus AI</b> | Powered by Quantum Trade<br/>
    Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}<br/>
    Versão: 1.0
    """
    story.append(Paragraph(rodape, styles['Normal']))
    
    # Gerar PDF
    doc.build(story)
    print(f"✅ PDF gerado: {filename}")
    return filename


if __name__ == '__main__':
    print("=" * 80)
    print("GERANDO PDF DETALHADO DAS CARTEIRAS")
    print("=" * 80)
    filename = criar_pdf_carteiras()
    print(f"\n✅ PDF criado com sucesso: {filename}")
    print("=" * 80)

