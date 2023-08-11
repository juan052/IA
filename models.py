from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
db = SQLAlchemy()

class CategoriaProducto(db.Model):
    __tablename__ = 'categoria_producto'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    descripcion = db.Column(db.String(250))
    estado = db.Column(db.Integer)
    
    def __init__(self, nombre, descripcion, estado):
        self.nombre = nombre
        self.descripcion = descripcion
        self.estado = estado

    

class SubCategoriaProducto(db.Model):
    __tablename__ = 'sub_categoria_producto'

    id = db.Column(db.Integer, primary_key=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categoria_producto.id'))
    nombre = db.Column(db.String(250), nullable=False)
    descripcion = db.Column(db.String(250))
    estado = db.Column(db.Integer)
    categoria = relationship('CategoriaProducto')
    
    def __init__(self, id_categoria, nombre, descripcion, estado):
        self.id_categoria = id_categoria
        self.nombre = nombre
        self.descripcion = descripcion
        self.estado = estado

class Producto(db.Model):
    __tablename__ = 'producto'

    id = db.Column(db.Integer, primary_key=True)
    id_sub_categoria = db.Column(db.Integer, db.ForeignKey('sub_categoria_producto.id'))
    nombre = db.Column(db.String(120), nullable=False)
    descripcion = db.Column(db.String(250), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    logo=db.Column(db.String(250), nullable=False)
    estado = db.Column(db.Integer)
    subcategoria = relationship('SubCategoriaProducto')
    
    def __init__(self, id_sub_categoria, nombre, descripcion, cantidad,logo, estado):
        self.id_sub_categoria = id_sub_categoria
        self.nombre = nombre
        self.descripcion = descripcion
        self.cantidad = cantidad
        self.logo=logo
        self.estado = estado

class Precio(db.Model):
    __tablename__ = 'precio'

    id = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('producto.id'))
    precio_actual = db.Column(db.Numeric(10,2), nullable=False)
    precio_anterior = db.Column(db.Numeric(10,2), nullable=False)
    estado = db.Column(db.Integer)
    producto = relationship('Producto')
    
    def __init__(self,id_producto,precio_actual,precio_anterior,estado):
        self.id_producto=id_producto
        self.precio_actual=precio_actual
        self.precio_anterior=precio_anterior
        self.estado=estado

class Servicio(db.Model):
    __tablename__ = 'servicios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    descripcion = db.Column(db.String(250))
    foto = db.Column(db.String(250))
    estado = db.Column(db.Integer)

    def __init__(self, nombre, descripcion, foto, estado):
        self.nombre = nombre
        self.descripcion = descripcion
        self.foto = foto
        self.estado = estado


class PrecioServicio(db.Model):
    __tablename__ = 'precio_servicios'

    id = db.Column(db.Integer, primary_key=True)
    id_servicios = db.Column(db.Integer, db.ForeignKey('servicios.id'))
    precio_actual = db.Column(db.Numeric(10, 2), nullable=False)
    precio_anterior = db.Column(db.Numeric(10, 2))
    estado = db.Column(db.Integer)

    servicio = db.relationship('Servicio')
    def __init__(self, id_servicios, precio_actual, precio_anterior, estado):
        self.id_servicios = id_servicios
        self.precio_actual = precio_actual
        self.precio_anterior = precio_anterior
        self.estado = estado

class Persona(db.Model):
    __tablename__ = 'persona'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    correo = db.Column(db.String(150), nullable=False)
    direccion = db.Column(db.String(250), nullable=False)
    celular = db.Column(db.Integer)
    persona_natural = db.relationship('PersonaNatural', uselist=False)
    def __init__(self, nombre, correo, direccion, celular=None):
        self.nombre = nombre
        self.correo = correo
        self.direccion = direccion
        self.celular = celular


class PersonaNatural(db.Model):
    __tablename__ = 'persona_natural'

    id = db.Column(db.Integer, primary_key=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('persona.id'))
    apellido = db.Column(db.String(250), nullable=False)
    cedula = db.Column(db.String(80))
    fecha_nacimiento = db.Column(db.Date)
    genero = db.Column(db.CHAR)
    persona = relationship('Persona', back_populates='persona_natural')

    def __init__(self, id_persona, apellido, cedula, fecha_nacimiento, genero):
        self.id_persona = id_persona
        self.apellido = apellido
        self.cedula = cedula
        self.fecha_nacimiento = fecha_nacimiento
        self.genero = genero


class PersonaJuridica(db.Model):
    __tablename__ = 'persona_juridica'

    id = db.Column(db.Integer, primary_key=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('persona.id'))
    ruc = db.Column(db.String(250), nullable=False)
    razon_social = db.Column(db.String(250))
    fecha_constitucional = db.Column(db.Date)
    persona = relationship('Persona')



class Clientes(db.Model):
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('persona.id'))
    tipo_cliente = db.Column(db.String(250), nullable=False)
    foto = db.Column(db.String(250))
    estado = db.Column(db.Integer)
    persona = relationship('Persona')

    def __init__(self, id_persona, tipo_cliente, foto=None, estado=None):
        self.id_persona = id_persona
        self.tipo_cliente = tipo_cliente
        self.foto = foto
        self.estado = estado


