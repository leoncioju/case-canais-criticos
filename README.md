# Case Canais Críticos 🏦

Solução de classificação automática de reclamações bancárias que integra **regras de negócio** com **Machine Learning** para acelerar o processamento e melhorar a experiência do cliente.

## 📋 O Case

Um banco recebe **milhares de reclamações diárias** através de múltiplos canais (digital, físico, phone).

## ✅ A Solução

Sugestão de arquitetura que utiliza um **classificador híbrido** que:

1. **Normaliza o texto** - Remove acentos, maiúsculas e variações
2. **Tenta regras primeiro** - Classificação baseada em palavras-chave (rápido, grátis)
3. **Usa ML como fallback** - Amazon Comprehend para casos ambíguos
4. **Marca para revisão** - Casos com baixa confiança vão para humanos

### Arquitetura da Solução

![Arquitetura da Solução](desenho-solucao/arq.png)
 

## 📖 Documentação Detalhada

### Compreensão do Desafio
Leia [TOPICO_1_CLASSIFICACAO.md](desenho-solucao/TOPICO_1_CLASSIFICACAO.md) para entender o desafio e a solução implementada.

### Fluxo do Sistema
Veja [TOPICO_2_FLUXO.md](desenho-solucao/TOPICO_2_FLUXO.md) para o fluxo geral de processamento.

### Arquitetura
Estude [TOPICO_3_ARQUITETURA.md](desenho-solucao/TOPICO_3_ARQUITETURA.md) para Clean Architecture e DDD.

### Componentes
Veja [TOPICO_4_COMPONENTES.md](desenho-solucao/TOPICO_4_COMPONENTES.md) para exemplo detalhado do HybridClassifier.

### Tech Stack
Consulte [TOPICO_5_LINGUAGENS_DADOS.md](desenho-solucao/TOPICO_5_LINGUAGENS_DADOS.md) para Python + DynamoDB.

### IA & Machine Learning
Leia [TOPICO_6_IA.md](desenho-solucao/TOPICO_6_IA.md) para integração com Comprehend e Textract.


## 🔧 Tecnologias Utilizadas

- **Python 3.12** - Linguagem principal
- **pytest** - Framework de testes
- **unicodedata** - Normalização de texto Unicode
- **re** - Expressões regulares com word boundaries
- **AWS** - Arquitetura cloud 
