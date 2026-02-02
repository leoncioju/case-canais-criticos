## 4. Organização do Componente da Lambda Classificadora

A Lambda Classificadora foi estruturada de forma modular, seguindo princípios de **Clean Architecture** e **Single Responsibility**, permitindo fácil manutenção, testes e evolução do pipeline de classificação (regras + ML).

A organização separa claramente:

- Orquestração (handler)
- Regras de negócio
- Implementações de classificação
- Modelos de domínio
- Testes automatizados

### Estrutura de Diretórios

```text
src/
├── classifier/
│   ├── __init__.py
│   ├── category_rules.py
│   ├── rule_repository.py
│   ├── rule_classifier.py
│   ├── ml_classifier.py
│   └── hybrid_classifier.py
│
├── models/
│   ├── __init__.py
│   └── complaint.py
│
├── handler.py
├── rules_api_handler.py
│
└── tests/
    ├── fixtures/
    │   └── complaints.json
    ├── test_rule_classifier.py
    ├── test_ml_classifier.py
    └── test_hybrid_classifier.py

infra/
├── main.tf
├── variables.tf
├── iam.tf
├── envs/
│   ├── dev/
│   │   └── terraform.tfvars
│   ├── hom/
│   │   └── terraform.tfvars
│   └── prod/
│       └── terraform.tfvars