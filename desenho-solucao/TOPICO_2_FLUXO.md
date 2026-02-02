# Tópico 2: Desenho do Fluxo Completo

## 📋 Questões do Case

> **2. Desenhe como seria esse fluxo**
> - Como você monitoriaria esse fluxo e acionaria alertas em caso de erro?
> - Como evitar gargalos?

---

## 🔄 Fluxo Completo da Solução

### Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                    CANAL DIGITAL (API Gateway)                  │
│                                                                 │
│  Cliente Web → POST /complaints → API Gateway → SQS FIFO       │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                    CANAL FÍSICO (S3 + EventBridge)              │
│                                                                 │
│  Documento → S3 → EventBridge → Textract (OCR) → SQS FIFO      │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                  FILA DE PROCESSAMENTO (SQS FIFO)               │
│                                                                 │
│  • Deduplicação automática                                     │
│  • Ordenação garantida (FIFO)                                  │
│  • Retry automático (3x)                                       │
│  • Dead Letter Queue para falhas                               │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                 PROCESSAMENTO (Lambda + Step Functions)         │
│                                                                 │
│  Lambda Classifier (Batch de 10 mensagens)                     │
│    ↓                                                            │
│  FASE 1: Rule Classifier (~70%)                                │
│    ├─ Match encontrado? → Classificado (95% confiança)         │
│    └─ Sem match → FASE 2                                       │
│                                                                 │
│  FASE 2: ML Classifier (~25%)                                  │
│    ├─ Confiança >= 60%? → Classificado                         │
│    └─ Confiança < 60% → FASE 3                                 │
│                                                                 │
│  FASE 3: Fallback (~5%)                                        │
│    └─ Marca para revisão manual                                │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                    PERSISTÊNCIA (DynamoDB + S3)                 │
│                                                                 │
│  • DynamoDB: Metadados da reclamação                           │
│  • S3: Documentos e anexos                                     │
│  • EventBridge: Eventos para sistemas legados                  │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                    NOTIFICAÇÕES E ALERTAS                       │
│                                                                 │
│  • SNS: Notifica equipes (email, SMS, Slack)                   │
│  • CloudWatch: Métricas e dashboards                           │
│  • Lambda Deadline Monitor: Alerta vencimentos                 │
└─────────────────────────────────────────────────────────────────┘
```

**Visualização completa:** Veja `diagrams/architecture.drawio`

---

## 🎯 Fluxo Detalhado Passo a Passo

### Cenário 1: Reclamação Digital (Site/App)

```
1. Cliente submete reclamação via portal web
   POST /api/v1/complaints
   {
     "text": "Não consigo acessar minha conta",
     "customer_id": "12345",
     "channel": "digital"
   }

2. API Gateway valida request
   ✓ Schema válido?
   ✓ Customer ID existe?
   ✓ Rate limit OK?

3. API Gateway → SQS FIFO
   MessageGroupId: customer_id (garante ordenação)
   MessageDeduplicationId: hash(text + timestamp)

4. Lambda é triggerada (batch de 10 mensagens)
   Concurrency: 10 (reservado)
   Timeout: 60s
   Memory: 512MB

5. Para cada mensagem do batch:
   
   a) Parse e validação
      ✓ Campos obrigatórios presentes?
      ✓ Texto não vazio?
   
   b) Classificação (Híbrida)
      FASE 1: Rule Classifier
        ├─ Busca patterns regex
        ├─ Match "acesso": \b(não consigo acessar)\b
        └─ Confiança: 95% ✅
      
      FASE 2: ML (pulado - já tem match claro)
      
      FASE 3: Fallback (não necessário)
   
   c) Enriquecimento
      ├─ Busca histórico do cliente (DynamoDB)
      ├─ Conta reclamações anteriores
      └─ Verifica se é recorrente
   
   d) Persistência
      ├─ DynamoDB: PutItem
      │   PK: COMPLAINT#REC-001
      │   SK: METADATA
      │   categories: ["acesso"]
      │   status: "CLASSIFIED"
      │   deadline: 2024-02-11T10:30:00Z
      │
      └─ S3: (anexos, se houver)
   
   e) Publicação de Evento
      EventBridge → PutEvents
      {
        "source": "complaint.classifier",
        "detail-type": "ComplaintClassified",
        "detail": {
          "complaint_id": "REC-001",
          "categories": ["acesso"],
          "requires_review": false
        }
      }

6. Sistemas consumidores recebem evento
   ├─ Sistema de Tickets: Cria ticket automaticamente
   ├─ CRM: Atualiza histórico do cliente
   ├─ Analytics: Registra métrica
   └─ Notificações: Email para cliente (confirmação)

7. Lambda responde ao SQS
   ✅ Success → Mensagem deletada da fila
   ❌ Error → Retry (até 3x) → DLQ

