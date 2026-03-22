import re
import unicodedata
import logging


logger = logging.getLogger(__name__)


def normalizar_texto(texto: str) -> str:
    """Remove acentos, converte para minúsculas e normaliza espaços."""
    logger.debug("Iniciando normalização de texto", extra={"tamanho_texto": len(texto)})

    # Decompõe caracteres para separar letras dos acentos.
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join([c for c in texto if not unicodedata.combining(c)])
    texto_normalizado = texto.lower()

    logger.debug(
        "Texto normalizado com sucesso",
        extra={"tamanho_texto_normalizado": len(texto_normalizado)}
    )
    return texto_normalizado


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
    logger.info(
        "Iniciando classificação de reclamação",
        extra={"quantidade_categorias": len(categorias)}
    )

    texto_normalizado = normalizar_texto(texto)
    categorias_encontradas = []
    detalhes = {}

    for categoria, palavras_chave in categorias.items():
        logger.debug(
            "Avaliando categoria",
            extra={"categoria": categoria, "quantidade_palavras_chave": len(palavras_chave)}
        )

        palavras_encontradas = []
        
        for palavra in palavras_chave:
            palavra_normalizada = normalizar_texto(palavra)
            # Word boundary evita falso positivo por substring.
            if re.search(rf'\b{re.escape(palavra_normalizada)}\b', texto_normalizado):
                palavras_encontradas.append(palavra)
                logger.debug(
                    "Palavra-chave encontrada",
                    extra={"categoria": categoria, "palavra_chave": palavra}
                )

        if palavras_encontradas:
            categorias_encontradas.append(categoria)
            detalhes[categoria] = palavras_encontradas
            logger.info(
                "Categoria classificada",
                extra={"categoria": categoria, "palavras_encontradas": len(palavras_encontradas)}
            )

    logger.info(
        "Classificação finalizada",
        extra={"categorias_encontradas": len(categorias_encontradas)}
    )

    return {
        "categorias": categorias_encontradas,
        "detalhes": detalhes
    }
