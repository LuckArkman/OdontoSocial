# Sprint 32: API de Human Handoff (Takeover)

## 🎯 Objetivo
Permitir que um humano 'trave' a IA e assuma o chat manualmente.

## 🛠️ Bibliotecas e Ferramentas
- redis

## 🏗️ Estrutura Técnica (Classes e Modelos)
- LockService, AgentControl

## 🛣️ Rotas e Endpoints
- POST /chat/lock, POST /chat/unlock

## 📝 Detalhes da Implementação
Uso do Redis para sinalizar que a IA deve ignorar mensagens deste lead temporariamente.

---
**Status:** Planejado
**Data Estimada:** Março/Abril 2026
**Projeto:** OdontoSocial Backend
