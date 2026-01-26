# MicroPython Compatibility

Esta rama contiene una versión del SPV client compatible con MicroPython.

## Cambios Realizados

### 1. Eliminación de Keyword Arguments en `to_bytes()`

MicroPython no soporta keyword arguments en el método `to_bytes()`. Se cambiaron todos los usos:

```python
# Antes (Python estándar)
n.to_bytes(4, byteorder="little")

# Ahora (MicroPython compatible)
n.to_bytes(4, "little")
```

**Archivos modificados:**
- `spv/utils/byte.py` - create_varint()
- `spv/messages/version.py` - create_version()
- `spv/messages/default.py` - create_feefilter()

### 2. Compatibilidad Total

Los siguientes métodos ya eran compatibles:
- `int.from_bytes(data, "little")` - No usa keyword arguments ✓
- `str.encode()` - Compatible ✓
- `bytes.decode()` - Compatible ✓

## Uso con MicroPython

```bash
# En lugar de
python3 __main__.py

# Usar
micropython __main__.py
```

## Diferencias entre Ramas

| Rama | Python Version | Keyword Args | Estado |
|------|---------------|--------------|--------|
| `master` | CPython 3.6+ | Sí | Estable |
| `micropython` | MicroPython | No | Experimental |

## Limitaciones Conocidas

1. **DNS Seeds:** MicroPython puede tener limitaciones en `socket.getaddrinfo()`
2. **Threading:** Si usas múltiples conexiones, verifica compatibilidad de `_thread`
3. **Memoria:** MicroPython tiene menos memoria RAM disponible

## Testing

Para probar que los cambios funcionan:

```bash
# Verificar sintaxis
micropython -m py_compile spv/peer.py

# Ejecutar cliente
micropython __main__.py
```

## Volver a Master

```bash
git checkout master
```