8. CloudWatch registra
   ├─ Logs: Detalhes do processamento
   ├─ Metrics: Latência, categorias, método usado
   └─ Traces: X-Ray trace completo
```

### Cenário 2: Reclamação Física (Documento Escaneado)

```
1. Documento PDF enviado ao S3
   s3://complaints-physical/2024/02/01/doc_001.pdf

2. S3 Event → EventBridge
   Event: {
     "source": "aws.s3",
     "detail-type": "Object Created"
   }

3. Lambda OCR (Textract)
   ├─ Extrai texto do PDF
   ├─ Valida qualidade do texto
   └─ Envia para SQS FIFO

4. Resto do fluxo segue igual ao Cenário 1
```

---

## 📊 Monitoramento e Alertas

### 1. CloudWatch Metrics (Custom)

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

# Publicar métrica customizada
cloudwatch.put_metric_data(
    Namespace='ComplaintClassifier',
    MetricData=[
        {
            'MetricName': 'ClassificationMethod',
            'Dimensions': [
                {'Name': 'Method', 'Value': 'rule-based'}
            ],
            'Value': 1,
            'Unit': 'Count'
        },
        {
            'MetricName': 'ProcessingTime',
            'Value': processing_time_ms,
            'Unit': 'Milliseconds'
        },
        {
            'MetricName': 'RequiresReviewRate',
            'Value': 1 if requires_review else 0,
            'Unit': 'Count'
        }
    ]
)
```

**Métricas monitoradas:**
- `ClassificationMethod` (rule-based, ml-based, fallback)
- `ProcessingTime` (latência)
- `RequiresReviewRate` (% que precisa revisão)
- `CategoryDistribution` (distribuição por categoria)
- `ErrorRate` (taxa de erros)

### 2. CloudWatch Alarms

```bash
# Alarme: Alta taxa de revisão manual
aws cloudwatch put-metric-alarm \
  --alarm-name high-review-rate \
  --metric-name RequiresReviewRate \
  --namespace ComplaintClassifier \
  --statistic Average \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:us-east-1:123:oncall-team

# Alarme: Lambda com erros
aws cloudwatch put-metric-alarm \
  --alarm-name lambda-errors \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --dimensions Name=FunctionName,Value=complaint-classifier \
  --statistic Sum \
  --period 60 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1
```

**Alarmes configurados:**
| Alarme | Threshold | Ação |
|--------|-----------|------|
| `high-review-rate` | >10% | PagerDuty + Email |
| `lambda-errors` | >5 erros/min | PagerDuty |
| `comprehend-latency` | p99 > 2s | Email |
| `sqs-dlq-messages` | >10 msgs | PagerDuty |
| `dynamodb-throttling` | >1 throttle/min | Email |
| `deadline-approaching` | <24h restantes | Slack |

### 3. X-Ray Tracing

```python
from aws_xray_sdk.core import xray_recorder

@xray_recorder.capture('classify_complaint')
def classify_complaint(text, complaint_id):
    # X-Ray captura automaticamente:
    # - Tempo de execução
    # - Chamadas a serviços AWS
    # - Erros e exceções
    
    with xray_recorder.capture('rule_classification'):
        rule_result = rule_classifier.classify(text)
    
    if not rule_result:
        with xray_recorder.capture('ml_classification'):
            ml_result = ml_classifier.classify(text)
    
    return result
```

**Benefícios do X-Ray:**
- ✅ Trace end-to-end (API → Lambda → DynamoDB)
- ✅ Identifica gargalos
- ✅ Análise de latência por componente
- ✅ Mapa de dependências

### 4. CloudWatch Logs Insights

**Queries úteis:**

```sql
-- Taxa de classificação por método
fields @timestamp, classification_method
| stats count() by classification_method

-- Top 10 categorias
fields categories
| stats count() by categories
| sort count desc
| limit 10

-- Latência p99 por método
fields processing_time_ms, classification_method
| stats percentile(processing_time_ms, 99) by classification_method

-- Erros nas últimas 24h
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc

-- Reclamações que precisam revisão
fields @timestamp, complaint_id, categories, confidence
| filter requires_review = true
| sort @timestamp desc
```

### 5. Dashboard CloudWatch

```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["ComplaintClassifier", "ClassificationMethod", {"stat": "Sum"}]
        ],
        "period": 300,
        "stat": "Sum",
        "region": "us-east-1",
        "title": "Classificações por Método"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/Lambda", "Duration", {"stat": "Average"}],
          ["...", {"stat": "p99"}]
        ],
        "title": "Latência Lambda"
      }
    },
    {
      "type": "log",
      "properties": {
        "query": "fields @timestamp, complaint_id | filter requires_review = true",
        "title": "Reclamações para Revisão"
      }
    }
  ]
}
```

---

## 🚫 Como Evitar Gargalos

### 1. SQS FIFO com Grupos de Mensagens

