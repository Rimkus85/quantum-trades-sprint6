"""Módulos de processamento do Magnus Wealth."""

from .carteira_parser import CarteiraParser, parse_telegram_messages, get_recommendations_summary

__all__ = ['CarteiraParser', 'parse_telegram_messages', 'get_recommendations_summary']

