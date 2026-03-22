# 🏦 Case — Canais Críticos: Classificação Automática de Reclamações Bancárias

> **Solução completa** para ingestão, classificação e rastreabilidade de reclamações bancárias provenientes de canais digitais e físicos, com SLA de 10 dias corridos e volume de ~1.000 reclamações/dia.

---

## 📌 Índice

1. [O Problema](#1-o-problema)
2. [A Solução em Uma Frase](#2-a-solução-em-uma-frase)
3. [Arquitetura Geral](#3-arquitetura-geral)
4. [Tópico 1 — Classificação Automática (código)](#4-tópico-1--classificação-automática-código)
5. [Tópico 2 — Fluxo, Observabilidade e Gargalos](#5-tópico-2--fluxo-observabilidade-e-gargalos)
6. [Tópico 3 — Arquitetura de Software](#6-tópico-3--arquitetura-de-software)
7. [Tópico 4 — Exemplo de Componente em Camadas](#7-tópico-4--exemplo-de-componente-em-camadas)
8. [Tópico 5 — Linguagens e Banco de Dados](#8-tópico-5--linguagens-e-banco-de-dados)
9. [Tópico 6 — Como a IA Acelera o Processo](#9-tópico-6--como-a-ia-acelera-o-processo)
10. [Estrutura do Repositório](#10-estrutura-do-repositório)
11. [Como Rodar os Testes](#11-como-rodar-os-testes)

---

## 1. O Problema

O banco recebe reclamações por dois canais distintos:

| Canal | Forma de entrada |
|---|---|
| **Digital** | Formulário no site (API REST) |
| **Físico** | Documento recepcionado e digitalizado (upload em S3 + OCR) |

Essas reclamações precisam ser:
- **Recepcionadas e padronizadas** independente do canal de origem
- **Classificadas automaticamente** por tipo de demanda (acesso, fraude, cobrança, etc.)
- **Rastreadas** durante todo o ciclo de vida com SLA de 10 dias
- **Expostas** em portal interno e enviadas para sistemas legados

**Escala:** ~1.000 novas reclamações/dia com picos e fluxo contínuo.

---

## 2. A Solução em Uma Frase

> Classificador híbrido serverless (regras + ML) sobre arquitetura event-driven na AWS, com observabilidade centralizada no Datadog e rastreabilidade completa no DynamoDB.

---

## 3. Arquitetura Geral

![Arquitetura da Solução](desenho-solucao/arq.png)

### Fluxo resumido

```
[Canal Digital]  ──→  API Gateway
                              │
[Canal Físico]   ──→  S3 + Textract (OCR)
                              │
                         SQS (fila)
                              │
                         Lambda
                         ├── 1. Normaliza texto
                         ├── 2. Tenta classificar por REGRAS  ──→ match? → salva
                         ├── 3. Fallback: AWS Comprehend (ML) ──→ confiança ≥ threshold? → salva
                         └── 4. Baixa confiança → marca para REVISÃO HUMANA
                              │
                         DynamoDB  ←→  API interna / Portal / Sistemas legados
                              │
                         Datadog (logs + métricas + alertas)
```

---

## 4. Tópico 1 — Classificação Automática (código)

📄 [Ver documento completo](desenho-solucao/TOPICO_1_CLASSIFICACAO.md)

### Abordagem: Classificação por Palavras-Chave com Normalização

O classificador funciona em três passos:

**Passo 1 — Normalização**
Remove acentos, converte para minúsculas, normaliza espaços. Isso garante que `"Não"`, `"nao"` e `"NÃO"` sejam tratados de forma idêntica.

**Passo 2 — Busca com word boundaries**
Usa regex com `\b` para evitar falsos positivos. Ex: `"valor"` não ativa `"valorização"`.

**Passo 3 — Multi-label**
Retorna **todas** as categorias aplicáveis com detalhe de quais palavras fizeram match.

### Exemplo

**Entrada:**
```json
{
  "reclamacao": "Estou com problemas para acessar minha conta e o aplicativo está travando muito.",
  "categorias": {
    "acesso": ["acessar", "login", "senha"],
    "aplicativo": ["app", "aplicativo", "travando", "erro"],
    "fraude": ["fatura", "nao reconhece divida", "fraude"]
  }
}
```

**Saída:**
```json
{
  "categorias": ["acesso", "aplicativo"],
  "detalhes": {
    "acesso": ["acessar"],
    "aplicativo": ["aplicativo", "travando"]
  }
}
```

### Onde está o código

| Arquivo | Descrição |
|---|---|
| `implementacao/classificacao.py` | Função principal `classificar_reclamacao()` |
| `implementacao/test_classificacao.py` | Testes unitários com pytest |

---

## 5. Tópico 2 — Fluxo, Observabilidade e Gargalos

📄 [Ver documento completo](desenho-solucao/TOPICO_2_FLUXO.md)

### Observabilidade com Datadog

Cada reclamação gera logs estruturados com:
- ID, método de classificação, categorias encontradas, score de confiança, tempo total, erros

**Alarmes automáticos:**

| Alarme | Condição |
|---|---|
| Taxa alta de revisão manual | > 10% em 5 min |
| Latência elevada | p99 > 2 segundos |
| Erros em Lambda | > 5 erros/min |
| Dead Letter Queue com msgs | > 10 mensagens acumuladas |
| DynamoDB Throttling | Qualquer throttle detectado |

### Como evitar gargalos

| Estratégia | Detalhe |
|---|---|
| **Lambda com concurrency reservada** | Isolamento de picos, custo previsível |
| **DynamoDB Auto-Scaling** | Mín. 5 / Máx. 100 unidades, sem ação manual |
| **Batch Processing no SQS** | Lotes de até 10 mensagens processadas em paralelo (threads) |
| **Cache de regras em memória** | Regras carregadas 1× por instância Lambda, evita consultas repetidas ao DynamoDB |

### Retry e DLQ

- Mensagens com falha: **3 retentativas** com backoff
- Após 3 falhas: vai para **Dead Letter Queue** para análise manual
- Erros temporários (timeout) → retry automático
- Erros permanentes (dados inválidos) → log + continua processamento

### Escalabilidade

| Cenário | Lambda | Comprehend | DynamoDB |
|---|---|---|---|
| 1.000 req/dia (atual) | 10 concurrent (~2%) | 1 unit (~20%) | On-demand |
| 10.000 req/dia | 50 concurrent | 3 units | On-demand (auto) |
| Custo adicional para 10x | — | — | +$50-70/mês |

---

## 6. Tópico 3 — Arquitetura de Software

📄 [Ver documento completo](desenho-solucao/TOPICO_3_ARQUITETURA.md)

### Clean Architecture + Event-Driven

A solução usa **Clean Architecture** com processamento orientado a eventos, organizada em camadas desacopladas:

```
┌─────────────────────────────────────────┐
│         CAMADA DE INGESTÃO              │
│  API Gateway (digital) + S3/Textract    │
│  (físico) → entrada padronizada         │
├─────────────────────────────────────────┤
│         CAMADA DE MENSAGERIA            │
│  SQS → absorve picos, garante           │
│  resiliência, habilita DLQ              │
├─────────────────────────────────────────┤
│       CAMADA DE PROCESSAMENTO           │
│  Rule Classifier → ML (Comprehend)      │
│  → Revisão Humana                       │
├─────────────────────────────────────────┤
│          CAMADA DE DADOS                │
│  DynamoDB (reclamações/estados)         │
│  S3 (documentos/anexos)                 │
├─────────────────────────────────────────┤
│       CAMADA DE EXPOSIÇÃO               │
│  API REST → Portal Interno              │
│  → Sistemas Legados                     │
├─────────────────────────────────────────┤
│       CAMADA DE OBSERVABILIDADE         │
│  CloudWatch + Datadog                   │
└─────────────────────────────────────────┘
```

### Por que Clean Architecture?

| Requisito do case | Como a arquitetura atende |
|---|---|
| Alto volume e picos | SQS desacopla ingestão e processamento |
| Múltiplos canais | Camada de ingestão unificada e normalizadora |
| Classificação evolutiva | Pipeline híbrido (regras → ML), começa simples e evolui |
| Rastreabilidade e SLA | Estados e timestamps persistidos no DynamoDB |
| Integração com legados | API REST desacoplada do core |

---

## 7. Tópico 4 — Exemplo de Componente em Camadas

📄 [Ver documento completo](desenho-solucao/TOPICO_4_COMPONENTES.md)

O componente detalhado é o **HybridClassifier**, que demonstra a separação de responsabilidades na prática:

```
Domain Layer        → Entidades: Reclamação, Categoria, Resultado
Use Case Layer      → ClassificarReclamacaoUseCase
Infrastructure Layer→ RuleClassifier, MLClassifier (Comprehend), DynamoRepository
Presentation Layer  → Lambda handler (entry point)
```

O código de implementação está em `implementacao/` com testes em `implementacao/test_classificacao.py`.

---

## 8. Tópico 5 — Linguagens e Banco de Dados

📄 [Ver documento completo](desenho-solucao/TOPICO_5_LINGUAGENS_DADOS.md)

### Linguagem: Python 3.11

- Ecossistema ML maduro (`boto3`, `comprehend`)
- Fácil manutenção e leitura
- Performance adequada para Lambdas de processamento

### Banco de Dados

**DynamoDB (principal)**
- Latência consistente < 10ms
- Auto-scaling nativo (sem servidor para gerenciar)
- Pay-per-request
- Integração nativa com Lambda

Schema principal com GSIs para os access patterns mais críticos:
```
Query 1: Buscar reclamação por ID
Query 2: Reclamações próximas do prazo (GSI por status + deadline)
Query 3: Histórico do cliente (GSI por customer_id)
```

**S3 (documentos/anexos)**
- Armazenamento ilimitado de PDFs e imagens
- Lifecycle policies, versionamento, durabilidade 99.999999999%
- Custo: $0,023/GB

**DynamoDB separado para Regras**
- Atualização de regras de negócio **sem redeploy** da Lambda
- Auditoria e versionamento das regras
- Possibilita A/B testing de estratégias de classificação

---

## 9. Tópico 6 — Como a IA Acelera o Processo

📄 [Ver documento completo](desenho-solucao/TOPICO_6_IA.md)

### Onde a IA entra na solução

| Etapa | Serviço | Papel |
|---|---|---|
| OCR de documentos físicos | **AWS Textract** | Extrai texto de PDFs e imagens digitalizadas |
| Classificação ambígua | **AWS Comprehend** | Fallback quando regras não têm match suficiente |
| Detecção de urgência | **Comprehend (Sentiment)** | Identifica reclamações com linguagem de alta urgência |
| Alerta de SLA | Regra sobre timestamp + **evento agendado** | Identifica casos próximos do vencimento automaticamente |

### Melhorias futuras com IA

- **Fuzzy matching** — detectar variações de digitação ("travanndo", "aceso")
- **Embedding similarity** — classificar reclamações sem palavras-chave exatas
- **Fine-tuning** — treinar modelo próprio com histórico de reclamações classificadas manualmente
- **Análise de sentimento** — priorizar automaticamente reclamações com tom mais crítico

---

## 10. Estrutura do Repositório

```
case-canais-criticos/
│
├── implementacao/
│   ├── classificacao.py          # Classificador híbrido (lógica principal)
│   └── test_classificacao.py     # Testes com pytest
│
├── desenho-solucao/
│   ├── arq.png                   # Diagrama de arquitetura
│   ├── TOPICO_1_CLASSIFICACAO.md # Detalhamento do classificador
│   ├── TOPICO_2_FLUXO.md         # Fluxo, observabilidade, gargalos
│   ├── TOPICO_3_ARQUITETURA.md   # Clean Architecture + justificativas
│   ├── TOPICO_4_COMPONENTES.md   # HybridClassifier em camadas
│   ├── TOPICO_5_LINGUAGENS_DADOS.md  # Python + DynamoDB + S3
│   └── TOPICO_6_IA.md            # Textract, Comprehend e melhorias futuras
│
└── APRESENTACAO.md               # ← você está aqui
```
---

## Critérios Técnicos Atendidos

| Critério | Como foi atendido |
|---|---|
| **Organização do código e fluxo** | Clean Architecture em camadas, SQS desacoplando ingestão/processamento |
| **Tratamento de casos ambíguos** | Classificador híbrido: regras → ML → revisão humana |
| **Boas práticas** | pytest, word boundaries com regex, cache de regras, DLQ, retry |
| **Clareza e documentação** | 6 tópicos documentados individualmente + diagrama de arquitetura |

---
