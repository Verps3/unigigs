from typing import Generic, TypeVar

from app.excepciones import NoEncontradoError

T = TypeVar("T")


class RepositorioMemoria(Generic[T]):
    """Persistencia en memoria del prototipo (los datos se pierden al reiniciar)."""

    def __init__(self, nombre: str) -> None:
        self._nombre = nombre
        self._items: dict[int, T] = {}
        self._siguiente_id = 1

    def agregar(self, item: T) -> T:
        item.id = self._siguiente_id  # type: ignore[attr-defined]
        self._items[self._siguiente_id] = item
        self._siguiente_id += 1
        return item

    def obtener(self, id: int) -> T:
        try:
            return self._items[id]
        except KeyError:
            raise NoEncontradoError(f"{self._nombre} {id} no existe.") from None

    def listar(self) -> list[T]:
        return list(self._items.values())
