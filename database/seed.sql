INSERT INTO roles (id, nombre) VALUES
(1, 'Solicitante'),
(2, 'Responsable TI')
ON CONFLICT(id) DO UPDATE SET nombre = excluded.nombre;

INSERT INTO usuarios (id, nombre, correo, rol_id, activo) VALUES
(1, 'Juan Pérez', 'juan.perez@empresa.cl', 1, 1),
(2, 'Camila Soto', 'camila.soto@empresa.cl', 1, 1),
(3, 'Felipe Morales', 'felipe.morales@empresa.cl', 1, 1),
(4, 'María Arias', 'maria.arias@empresa.cl', 2, 1),
(5, 'Gonzalo Saez', 'gonzalo.saez@empresa.cl', 2, 1),
(6, 'Ankatu Sanchez', 'ankatu.sanchez@empresa.cl', 2, 1)
ON CONFLICT(id) DO UPDATE SET
    nombre = excluded.nombre,
    correo = excluded.correo,
    rol_id = excluded.rol_id,
    activo = excluded.activo;

INSERT INTO categorias (id, nombre, activa) VALUES
(1, 'Hardware', 1),
(2, 'Software', 1),
(3, 'Redes', 1),
(4, 'Acceso', 1),
(5, 'Otros', 1)
ON CONFLICT(id) DO UPDATE SET
    nombre = excluded.nombre,
    activa = excluded.activa;

INSERT INTO prioridades (id, nombre, orden) VALUES
(1, 'Baja', 1),
(2, 'Media', 2),
(3, 'Alta', 3),
(4, 'Crítica', 4)
ON CONFLICT(id) DO UPDATE SET
    nombre = excluded.nombre,
    orden = excluded.orden;

INSERT INTO estados (id, nombre, orden) VALUES
(1, 'Nuevo', 1),
(2, 'En proceso', 2),
(3, 'Resuelto', 3),
(4, 'Cerrado', 4)
ON CONFLICT(id) DO UPDATE SET
    nombre = excluded.nombre,
    orden = excluded.orden;
