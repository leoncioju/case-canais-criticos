import re
import unicodedata


def normalizar_texto(texto: str) -> str:
    """Remove acentos, converte para minúsculas e normaliza espaços."""
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join([c for c in texto if not unicodedata.combining(c)])
    return texto.lower()


def classificar_reclamacao(
    texto: str, 
    categorias: dict[str, list[str]]
) -> dict:
    """
    Classifica uma reclamação por palavras-chave.
    
    Args:
        texto: Texto da reclamação
        categorias: Dict {categoria: [palavras_chave]}
        
    Returns:
        Dict com:
            - categorias: lista de categorias encontradas
            - detalhes: dict com as palavras-chave que triggou cada categoria
    """
    texto_normalizado = normalizar_texto(texto)
    categorias_encontradas = []
    detalhes = {}

    for categoria, palavras_chave in categorias.items():
        palavras_encontradas = []
        
        for palavra in palavras_chave:
            palavra_normalizada = normalizar_texto(palavra)
            # \b = word boundary (evita falsos positivos como "valor" em "valorização")
            if re.search(rf'\b{re.escape(palavra_normalizada)}\b', texto_normalizado):
                palavras_encontradas.append(palavra)

        if palavras_encontradas:
            categorias_encontradas.append(categoria)
            detalhes[categoria] = palavras_encontradas

    return {
        "categorias": categorias_encontradas,
        "detalhes": detalhes
    }
