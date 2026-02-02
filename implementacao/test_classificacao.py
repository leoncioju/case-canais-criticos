import pytest
from implementacao import classificar_reclamacao, normalizar_texto


class TestNormalizarTexto:
    """Testes da função de normalização de texto."""
    
    def test_converter_para_minusculas(self):
        assert normalizar_texto("ACESSO") == "acesso"
    
    def test_remover_acentos(self):
        assert normalizar_texto("São Paulo") == "sao paulo"
        assert normalizar_texto("não") == "nao"
        assert normalizar_texto("acessár") == "acessar"
    
    def test_normalizar_combinado(self):
        assert normalizar_texto("Não Consigo Acessár") == "nao consigo acessar"


class TestClassificarReclamacao:
    """Testes da função de classificação de reclamação."""
    
    @pytest.fixture
    def categorias(self):
        """Fixture com categorias padrão."""
        return {
            "imobiliario": ["credito imobiliario", "casa", "apartamento"],
            "seguros": ["resgate", "capitalizacao", "socorro"],
            "cobranca": ["fatura", "cobranca", "valor", "indevido"],
            "acesso": ["acessar", "login", "senha"],
            "aplicativo": ["app", "aplicativo", "travando", "erro"],
            "fraude": ["fatura", "nao reconhece divida", "fraude"]
        }
    
    def test_multiplas_categorias(self, categorias):
        """Testa classificação com múltiplas categorias encontradas."""
        texto = "Estou com problemas para acessar minha conta e o aplicativo está travando muito."
        resultado = classificar_reclamacao(texto, categorias)
        
        assert "acesso" in resultado["categorias"]
        assert "aplicativo" in resultado["categorias"]
        assert len(resultado["categorias"]) == 2
    
    def test_sem_categoria_encontrada(self, categorias):
        """Testa quando nenhuma categoria é encontrada."""
        texto = "O tempo está lindo hoje."
        resultado = classificar_reclamacao(texto, categorias)
        
        assert resultado["categorias"] == []
        assert resultado["detalhes"] == {}
    
    def test_evita_falso_positivo_substring(self, categorias):
        """Testa que não encontra 'valor' em 'valorização' (word boundary)."""
        texto = "A valorização do imóvel está em alta."
        resultado = classificar_reclamacao(texto, categorias)
        
        # "valor" está em "valorização" mas não deve ser encontrado
        assert resultado["categorias"] == []
    
    def test_encontra_valor_como_palavra_completa(self, categorias):
        """Testa que encontra 'valor' quando é uma palavra completa."""
        texto = "O valor da cobrança está indevido."
        resultado = classificar_reclamacao(texto, categorias)
        
        assert "cobranca" in resultado["categorias"]
        assert "valor" in resultado["detalhes"]["cobranca"]
    
    def test_normaliza_acentos_na_classificacao(self, categorias):
        """Testa que normaliza acentos durante a classificação."""
        texto = "Não consigo acessár e preciso de sócorro urgente!"
        resultado = classificar_reclamacao(texto, categorias)
        
        assert "acesso" in resultado["categorias"]
        assert "seguros" in resultado["categorias"]
    
    def test_detalhes_contem_palavras_encontradas(self, categorias):
        """Testa que detalhes retorna as palavras-chave encontradas."""
        texto = "Problemas para acessar login com erro na senha."
        resultado = classificar_reclamacao(texto, categorias)
        
        assert "acesso" in resultado["categorias"]
        assert "acessar" in resultado["detalhes"]["acesso"]
        assert "login" in resultado["detalhes"]["acesso"]
        assert "senha" in resultado["detalhes"]["acesso"]
    
    def test_estrutura_resposta(self, categorias):
        """Testa que a resposta tem a estrutura esperada."""
        texto = "Acessar problemas."
        resultado = classificar_reclamacao(texto, categorias)
        
        assert isinstance(resultado, dict)
        assert "categorias" in resultado
        assert "detalhes" in resultado
        assert isinstance(resultado["categorias"], list)
        assert isinstance(resultado["detalhes"], dict)
    
    def test_categorias_multiplas_palavras(self, categorias):
        """Testa categoria que encontra múltiplas palavras-chave."""
        texto = "Fatura com valor indevido e cobrança errada."
        resultado = classificar_reclamacao(texto, categorias)
        
        assert "cobranca" in resultado["categorias"]
        palavras = resultado["detalhes"]["cobranca"]
        assert len(palavras) >= 2  # Encontrou pelo menos 2 palavras-chave
