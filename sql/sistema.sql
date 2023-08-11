INSERT INTO modulo(nombre,icono,estado)
VALUES('Dashboard','fas fa-chart-line',1),
      ('Gestion de productos','fas fa-box-open',1),
      ('Gestion de servicios','fa-clipboard-list',1),
      ('Gestion de colaborador','fas fa-user-tie',1),
      ('Gestion de pedidos','fas fa-receipt',1),
      ('Gestion de ventas','fas fa-shopping-cart',1),
      ('Gestion de usuarios','fas fa-users',1);


INSERT INTO sub_modulo(id_modulo,nombre,enlace)VALUES(1,'Dashboard','/dashboard'),
(2,'Categorias','/categoria'),(2,'Sub categoria','/sub'),(2,'Productos','/producto'),
(2,'Precio productos','/precio_producto'),(3,'Servicios','/servicios'),(3,'Precios servicios','/precio_servicios'),
(4,'Colaboradores','/trabajador'),(4,'Salarios','/salarios'),(5,'Pedidos','/personalizaciones'),
(6,'Ventas','/ventas'),(6,'Clientes','/clientes'),(7,'Usuarios','/usuarios'),(7,'Accesos','/modulos'),(7,'Permisos','/permisos');

/*Consulta de verificacion*/
SELECT m.id AS modulo_id, m.nombre AS modulo_nombre, 
                sm.id AS submodulo_id, sm.nombre AS submodulo_nombre
            FROM modulo m LEFT JOIN sub_modulo sm ON m.id = sm.id_modulo;

/*Permisos*/
INSERT INTO permiso (nombre) VALUES ('Crear'),('Actualizar'),('Eliminar'),('Anular');


/*Permisos por modulos*/
-- Insertar datos en la tabla 'permiso_modulo' para el módulo 'Dashboard'
INSERT INTO permiso_modulo (id_permiso, id_modulo)
VALUES
    (1, 1),
    (2, 1),
    (3, 1);

-- Insertar datos en la tabla 'permiso_modulo' para el módulo 'Gestion de productos'
INSERT INTO permiso_modulo (id_permiso, id_modulo)
VALUES
    (1, 2),
    (2, 2),
    (3, 2);

-- Insertar datos en la tabla 'permiso_modulo' para el módulo 'Gestion de servicios'
INSERT INTO permiso_modulo (id_permiso, id_modulo)
VALUES
    (1,3),
    (2,3),
    (3,3);

-- Insertar datos en la tabla 'permiso_modulo' para el módulo 'Gestion de colaborador'
INSERT INTO permiso_modulo (id_permiso, id_modulo)
VALUES
    (1,4),
    (2,4),
    (3,4);

-- Insertar datos en la tabla 'permiso_modulo' para el módulo 'Gestion de pedidos'
INSERT INTO permiso_modulo (id_permiso, id_modulo)
VALUES
    (1,5),
    (2,5),
    (3,5);

-- Insertar datos en la tabla 'permiso_modulo' para el módulo 'Gestion de ventas'
INSERT INTO permiso_modulo (id_permiso, id_modulo)
VALUES
    (1, 6),
    (2, 6),
    (4,6);

-- Insertar datos en la tabla 'permiso_modulo' para el módulo 'Gestion de usuarios'
INSERT INTO permiso_modulo (id_permiso, id_modulo)
VALUES
    (1, 7),
    (2, 7),
    (3, 7);


/*Consulta de verficacion*/
SELECT pm.id AS id_permiso_modulo, m.id AS id_modulo, m.nombre AS nombre_modulo, p.id AS id_permiso, p.nombre AS nombre_permiso
              FROM modulo m
              INNER JOIN permiso_modulo pm ON m.id = pm.id_modulo
              INNER JOIN permiso p ON pm.id_permiso = p.id
              WHERE m.estado = 1