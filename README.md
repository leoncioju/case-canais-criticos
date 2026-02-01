# Case Canais Críticos 🏦

Um sistema inteligente de classificação de reclamações bancárias que normaliza e categoriza feedbacks de clientes através de processamento de linguagem natural.

## 📌 Sobre o Projeto

Este projeto implementa um **classificador de reclamações baseado em palavras-chave** com suporte a:
- Normalização de texto (acentos, case-sensitivity)
- Detecção de múltiplas categorias por reclamação
- Rastreamento das palavras-chave que triggerou cada classificação
- Proteção contra falsos positivos usando word boundaries

## 🏗️ Estrutura do Projeto

```
.
├── implementacao.py                # Código principal (funções de classificação)
├── test_implementacao.py           # Suite de testes unitários (pytest)
├── README.md                       # Documentação do projeto
├── ARQUITETURA_AWS.md             # Arquitetura cloud da solução
├── TOPICO_1_IMPLEMENTACAO.md      # Detalhes técnicos da implementação
├── TOPICO_2_FLUXO.md              # Fluxo geral do sistema
└── arquitetura-aws.drawio         # Diagrama da arquitetura
```

## 🚀 Quick Start

### Pré-requisitos
- Python 3.8+
- pip

### Instalação

```bash
# Instalar dependências
pip install pytest pytest-cov
```

### Executar Testes

```bash
# Rodar todos os testes
pytest test_implementacao.py -v

# Rodar com cobertura de código
pytest test_implementacao.py --cov=implementacao --cov-report=html

# Visualizar cobertura (abre em navegador)
# htmlcov/index.html
```

## 📚 API da Solução

### `normalizar_texto(texto: str) -> str`

Remove acentos, converte para minúsculas e normaliza espaços.

**Exemplo:**
```python
from implementacao import normalizar_texto

normalizar_texto("São Paulo")  # "sao paulo"
normalizar_texto("NÃO Consigo")  # "nao consigo"
```

### `classificar_reclamacao(texto: str, categorias: dict) -> dict`

Classifica uma reclamação em múltiplas categorias usando palavras-chave.

**Parâmetros:**
- `texto`: String com o texto da reclamação
- `categorias`: Dicionário no formato `{categoria: [palavras_chave]}`

**Retorno:**
```python
{
    "categorias": ["acesso", "aplicativo"],  # Categorias encontradas
    "detalhes": {
        "acesso": ["acessar", "login"],
        "aplicativo": ["app", "travando"]
    }
}
```

**Exemplo de Uso:**

```python
from implementacao import classificar_reclamacao

categorias = {
    "acesso": ["acessar", "login", "senha"],
    "aplicativo": ["app", "aplicativo", "travando", "erro"],
    "cobranca": ["fatura", "cobranca", "valor", "indevido"],
}

texto = "Estou com problemas para acessar minha conta e o aplicativo está travando."
resultado = classificar_reclamacao(texto, categorias)

print(resultado)
# {
#     'categorias': ['acesso', 'aplicativo'],
#     'detalhes': {
#         'acesso': ['acessar'],
#         'aplicativo': ['aplicativo', 'travando']
#     }
# }
```

## ✅ Cobertura de Testes

A suite de testes cobre os seguintes cenários:

| Cenário | Teste |
|---------|-------|
| Conversão para minúsculas | `test_converter_para_minusculas` |
| Remoção de acentos | `test_remover_acentos` |
| Normalização combinada | `test_normalizar_combinado` |
| Múltiplas categorias | `test_multiplas_categorias` |
| Sem categoria encontrada | `test_sem_categoria_encontrada` |
| Evita falsos positivos (substring) | `test_evita_falso_positivo_substring` |
| Encontra palavra completa | `test_encontra_valor_como_palavra_completa` |
| Normaliza acentos na classificação | `test_normaliza_acentos_na_classificacao` |
| Detalhes com palavras encontradas | `test_detalhes_contem_palavras_encontradas` |
| Estrutura de resposta | `test_estrutura_resposta` |
| Múltiplas palavras por categoria | `test_categorias_multiplas_palavras` |

## 🔍 Detalhes Técnicos

### Word Boundaries
A implementação usa regex com `\b` para evitar falsos positivos:
```python
# ✅ Encontra "valor" em "O valor está errado"
# ❌ Não encontra "valor" em "A valorização do imóvel"
if re.search(rf'\b{re.escape(palavra_normalizada)}\b', texto_normalizado):
```

### Normalização de Acentos
Utiliza `unicodedata` para decomposição e remoção de caracteres de combinação:
```python
texto = unicodedata.normalize('NFKD', texto)
texto = ''.join([c for c in texto if not unicodedata.combining(c)])
```

## 🏛️ Arquitetura da Solução

```
┌─────────────────────┐
│  Reclamação (texto) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────┐
│  normalizar_texto()         │  (acentos → minúsculas)
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  classificar_reclamacao()   │  (word boundary search)
└──────────┬──────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ {"categorias": [...],        │
│  "detalhes": {...}}          │
└──────────────────────────────┘
```

Para arquitetura cloud completa, consulte [ARQUITETURA_AWS.md](ARQUITETURA_AWS.md).

## 📋 Documentação Adicional

- [TOPICO_1_IMPLEMENTACAO.md](TOPICO_1_IMPLEMENTACAO.md) - Detalhes técnicos da implementação
- [TOPICO_2_FLUXO.md](TOPICO_2_FLUXO.md) - Fluxo geral e diagrama do sistema
- [ARQUITETURA_AWS.md](ARQUITETURA_AWS.md) - Arquitetura cloud completa da solução

## 💡 Caso de Uso

Um cliente bancário reclamando sobre problemas de acesso pode enviar:

> "Não consigo acessár minha conta! O aplicativo está travando e a senha não funciona mais. Preciso de sócorro urgente!"

A função classifica automaticamente em:
- ✅ **acesso** (encontrou: "acessar", "senha")
- ✅ **aplicativo** (encontrou: "aplicativo", "travando")
- ✅ **seguros** (encontrou: "sócorro" → "socorro" após normalização)

Isso permite que o banco direcione a reclamação para o departamento correto automaticamente.

## 🔧 Tecnologias Utilizadas

- **Python 3.8+** - Linguagem principal
- **pytest** - Framework de testes
- **unicodedata** - Normalização de texto Unicode
- **re** - Expressões regulares com word boundaries
- **AWS** - Arquitetura cloud (opcional)

## 📝 Licença

Este projeto é um case de estudo para demonstrar boas práticas em classificação de texto e arquitetura de sistemas bancários.

## 👤 Autor

Desenvolvido como um case prático de processamento de reclamações bancárias.