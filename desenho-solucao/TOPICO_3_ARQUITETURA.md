## 3. Arquitetura de Software Recomendada

A solução foi projetada utilizando uma **Arquitetura Limpa (Clean Architecture)** combinada com um processamento orientado a eventos, organizada em camadas bem definidas e desacopladas, garantindo escalabilidade, rastreabilidade e facilidade de evolução.

### Justificativa da Arquitetura

A arquitetura atende diretamente aos requisitos do case:

- **Alto volume e picos de entrada**  
  → Uso de SQS para desacoplar ingestão e processamento.

- **Múltiplos canais de entrada (digital e físico)**  
  → Camada de ingestão unificada, normalizando os dados desde a origem.

- **Classificação automática e evolutiva**  
  → Pipeline híbrido (regras + ML), permitindo começar simples e evoluir com segurança.

- **Rastreabilidade e SLA**  
  → Persistência de estados e timestamps em banco de dados.

- **Integração com sistemas legados e portal interno**  
  → Camada de exposição desacoplada via API.

### Camadas da Arquitetura
---
#### Camada de Ingestão

Responsável por receber reclamações de diferentes canais:

- Canal digital via API Gateway  
- Canal físico via upload em S3 e extração de texto com Amazon Textract  

Essa camada garante que todas as reclamações entrem no sistema em um formato padronizado, independentemente da origem.

---
#### Camada de Mensageria

Utiliza Amazon SQS para:

- Absorver picos de volume  
- Garantir resiliência  
- Permitir reprocessamento em caso de falhas (DLQ)  

Essa abordagem evita gargalos e perda de mensagens.

---
#### Camada de Processamento

Implementa o fluxo principal de negócio:

**Classificação baseada em regras (Rule Classifier)**

- Baixa latência  
- Totalmente explicável  
- Resolve a maioria dos casos  

**Classificação com Machine Learning (Amazon Comprehend)**

- Executada apenas quando não há match por regras  
- Utiliza threshold de confiança  
- Fallback para revisão manual  

**Casos ambíguos ou de baixa confiança**

Esse modelo híbrido reduz custo, aumenta precisão e facilita auditoria.

---
#### Camada de Dados

Responsável por persistência:

- DynamoDB para reclamações e estados do fluxo  
- S3 para documentos e anexos  

A separação entre dados estruturados e não estruturados simplifica escalabilidade e governança.

---
#### Camada de Exposição de Dados

Disponibiliza as informações para:

- Portal interno  
- Integrações com sistemas legados  

Feita via API REST, mantendo o core do sistema isolado de consumidores externos.

---
#### Camada de Observabilidade

Centraliza logs, métricas e alertas:

- CloudWatch para métricas técnicas  
- Datadog para visualização, alertas e monitoramento de SLA  

---
### Resumo da Arquitetura

A arquitetura proposta prioriza:

- Desacoplamento  
- Evolução incremental  
- Simplicidade operacional  
- Observabilidade  
- Preparação para IA sem dependência imediata