class Trabajador(db.Model):
    __tablename__ = 'trabajador'

    id = db.Column(db.Integer, primary_key=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('persona.id'))
    foto = db.Column(db.String(250))
    estado = db.Column(db.Integer)
    persona = relationship('Persona')
    def __init__(self,id_persona,foto,estado):
        self.id_persona=id_persona
        self.foto=foto
        self.estado=estado

class Salario(db.Model):
    __tablename__ = 'salario'

    id = db.Column(db.Integer, primary_key=True)
    id_trabajador = db.Column(db.Integer, db.ForeignKey('trabajador.id'))
    salario_actual = db.Column(db.Numeric(10,2), nullable=False)
    salario_anterior = db.Column(db.Numeric(10,2))
    estado = db.Column(db.Integer)
    trabajador= relationship('Trabajador')
    def __init__(self,id_trabajador,salario_actual,salario_anterior,estado):
        self.id_trabajador=id_trabajador
        self.salario_actual=salario_actual
        self.salario_anterior=salario_anterior
        self.estado=estado


class Cliente(db.Model):
    __tablename__ = 'clientes'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('persona.id'))
    tipo_cliente = db.Column(db.String(250), nullable=False)
    foto = db.Column(db.String(250))
    estado = db.Column(db.Integer)
    persona = relationship('Persona')
    def __init__(self, id_persona, tipo_cliente, foto, estado):
        self.id_persona = id_persona
        self.tipo_cliente = tipo_cliente
        self.foto = foto
        self.estado = estado

class GrupoUsuarios(db.Model):
    __tablename__ = 'grupo_usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    descripcion = db.Column(db.String(250), nullable=False)
    estado = db.Column(db.Integer)

    def __init__(self, nombre, descripcion, estado):
        self.nombre = nombre
        self.descripcion = descripcion
        self.estado = estado

class Usuario(db.Model):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    id_grupo = db.Column(db.Integer, db.ForeignKey('grupo_usuarios.id'))
    id_persona = db.Column(db.Integer, db.ForeignKey('persona.id'))
    usuario = db.Column(db.String(200), nullable=False)
    contraseña = db.Column(db.String(250), nullable=False)
    estado = db.Column(db.Integer)
    grupo = relationship('GrupoUsuarios')

    def __init__(self, id_grupo, id_persona, usuario, contraseña, estado):
        self.id_grupo = id_grupo
        self.id_persona = id_persona
        self.usuario = usuario
        self.contraseña = contraseña
        self.estado = estado

class TipoVenta(db.Model):
    __tablename__ = 'tipo_venta'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(250), nullable=False)
    descripcion = db.Column(db.String(250))
    estado = db.Column(db.Integer)

    def __init__(self, nombre, descripcion, estado):
        self.nombre = nombre
        self.descripcion = descripcion
        self.estado = estado 
class Personalizacion(db.Model):
    __tablename__ = 'personalizacion'

    id = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    descripcion = db.Column(db.String(250))
    fotos = db.Column(db.String(150))
    presupuesto = db.Column(db.Numeric)
    estado = db.Column(db.Integer)
    cliente = relationship('Cliente')

    def __init__(self,id_cliente, descripcion, fotos, presupuesto, estado):
        self.id_cliente=id_cliente
        self.descripcion = descripcion
        self.fotos = fotos
        self.presupuesto = presupuesto
        self.estado = estado