```python
# Particiona por canal para paralelização
message_group_id = f"{complaint.channel}_{complaint.customer_id % 10}"

sqs.send_message(
    QueueUrl=queue_url,
    MessageBody=json.dumps(complaint),
    MessageGroupId=message_group_id,  # 20 grupos (2 canais × 10 partições)
    MessageDeduplicationId=dedup_id
)
```

**Benefício:** 20 grupos = até 20 Lambdas processando em paralelo

### 2. Lambda com Concurrency Reservada

```bash
aws lambda put-function-concurrency \
  --function-name complaint-classifier \
  --reserved-concurrent-executions 10
```

**Vantagens:**
- ✅ Evita throttling
- ✅ Custo previsível
- ✅ Isola de outras funções

### 3. DynamoDB Auto-Scaling

```terraform
resource "aws_appautoscaling_target" "dynamodb_table_read" {
  max_capacity       = 100
  min_capacity       = 5
  resource_id        = "table/complaints"
  scalable_dimension = "dynamodb:table:ReadCapacityUnits"
  service_namespace  = "dynamodb"
}

resource "aws_appautoscaling_policy" "dynamodb_table_read_policy" {
  name               = "DynamoDBReadCapacityUtilization"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.dynamodb_table_read.resource_id
  scalable_dimension = aws_appautoscaling_target.dynamodb_table_read.scalable_dimension
  service_namespace  = aws_appautoscaling_target.dynamodb_table_read.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBReadCapacityUtilization"
    }
    target_value = 70.0
  }
}
```

### 4. Batch Processing Otimizado

```python
def lambda_handler(event, context):
    # SQS entrega até 10 mensagens por vez
    records = event.get('Records', [])
    
    # Processa em paralelo com threads
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for record in records:
            future = executor.submit(process_complaint, record)
            futures.append(future)
        
        # Aguarda todos completarem
        results = [f.result() for f in futures]
    
    return {'statusCode': 200, 'processed': len(results)}
```

### 5. Cache de Regras

```python
class RuleRepository:
    def __init__(self, cache_ttl_seconds=300):
        self._cached_rules = None
        self._cache_timestamp = None
    
    def get_rules(self):
        # Verifica cache primeiro (evita DynamoDB)
        if self._is_cache_valid():
            return self._cached_rules
        
        # Cache miss: carrega do DynamoDB
        rules = self._load_from_dynamodb()
        self._cached_rules = rules
        return rules
```

**Redução:** 1.000 req/dia → 1 req ao DynamoDB (após warm start)

### 6. Comprehend Endpoint com Múltiplas Units

```bash
# Aumenta throughput do Comprehend
aws comprehend update-endpoint \
  --endpoint-arn arn:... \
  --desired-inference-units 3  # 300 req/min
```

### 7. Circuit Breaker para ML

```python
class MLClassifier:
    def __init__(self):
        self.failure_count = 0
        self.circuit_open = False
    
    def classify(self, text):
        # Se Comprehend está falhando, pula ML
        if self.circuit_open:
            return []
        
        try:
            result = self._call_comprehend(text)
            self.failure_count = 0  # Reset
            return result
        except Exception:
            self.failure_count += 1
            
            # Abre circuito após 5 falhas
            if self.failure_count >= 5:
                self.circuit_open = True
                # Agenda fechamento após 1 min
                
            return []  # Fallback gracioso
```

---

## 🔄 Retry e Error Handling

### SQS Retry Strategy

```json
{
  "RedrivePolicy": {
    "deadLetterTargetArn": "arn:aws:sqs:...:complaints-dlq.fifo",
    "maxReceiveCount": 3
  },
  "VisibilityTimeout": 70
}
```

**Comportamento:**
1. Tentativa 1: Imediato
2. Tentativa 2: Após 70s
3. Tentativa 3: Após 70s
4. Falha → DLQ

### Lambda Error Handling

```python
def lambda_handler(event, context):
    successful = []
    failed = []
    
    for record in event['Records']:
        try:
            result = process_complaint(record)
            successful.append(result)
        except TransientError:
            # Erro temporário: Lambda vai retentar
            failed.append(record)
            raise  # Força retry
        except PermanentError as e:
            # Erro permanente: registra e continua
            log_error(record, e)
            # Envia para DLQ manualmente
            send_to_dlq(record)
    
    # Partial batch failure
    return {
        'batchItemFailures': [
            {'itemIdentifier': f['messageId']} for f in failed
        ]
    }
```

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

```bash
# 1. Aumentar Lambda concurrency
aws lambda put-function-concurrency \
  --function-name complaint-classifier \
  --reserved-concurrent-executions 50

# 2. Aumentar Comprehend units
aws comprehend update-endpoint \
  --desired-inference-units 3

# 3. DynamoDB já escala automaticamente
```

**Custo adicional:** +$50-70/mês

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
