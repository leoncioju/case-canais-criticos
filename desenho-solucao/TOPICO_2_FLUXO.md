# Tópico 2: Desenho do Fluxo Completo

## 📋 Questões do Case

> **2. Desenhe como seria esse fluxo**
> - Como você monitoriaria esse fluxo e acionaria alertas em caso de erro?
> - Como evitar gargalos?

---

## 🔄 Fluxo Completo da Solução

### Diagrama de Arquitetura

![Arquitetura da Solução](arq.png)

---

## 📊 Observabilidade com Datadog

### Métricas Coletadas

A aplicação coleta métricas em tempo real durante o processamento de cada reclamação:

- **Latência de classificação** - Tempo total desde o recebimento até a resposta (em ms)
- **Método utilizado** - Se foi regra, ML ou fallback
- **Taxa de revisão** - Percentual de reclamações que precisam revisão manual
- **Categorias encontradas** - Distribuição de quais categorias foram detectadas
- **Taxa de erro** - Quantidade e tipo de erros ocorridos

### Alarmes no Datadog

Monitores automáticos acionam alertas quando anomalias são detectadas:

| Alarme | Condição |
|--------|----------|
| **Taxa Alta de Revisão** | >10% em 5 min | 
| **Latência Elevada** | p99 > 2 segundos | 
| **Erros em Lambda** | >5 erros/min | 
| **DLQ com mensagens** | >10 msgs acumuladas | 
| **DynamoDB Throttling** | Qualquer throttle detectado | 

### Dashboard em Tempo Real

Um dashboard centralizado mostra a saúde do sistema com:

- **Gráfico de classificações** - Quantas reclamações foram processadas por método (regras vs ML)
- **Taxa de revisão** - Percentual visual de reclamações que precisam revisão
- **Latência** - Percentis P50, P95 e P99 de tempo de processamento
- **Taxa de erros** - Total de erros e distribuição por tipo
- **Categorias mais frequentes** - Quais categorias aparecem mais
- **Distribuição de latência** - Heatmap mostrando padrão de tempo de resposta
- **Status de saúde** - Indicador de disponibilidade do serviço

### Rastreamento Distribuído

Cada reclamação é rastreada em toda sua jornada:

- **API recebe requisição** → enviada para fila (SQS)
- **Lambda processa** → tenta classificação com regras
- **Se falhar, tenta ML** → chama Comprehend
- **Salva resultado** → armazena no DynamoDB

Cada etapa é rastreada, permitindo identificar exatamente onde estão os gargalos e quanto tempo cada fase consome.

### Logs Estruturados

Logs detalhados são gerados para cada reclamação processada, contendo:

- ID da reclamação
- Método de classificação usado
- Categorias encontradas
- Score de confiança
- Se precisa revisão
- Tempo total processado
- Tipo de erro (se houver)

Esses logs podem ser consultados e filtrados para análise, troubleshooting ou auditoria.

---

## 🚫 Como Evitar Gargalos

### 1. Lambda com Concurrency Reservada

O Lambda é configurado com uma quantidade máxima de execuções simultâneas para evitar throttling. Isso garante que o serviço não seja afetado por picos de outras funções na mesma conta AWS, mantendo custo previsível e isolamento.

### 2. DynamoDB Auto-Scaling

O DynamoDB é configurado para escalar automaticamente a capacidade de leitura e escrita conforme a demanda aumenta. Com um limite mínimo de 5 unidades e máximo de 100, o banco cresce organicamente sem necessidade de intervenção manual.

### 3. Batch Processing Otimizado

O SQS entrega mensagens em lotes (até 10 por vez). O Lambda processa essas mensagens em paralelo usando threads para aproveitar melhor o tempo de execução, aumentando o throughput sem custo adicional.

### 4. Cache de Regras

As regras de classificação são carregadas uma única vez na memória do Lambda e reutilizadas em todas as invocações subsequentes. Isso reduz drasticamente as consultas ao DynamoDB (de centenas por dia para apenas uma).

---

## 🔄 Retry e Error Handling

### Estratégia de Retry no SQS

Mensagens que falham são automaticamente retentadas 3 vezes com intervalos de espera. Após as 3 tentativas, a mensagem vai para uma fila de mensagens mortas (Dead Letter Queue) para análise manual.

### Error Handling na Lambda

Erros temporários (timeout, serviço indisponível) causam retry automático. Erros permanentes (dados inválidos, configuração errada) são registrados e a execução continua para não bloquear outras mensagens da fila.

---

## 📈 Escalabilidade

### Capacidade Atual (1.000 req/dia)

| Componente | Capacidade | Utilização |
|------------|------------|------------|
| Lambda | 10 concurrent | ~2% |
| SQS | Ilimitado | N/A |
| DynamoDB | On-demand | Auto |
| Comprehend | 100 req/min | ~20% |

### Escalar para 10.000 req/dia

Para aumentar 10x a capacidade, basta:

1. **Aumentar Lambda concurrency** - De 10 para 50 execuções simultâneas
2. **Aumentar Comprehend units** - De 1 para 3 unidades de inferência para processar mais requisições/minuto
3. **DynamoDB escala automaticamente** - Não requer ação manual

**Custo adicional:** +$50-70/mês para essa escalabilidade

---

## 🎯 SLA e Garantias

| Métrica | Target | Monitoramento |
|---------|--------|---------------|
| **Disponibilidade** | 99.9% | CloudWatch Alarms |
| **Latência p99** | <2s | X-Ray |
| **Taxa de erro** | <0.1% | CloudWatch Metrics |
| **Processamento** | <5min | Custom metric |
| **Deadline** | 10 dias | Lambda monitor |

---

## 📚 Referências

- **Diagrama:** `diagrams/architecture.drawio`
- **Fluxos detalhados:** `docs/FLOWS.md`
- **Monitoramento:** `docs/ARCHITECTURE.md` (seção Observabilidade)
- **Código:** `src/handler.py`