class DetallePersonalizacion(db.Model):
    __tablename__ = 'detalle_personalizacion'

    id = db.Column(db.Integer, primary_key=True)
    id_personalizacion = db.Column(db.Integer, db.ForeignKey('personalizacion.id'))
    costo_total = db.Column(db.Numeric)
    nota = db.Column(db.Text)
    fecha_entrega = db.Column(db.Date)

    personalizacion = db.relationship('Personalizacion')

    def __init__(self, id_personalizacion, costo_total, nota, fecha_entrega):
        self.id_personalizacion = id_personalizacion
        self.costo_total = costo_total
        self.nota = nota
        self.fecha_entrega = fecha_entrega

class Venta(db.Model):
    __tablename__ = 'venta'

    id = db.Column(db.Integer, primary_key=True)
    id_tipo = db.Column(db.Integer, db.ForeignKey('tipo_venta.id'))
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    fecha = db.Column(db.Date)
    codigo=db.Column(db.String(250))
    tipo_entrega=db.Column(db.String(500))
    estado = db.Column(db.Integer)
    tipo_venta = relationship('TipoVenta')
    cliente = relationship('Cliente')

    def __init__(self, id_tipo, id_cliente, fecha,codigo,tipo_entrega, estado):
        self.id_tipo = id_tipo
        self.id_cliente = id_cliente
        self.fecha = fecha
        self.codigo=codigo
        self.tipo_entrega=tipo_entrega
        self.estado = estado


class DetalleVenta(db.Model):
    __tablename__ = 'detalle_venta'

    id = db.Column(db.Integer, primary_key=True)
    id_venta = db.Column(db.Integer, db.ForeignKey('venta.id'))
    id_producto = db.Column(db.Integer, db.ForeignKey('producto.id'))
    subtotal = db.Column(db.Numeric, nullable=False)
    descuento = db.Column(db.Numeric, nullable=False)
    total = db.Column(db.Numeric, nullable=False)
    producto = relationship('Producto')
    venta = relationship('Venta')
    def __init__(self, id_venta, id_producto, subtotal, descuento, total):
        self.id_venta = id_venta
        self.id_producto = id_producto
        self.subtotal = subtotal
        self.descuento = descuento
        self.total = total

class VentaPersonalizacion(db.Model):
    __tablename__ = 'venta_personalizacion'

    id = db.Column(db.Integer, primary_key=True)
    id_venta = db.Column(db.Integer, db.ForeignKey('venta.id'))
    id_personalizacion = db.Column(db.Integer, db.ForeignKey('personalizacion.id'))
    subtotal = db.Column(db.Numeric, nullable=False)
    descuento = db.Column(db.Numeric, nullable=False)
    total = db.Column(db.Numeric, nullable=False)

    venta = relationship('Venta')
    personalizacion = relationship('Personalizacion')

    def __init__(self, id_venta, id_personalizacion, subtotal, descuento, total):
        self.id_venta = id_venta
        self.id_personalizacion = id_personalizacion
        self.subtotal = subtotal
        self.descuento = descuento
        self.total = total


class VentaServicios(db.Model):
    __tablename__ = 'venta_servicios'

    id = db.Column(db.Integer, primary_key=True)
    id_venta = db.Column(db.Integer, db.ForeignKey('venta.id'))
    id_reservacion = db.Column(db.Integer, db.ForeignKey('servicios.id'))
    subtotal = db.Column(db.Numeric, nullable=False)
    descuento = db.Column(db.Numeric, nullable=False)
    total = db.Column(db.Numeric, nullable=False)

    venta = relationship('Venta')
    reservacion = relationship('Servicio')

    def __init__(self, id_venta, id_reservacion, subtotal, descuento, total):
        self.id_venta = id_venta
        self.id_reservacion = id_reservacion
        self.subtotal = subtotal
        self.descuento = descuento
        self.total = total
class Modulo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(250))
    icono = db.Column(db.String(500))
    estado = db.Column(db.Integer)
   
    def __init__(self, nombre, icono, estado):
        self.nombre = nombre
        self.icono = icono
        self.estado = estado

class SubModulo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_modulo = db.Column(db.Integer, db.ForeignKey('modulo.id'))
    nombre = db.Column(db.String(250), nullable=False)
    enlace = db.Column(db.String(500), nullable=False)

    modulo = db.relationship('Modulo')

    def __init__(self, id_modulo, nombre, enlace):
        self.id_modulo = id_modulo
        self.nombre = nombre
        self.enlace = enlace
