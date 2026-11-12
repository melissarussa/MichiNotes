from .items.dibujo import ItemDibujo
from .items.enlace import ItemEnlace
from .items.figura import ItemFigura
from .items.imagen import ItemImagen
from .items.lista import ItemLista
from .items.nota import ItemNota, ItemTexto

CLASES = {"nota": ItemNota, "texto": ItemTexto, "lista": ItemLista, "enlace": ItemEnlace,
          "figura": ItemFigura, "imagen": ItemImagen, "dibujo": ItemDibujo}


def crear_item(elemento, ctx):
    """Fábrica: el tipo guardado en la base decide qué clase gráfica se crea."""
    return CLASES[elemento.tipo](elemento, ctx)
