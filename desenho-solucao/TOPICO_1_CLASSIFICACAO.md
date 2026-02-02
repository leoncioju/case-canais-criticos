# Tópico 1: Desafio de Lógica de Programação - Classificação Automática

## 📋 Enunciado do Desafio

> Imagine que você precisa implementar uma função que ajude na **classificação automática de reclamações** com base em palavras-chave. Cada reclamação contém um texto, e você tem uma lista de categorias com palavras associadas.

**Exemplo de entrada:**
```json
{
  "reclamacao": "Estou com problemas para acessar minha conta e o aplicativo está travando muito.",
  "categorias": {
    "imobiliario": ["credito imobiliario", "casa", "apartamento"],
    "seguro": ["resgate", "capitalização", "socorro"],
    "cobranca": ["fatura", "cobranca", "valor", "indevido"],
    "acesso": ["acessar", "login", "senha"],
    "aplicativo": ["app", "aplicativo", "travando", "erro"],
    "fraude": ["fatura", "nao reconhece divida", "fraude"]
  }
}
```

**Tarefa:** Implemente uma função que analise o texto da reclamação e retorne uma lista de categorias que se aplicam àquele texto.

---

## ✅ Solução Implementada

### Abordagem Escolhida: **Classificação por Palavras-Chave com Normalização**


#### **Função Principal: `classificar_reclamacao()`** (`classificacao.py`)

```python
from implementacao.classificacao import classificar_reclamacao

# Dados de entrada
texto = "Estou com problemas para acessar minha conta e o aplicativo está travando muito."
categorias = {
    "imobiliario": ["credito imobiliario", "casa", "apartamento"],
    "seguro": ["resgate", "capitalização", "socorro"],
    "cobranca": ["fatura", "cobranca", "valor", "indevido"],
    "acesso": ["acessar", "login", "senha"],
    "aplicativo": ["app", "aplicativo", "travando", "erro"],
    "fraude": ["fatura", "nao reconhece divida", "fraude"]
}

# Classificar reclamação
resultado = classificar_reclamacao(texto, categorias)

# Resultado
print(resultado)
```

**Output:**
```python
{
    "categorias": ["acesso", "aplicativo"],
    "detalhes": {
        "acesso": ["acessar"],
        "aplicativo": ["aplicativo", "travando"]
    }
}
```

#### **Função de Suporte: `normalizar_texto()`**

```python
from implementacao.classificacao import normalizar_texto

# Remove acentos, converte para minúsculas e normaliza espaços
texto_normalizado = normalizar_texto("Não CONSIGO ACESSAR minha conta")
# Resultado: "nao consigo acessar minha conta"
```

### 🎯 Características Principais

1. **Normalização de Texto**
   - Remove acentos e caracteres especiais
   - Converte para minúsculas
   - Normaliza espaços em branco
   - Trata variações como "não" vs "nao", "Ã" vs "A"

2. **Busca com Word Boundaries**
   - Usa regex com `\b` para evitar falsos positivos
   - "valor" não trigga "valorização"
   - "acessar" não trigga "inacessível"

3. **Multi-Label Classification**
   - Detecta **múltiplas categorias** em uma única reclamação
   - Retorna todas as categorias aplicáveis

4. **Detalhes de Matching**
   - Mostra exatamente quais palavras-chave foram encontradas
   - Facilita auditoria e debugging

---

## 💡 Melhorias Futuras

1. **Fuzzy matching** - Para detectar variações de digitação
2. **Pesos customizáveis** - Diferentes confianças por categoria
3. **Cache distribuído** - Para aplicações em larga escala
4. **Análise de urgência** - Detectar palavras que indicam prioridade

---

## 📚 Arquivos Relacionados

- **Código principal:** [implementacao/classificacao.py](../../implementacao/classificacao.py)
- **Testes:** [implementacao/test_classificacao.py](../../implementacao/test_classificacao.py)
