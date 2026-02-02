# Tópico 5: Linguagens e Banco de Dados

## 📋 Questão

> Quais linguagens e bancos de dados você recomendaria e por quê?

## Linguagens Recomendadas

### Python 3.11 (Principal)

**Por quê?**

✅ Ecossistema ML maduro (boto3, comprehend)  
✅ Fácil manutenção  
✅ Performance adequada  

**Quando usar:**
- Lambdas de processamento
- Scripts de ML/classificação
- ETL e processamento de dados

## Bancos de Dados Recomendados

### 1. DynamoDB (Principal)

#### Schema

```python
{
  "PK": "COMPLAINT#REC-001",  # Partition Key
  "SK": "METADATA",            # Sort Key
  "id": "REC-001",
  "text": "Não reconheço essa compra",
  "channel": "digital",
  "status": "CLASSIFIED",
  "customer_id": "CUST-12345",
  "categories": ["fraude"],
  "deadline": "2024-02-11T10:30:00Z",
  "GSI1PK": "STATUS#CLASSIFIED",
  "GSI1SK": "DEADLINE#2024-02-11",
  "GSI2PK": "CUSTOMER#CUST-12345",
  "GSI2SK": "CREATED_AT#2024-02-01"
}
```

#### Por quê?

✅ Performance consistente (<10ms)  
✅ Auto-scaling nativo  
✅ Pay-per-request  
✅ Sem gerenciamento de servidor  
✅ Integração nativa com Lambda  

#### Access Patterns

**Query 1: Buscar reclamação por ID**
```python
table.get_item(
    Key={'PK': 'COMPLAINT#REC-001', 'SK': 'METADATA'}
)
```

**Query 2: Reclamações próximas do prazo (GSI1)**
```python
table.query(
    IndexName='DeadlineIndex',
    KeyConditionExpression='GSI1PK = :status AND GSI1SK < :date',
    ExpressionAttributeValues={
        ':status': 'STATUS#IN_PROGRESS',
        ':date': tomorrow_date
    }
)
```

**Query 3: Histórico do cliente (GSI2)**
```python
table.query(
    IndexName='CustomerIndex',
    KeyConditionExpression='GSI2PK = :customer',
    ExpressionAttributeValues={
        ':customer': 'CUSTOMER#CUST-12345'
    }
)
```

### 2. S3 (Armazenamento de Documentos)

#### Estrutura

```
s3://complaints-attachments/
  ├── 2024/
  │   ├── 02/
  │   │   ├── 01/
  │   │   │   ├── REC-001/
  │   │   │   │   ├── attachment_1.pdf
  │   │   │   │   └── attachment_2.jpg
```

#### Por quê?

✅ Ilimitado  
✅ Durabilidade 99.999999999%  
✅ Lifecycle policies  
✅ Versionamento  
✅ Barato ($0.023/GB)  

### 3. DynamoDB (Regras Dinâmicas)

**Por quê ter tabela separada para regras?**

✅ Update sem redeploy  
✅ Versionamento de regras  
✅ Auditoria  
✅ A/B testing  

