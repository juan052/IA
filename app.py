import os
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
import random
from user_agents import parse
from decimal import Decimal
import string
from flask import Flask, send_file, session, redirect, url_for, render_template, request, flash,jsonify
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from sqlalchemy import create_engine, text, not_,and_, func
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_sqlalchemy import SQLAlchemy
from models import *
from helper import *
from helper1 import *
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import outerjoin
from sqlalchemy.orm import aliased
from sqlalchemy.sql import exists, not_
from twilio.rest import Client
import cloudinary
import cloudinary.uploader
import cloudinary.api         
cloudinary.config( 
  cloud_name = "dxhb03y8f", 
  api_key = "372496255286474", 
  api_secret = "ZMvKkXyeuKc6FA7D_rVzYborrCg" 
)
app = Flask(__name__)

# Check for environment variable
# Set up database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SESSION_PERMANENT"] = False
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ingsoftwar123@gmail.com'
app.config['MAIL_PASSWORD'] = 'xishvjfvtnrabdpj'
app.secret_key = 'tu_clave_secreta'
account_sid = 'AC4758eb208264635a3c58aa454bd39dde'
auth_token = '5795809fa88e649a310bd23103afbbd0'
client = Client(account_sid, auth_token)

mail = Mail(app)
Session(app)
db.init_app(app)

engine = create_engine(os.getenv("DATABASE_URL"))
db_session = scoped_session(sessionmaker(bind=engine))

# Inicio
@app.route("/")
def index():
    usuario = session.get('cliente_id')
    if usuario is None:
        Precios = Precio.query.options(joinedload(Precio.producto)).limit(3).all()
        return render_template('index.html', Precios=Precios)
    else:
        Precios = Precio.query.options(joinedload(Precio.producto)).limit(3).all()
        return render_template('index.html', Precios=Precios, usuario=usuario)

@app.route("/home")
def home():
    usuario = session.get('cliente_id')
    if usuario is None:
        Precios = Precio.query.options(joinedload(Precio.producto)).limit(3).all()
        return render_template('index.html', Precios=Precios)
    else:
        Precios = Precio.query.options(joinedload(Precio.producto)).limit(3).all()
        return render_template('index.html', Precios=Precios, usuario=usuario)
    
@app.route("/logout/<int:id>", methods=["POST","GET"])
def logout(id): 
    conexion= Conexion.query.get(id)
    conexion.estado=2
    db.session.add(conexion)
    db.session.commit()


      # Borrar toda la sesión
    session.clear()

    # Redireccionar al inicio de sesión
    return redirect(url_for('home'))

@app.route("/acerca")
def acerca():
    usuario = session.get('cliente_id')
    if usuario is None:
        # La sesión no existe
        # Realiza alguna acción o redirige a otra página
        return render_template('about.html')
    else:
        # La sesión existe
        
        return render_template('about.html', usuario=usuario)

@app.route("/contacto")
def contacto():
    usuario = session.get('cliente_id')
    if usuario is None:
        # La sesión no existe
        # Realiza alguna acción o redirige a otra página
        return render_template('contacto.html')
    else:
        # La sesión existe
        
        return render_template('contacto.html', usuario=usuario)

@app.route("/shop")
def shop():
    usuario = session.get('cliente_id')
    Precios = Precio.query.join(Precio.producto).filter(Producto.cantidad > 0).options(joinedload(Precio.producto)).all()
    cliente_id = session.get('cliente_id')
    cantidad = Personalizacion.query.filter(Personalizacion.estado == 2, Personalizacion.id_cliente == cliente_id).count()
    confirmar = DetallePersonalizacion.query.join(DetallePersonalizacion.personalizacion).filter(Personalizacion.estado == 2, Personalizacion.id_cliente == cliente_id).all()
    
    return render_template('shop.html', Precios=Precios, usuario=usuario, cantidad=cantidad, confirmar=confirmar)
    
@app.route("/perfil/<int:id>", methods=["POST","GET"])
@login_requirede
def perfil(id):
    cliente = Clientes.query.get(id)
    
    if cliente is None:
        return "Cliente no encontrado", 404
    
    persona = db.session.query(Persona, PersonaNatural, PersonaJuridica).\
        select_from(Clientes).\
        join(Persona, Clientes.id_persona == Persona.id).\
        outerjoin(PersonaNatural, Persona.id == PersonaNatural.id_persona).\
        outerjoin(PersonaJuridica, Persona.id == PersonaJuridica.id_persona).\
        filter(Clientes.id == id).\
        first()

    if persona is None:
        return "Persona no encontrada", 404
    
    persona_obj, persona_natural, persona_juridica = persona
    
    return render_template("perfil.html", cliente=cliente, persona=persona_obj, persona_natural=persona_natural, persona_juridica=persona_juridica)

@app.route('/actualizar_clientes/<int:id>', methods=["GET", "POST"])
@login_requirede
def actualizar_clientes(id):
   
    cliente = Cliente.query.get(id)
    print(cliente)
    if request.method == "POST":
        # Obtener los datos del formulario
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        telefono = request.form.get("celular")
        fecha_nacimiento = request.form.get("fecha_nacimiento")
        cedula = request.form.get("cedula")
        genero = request.form.get("genero")
        direccion = request.form.get("direccion")
        logo = cliente.foto
        if 'foto' in request.files:
            archivo_foto = request.files['foto']
            if archivo_foto:
                try:
                    if logo:
                                # Obtén el public_id de Cloudinary desde la URL de la imagen anterior
                        public_id_anterior = logo.split('/')[-1].split('.')[0]
                                # Intenta eliminar la imagen anterior de Cloudinary
                        try:
                                cloudinary.api.delete_resources_by_prefix(public_id_anterior)
                        except cloudinary.exceptions.Error as delete_error:
                                print(f"Error al eliminar la imagen anterior: {delete_error}")

                            # Subir y transformar la nueva imagen
                        result = cloudinary.uploader.upload(archivo_foto,transformation={"width": 300, "height": 300})
                        secure_url = result["secure_url"]
                except cloudinary.exceptions.Error as upload_error:
                    flash("Error al actualizar la imagen: {}".format(str(upload_error)), "error")
                    return redirect('/perfil')  

                    
       
        # Actualizar los datos del cliente existente
        cliente.persona.nombre = nombre
      
        cliente.persona.direccion = direccion
        cliente.persona.celular = telefono
        cliente.persona.persona_natural.apellido = apellido
        cliente.persona.persona_natural.cedula = cedula
        cliente.persona.persona_natural.fecha_nacimiento = fecha_nacimiento
        cliente.persona.persona_natural.genero = genero
       
        cliente.foto = secure_url
       
        db.session.add(cliente)
        db.session.commit()
        session['cliente_foto'] =secure_url
        session['cliente_direccion']=cliente.persona.direccion
        flash("Se ha actualizado correctamente la informacion","success")
        return redirect(f'/perfil/{id}')

    return redirect(f'/perfil/{id}')

@app.route("/cambiar_contraseñas",methods=["GET","POST"])
@login_requirede
def cambiar_contraseñas():
    if request.method == "POST":
        id=request.form.get('id')
        id_cliente=request.form.get('id_cliente')
        usuario=Usuario.query.get(id)
        print(usuario)
        contraseña_anterior=request.form.get('contraseña_actual')
        contraseña_nueva =request.form.get('contraseña_nueva')
        confirmacion=request.form.get('confirmacion')
        usuario = Usuario.query.get(id)
        if usuario is None:
         # Manejar el caso cuando el usuario no existe
            return "El usuario no existe"

  
        if not check_password_hash(usuario.contraseña, contraseña_anterior):
        # Manejar el caso cuando la contraseña actual no coincide
            flash("La contraseña actual no coincide", "error")
            return redirect(f'/perfil/{id_cliente}')
    
        if contraseña_nueva != confirmacion:
            # Manejar el caso cuando la confirmación de contraseña no coincide
            flash("La contraseña nueva no coinciden.", "error")
            return redirect(f'/perfil/{id_cliente}')
          
        
        hashed_password = generate_password_hash(contraseña_nueva)
        usuario.contraseña=hashed_password
        db.session.commit()
        flash("Se ha cambiado la contraseña correctamente", "success")
        return redirect(f'/perfil/{id_cliente}')

@app.route("/pedido/<int:id>", methods=["GET","POST"])
@login_requirede
def pedido(id):
    cliente=Clientes.query.get(id)
    id=cliente.id
    pedidos = (
    DetallePersonalizacion.query
    .options(joinedload(DetallePersonalizacion.personalizacion))
    .filter(DetallePersonalizacion.personalizacion.has(id_cliente=id))
    .all())
    ventas=(DetalleVenta.query
            .options(joinedload(DetalleVenta.venta))
            .filter(DetalleVenta.venta.has(id_cliente=id))
            .all())
    return render_template("pedidos.html")

#Gestion de productos
@app.route("/categoria")
@login_required
def categoria():
    categorias = CategoriaProducto.query.all()
    return render_template('categoria.html', categorias=categorias)

@app.route("/crear_categoria", methods=["GET", "POST"])
@login_required
def crear_categoria():
    if request.method == "POST":
        nombre = request.form.get('nombre')
        descripcion= request.form.get('descripcion')
        estado = request.form.get('estado')
        categoria = CategoriaProducto(nombre=nombre, descripcion=descripcion, estado=estado)
        db.session.add(categoria)
        db.session.commit()
        flash("Se ha creado la nueva categoria","success")
        return redirect(url_for('categoria'))
    else:
        flash("No se ha creado la categoria","error")
        return redirect(url_for('categoria'))
    
@app.route("/editar_categoria/<int:id>", methods=["GET", "POST"])
@login_required
def editar_categoria(id):
    categoria = CategoriaProducto.query.get(id)
    if request.method == "POST":
        categoria.nombre = request.form.get('nombre')
        categoria.descripcion = request.form.get('descripcion')
        categoria.estado = request.form.get('estado')
        db.session.commit()
        flash("Se ha actualizado la categoria","success")
        return redirect(url_for('categoria'))
    else:
       flash("No se ha actualizado la categoria","error")
       return redirect(url_for('categoria'))
    
@app.route("/eliminar_categoria", methods=["POST"])
@login_required
def eliminar_categoria():
    categoria_id = request.form.get("id")
    categoria = CategoriaProducto.query.get(categoria_id)

    if categoria:
        # Cambiar el estado de la categoría a inactivo (estado = 2)
        categoria.estado = 2
        db.session.commit()
        flash("No se ha desactivado la categoria","success")

    flash("No se ha desactivado la categoria","error")
    return redirect(url_for('categoria'))

@app.route("/sub")
@login_required
def sub():
    categorias = CategoriaProducto.query.all()
    subcategorias = SubCategoriaProducto.query.options(joinedload(SubCategoriaProducto.categoria)).all()
    return render_template('sub_categoria.html', categorias=categorias, subcategorias=subcategorias)

@app.route("/crear_sub", methods=["GET", "POST"])
@login_required
def crear_sub():
   
    if request.method == "POST":
        categoria=request.form.get('categoria')
        nombre = request.form.get('nombre')
        descripcion= request.form.get('descripcion')
        estado = request.form.get('estado')
        sub = SubCategoriaProducto(id_categoria=categoria,nombre=nombre, descripcion=descripcion, estado=estado)
        db.session.add(sub)
        db.session.commit()
        flash("Se ha creado la Sub scategoria","success")
        return redirect(url_for('sub'))
    else:
        flash("No se ha creado la sub categoria","error")
        return redirect('/sub')
    

@app.route("/sub_actualizar/<int:id>", methods=["GET", "POST"])
@login_required
def sub_actualizar(id):
    sub = SubCategoriaProducto.query.get(id)
    if request.method == "POST":
        sub.id_categoria = request.form.get('categoria')
        sub.nombre = request.form.get('nombre')
        sub.descripcion = request.form.get('descripcion')
        sub.estado = request.form.get('estado')
        db.session.commit()
        flash("Se ha actualizado la sub categoria","success")
        return redirect(url_for('sub'))
    
    else:
        flash("No se ha actualizado la  sub categoria","error")
        return render_template('sub_categoria.html')


@app.route("/eliminar_sub", methods=["POST"])
@login_required
def eliminar_sub():
    sub_id = request.form.get("id")
    subcategoria = SubCategoriaProducto.query.get(sub_id)

    if subcategoria:
        # Cambiar el estado de la categoría a inactivo (estado = 2)
        subcategoria.estado = 2
        db.session.commit()
        flash("No se ha desactivado la categoria","succces")

    return redirect(url_for('sub'))

def select_categorias():
    categorias = {}

    subcategorias = (
        db.session.query(
            CategoriaProducto.id.label('categoria_id'),
            CategoriaProducto.nombre.label('categoria'),
            SubCategoriaProducto.id.label('subcategoria_id'),
            SubCategoriaProducto.nombre.label('subcategoria')
        )
        .join(SubCategoriaProducto, CategoriaProducto.id == SubCategoriaProducto.id_categoria)
        .all()
    )

    for row in subcategorias:
        categoria_id = row.categoria_id
        categoria = row.categoria
        subcategoria_id = row.subcategoria_id
        subcategoria = row.subcategoria

        if categoria_id not in categorias:
            categorias[categoria_id] = {
                'nombre': categoria,
                'subcategorias': [],
            }

        categorias[categoria_id]['subcategorias'].append({
            'id': subcategoria_id,
            'nombre': subcategoria,
        })

    return categorias

@app.route("/producto", methods=["GET", "POST"])
@login_required
def producto():
    
    producto = Producto.query.options(joinedload(Producto.subcategoria).joinedload(SubCategoriaProducto.categoria)).all()
    categorias = select_categorias()
    print(categorias)
    return render_template("producto.html", producto=producto,categorias=categorias)


@app.route("/producto_crear", methods=["GET","POST"])
@login_required
def producto_crear():
    if request.method == "POST":
        id_sub_categoria=request.form.get('subcategoria')
        nombre = request.form.get('nombre')
        descripcion= request.form.get('descripcion')
        cantidad=request.form.get('cantidad')
        estado = request.form.get('estado')
        logo = None
        if 'foto' in request.files:
            logo = request.files['foto']
            print(logo)
            if logo:
                
                result = cloudinary.uploader.upload(logo ,transformation={"width": 300, "height": 300})
                secure_url = result["secure_url"]
              
     
        producto=Producto(id_sub_categoria=id_sub_categoria, nombre=nombre, descripcion=descripcion, cantidad=cantidad,logo=secure_url, estado=estado)
        db.session.add(producto)
        db.session.commit()
        flash("Se ha creado el producto","success")
        return redirect(url_for('producto'))
    else:
        flash("No se ha creado el producto","error")
        return redirect(url_for('producto'))
    

@app.route("/producto_actualizar/<int:producto_id>", methods=["GET", "POST"])
@login_required
def producto_actualizar(producto_id):
    producto = Producto.query.get_or_404(producto_id)

    if request.method == "POST":
        id_sub_categoria = request.form.get('subcategoria')
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        cantidad = request.form.get('cantidad')
        estado = request.form.get('estado')
        logo = producto.logo

        if 'foto' in request.files:
            nueva_logo = request.files['foto']
            if nueva_logo:
                try:
                        if logo:
                            # Obtén el public_id de Cloudinary desde la URL de la imagen anterior
                            public_id_anterior = logo.split('/')[-1].split('.')[0]
                            # Intenta eliminar la imagen anterior de Cloudinary
                            try:
                                cloudinary.api.delete_resources_by_prefix(public_id_anterior)
                            except cloudinary.exceptions.Error as delete_error:
                                print(f"Error al eliminar la imagen anterior: {delete_error}")

                        # Subir y transformar la nueva imagen
                        result = cloudinary.uploader.upload(nueva_logo,transformation={"width": 300, "height": 300})
                        secure_url = result["secure_url"]
                except cloudinary.exceptions.Error as upload_error:
                    flash("Error al actualizar la imagen: {}".format(str(upload_error)), "error")
                    return redirect(url_for('producto'))

        producto.id_sub_categoria = id_sub_categoria
        producto.nombre = nombre
        producto.descripcion = descripcion
        producto.cantidad = cantidad
        producto.logo = secure_url if 'secure_url' in locals() else logo
        producto.estado = estado

        try:
            db.session.commit()
            flash("Se ha actualizado el producto", "success")
        except Exception as db_error:
            db.session.rollback()
            flash("Error al actualizar el producto: {}".format(str(db_error)), "error")
        
    return redirect(url_for('producto'))


@app.route("/eliminar_producto", methods=["POST"])
@login_required
def eliminar_producto():
    producto_id = request.form.get("id")
    
    productos = Producto.query.get(producto_id)
    
    if productos:
        # Cambiar el estado de la categoría a inactivo (estado = 2)
        productos.estado = 2
        db.session.commit()
        flash("Se ha desactivado el producto","success")

    return redirect(url_for('producto'))

def obtener_estructura_de_productos():
    subcategoria_alias = aliased(SubCategoriaProducto)
    productos = (
        Producto.query
        .options(
            joinedload(Producto.subcategoria).joinedload(SubCategoriaProducto.categoria)
        )
        .outerjoin(subcategoria_alias, Producto.subcategoria)
        .outerjoin(Precio, Producto.id == Precio.id_producto)
        .filter(Precio.id_producto == None)
        .all()
    )

    categorias_y_productos = {}

    for producto in productos:
        categoria_nombre = producto.subcategoria.categoria.nombre
        subcategoria_nombre = producto.subcategoria.nombre
        producto_nombre = producto.nombre
        id_producto = producto.id

        if categoria_nombre not in categorias_y_productos:
            categorias_y_productos[categoria_nombre] = {'subcategorias': {}}

        if subcategoria_nombre not in categorias_y_productos[categoria_nombre]['subcategorias']:
            categorias_y_productos[categoria_nombre]['subcategorias'][subcategoria_nombre] = {'productos': []}

        categorias_y_productos[categoria_nombre]['subcategorias'][subcategoria_nombre]['productos'].append({
            'nombre': producto_nombre,
            'id': id_producto
        })

    return categorias_y_productos


@app.route("/precio_producto",methods=["POST","GET"])
@login_required
def precio_producto():
   Precios=Precio.query.options(joinedload(Precio.producto)).all()
   categorias_y_productos = obtener_estructura_de_productos()

   return render_template("precio_producto.html",Precios=Precios,categorias_y_productos=categorias_y_productos)



@app.route("/crear_precio",methods=["GET","POST"])
@login_required
def crear_precio():
    if request.method == "POST":
        id_producto=request.form.get('producto')
        precio_actual = request.form.get('precio_actual')
        estado=request.form.get('estado')
        precio = Precio(id_producto=id_producto, precio_actual=precio_actual, precio_anterior=0, estado=estado)
        db.session.add(precio)
        db.session.commit()
        flash("Se ha asignado correctamente el precio","success")
        return redirect(url_for('precio_producto'))
    else:
        flash("No se ha asignado el precio correctamente","error")
        return redirect(url_for('precio_producto'))
    


@app.route("/actualizar_precio/<int:id>",methods=["GET","POST"])
@login_required
def actualizar_precio(id):
    precio = Precio.query.get(id)
    if request.method == "POST":
        
        precio_actual = request.form.get('precio_actual')
        precio_anterior=request.form.get('precio_anterior')
        estado=request.form.get('estado')
        if precio_actual and precio_actual.strip():  
            precio.precio_actual=precio_actual
            precio.precio_anterior=precio_anterior
            precio.estado=estado
            db.session.commit()
            flash("Se ha actualizado correctamente el precio","success")
            return redirect(url_for('precio_producto'))
        else:
            precio.estado=estado
            db.session.commit()
            flash("Se ha actualizado correctamente el estado del precio","success")
            return redirect(url_for('precio_producto'))
      
        
    else:
        return redirect(url_for('precio_Producto'))

@app.route("/eliminar_precio", methods=["POST"])
@login_required
def eliminar_precio():
    id = request.form.get("id")
    
    productos = Precio.query.get(id)
    
    if productos:
        # Cambiar el estado de la categoría a inactivo (estado = 2)
        productos.estado = 2
        db.session.commit()

    return redirect(url_for('precio_producto'))

@app.route("/trabajador",methods=["GET","POST"])
@login_required
def trabajador():
    trabajadores = Trabajador.query.options(joinedload(Trabajador.persona)).all()
    return render_template("trabajador.html", trabajadores=trabajadores) 


@app.route("/crear_trabajador",methods=["GET","POST"])
@login_required
def crear_trabajador():
    if request.method == "POST":
        nombre=request.form.get('nombre')
        apellido = request.form.get('apellido')
        cedula=request.form.get('cedula')
        fecha=request.form.get('fecha_nacimiento')
        correo=request.form.get('correo')
        direccion=request.form.get('direccion')
        genero=request.form.get('genero')
        celular=request.form.get('celular')
        estado=request.form.get('estado')
        logo = None
        if 'foto' in request.files:
            logo = request.files['foto']
            
            if logo:
                result = cloudinary.uploader.upload(logo ,transformation={"width": 300, "height": 300})
                secure_url = result["secure_url"]
        persona=Persona(nombre=nombre,correo=correo,direccion=direccion,celular=celular)
        db.session.add(persona)
        db.session.commit()
        id_persona=persona.id
        personanat=PersonaNatural(id_persona=id_persona,apellido=apellido,cedula=cedula,fecha_nacimiento=fecha,genero=genero)
        db.session.add(personanat)
        db.session.commit()
        colaborador=Trabajador(id_persona=id_persona,foto=secure_url,estado=estado)
        db.session.add(colaborador)
        db.session.commit()
        flash("Se ha agreado correctamente el colaborador","success")
        return redirect(url_for('trabajador'))
    else:
        flash("No se agrego ningun colaborador","error")
        return redirect(url_for('trabajador')) 


@app.route("/actualizar_trabajador/<int:id>", methods=["GET", "POST"])
@login_required
def actualizar_trabajador(id):
    trabajador = Trabajador.query.get_or_404(id)
    persona = Persona.query.get_or_404(trabajador.id_persona)
    personanat = PersonaNatural.query.get_or_404(trabajador.id_persona)
    print(personanat)
    if request.method == "POST":
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        cedula = request.form.get('cedula')
        fecha = request.form.get('fecha_nacimiento')
        correo = request.form.get('correo')
        direccion = request.form.get('direccion')
        genero = request.form.get('genero')
        celular = request.form.get('celular')
        estado = request.form.get('estado')
        logo = trabajador.foto
         
        if 'foto' in request.files:
            archivo_foto = request.files['foto']
            
            try:
                    if logo:
                            # Obtén el public_id de Cloudinary desde la URL de la imagen anterior
                        public_id_anterior = logo.split('/')[-1].split('.')[0]
                            # Intenta eliminar la imagen anterior de Cloudinary
                        try:
                                cloudinary.api.delete_resources_by_prefix(public_id_anterior)
                        except cloudinary.exceptions.Error as delete_error:
                            print(f"Error al eliminar la imagen anterior: {delete_error}")

                        # Subir y transformar la nueva imagen
                    result = cloudinary.uploader.upload(archivo_foto,transformation={"width": 300, "height": 300})
                    secure_url = result["secure_url"]
            except cloudinary.exceptions.Error as upload_error:
                flash("Error al actualizar la imagen: {}".format(str(upload_error)), "error")
                redirect(url_for('trabajador'))

        persona.nombre = nombre
        persona.correo = correo
        persona.direccion = direccion
        persona.celular = celular
        db.session.add(persona)
        db.session.commit()

        personanat.apellido = apellido
        personanat.cedula = cedula
        personanat.fecha_nacimiento = fecha
        personanat.genero = genero
        db.session.add(personanat)
        db.session.commit()

        trabajador.foto = secure_url
        trabajador.estado = estado
        db.session.add(trabajador)
        db.session.commit()
        flash("Se ha actualizado correctamente el colaborador","success")
        return redirect(url_for('trabajador'))
    else:
        return render_template('trabajador.html', trabajador=trabajador, persona=persona, personanat=personanat)

@app.route("/eliminar_trabajador",methods=["GET","POST"])
def eliminar_colaborador():
    if request.method == "POST":
        id=request.form.get('id')
        trabajador=Trabajador.query.get(id)
        if trabajador:
        # Cambiar el estado de la categoría a inactivo (estado = 2)
            trabajador.estado = 2
            db.session.commit()

        usuario=Usuario.query.filter_by(id_persona=trabajador.id_persona).first()
        if usuario:
        # Cambiar el estado de la categoría a inactivo (estado = 2)
            usuario.estado = 2
            db.session.commit()
        flash("Se ha desactivado correctamente el colaborador","success")
        return redirect(url_for('trabajador'))
    
    
    
    return redirect(url_for('trabajador'))


@app.route("/salarios",methods=["POST","GET"])
@login_required
def salario():
    salarios=Salario.query.options(joinedload(Salario.trabajador)).all()
    trabajadores_sin_salario = Trabajador.query.filter(
    not_(exists().where(Salario.id_trabajador == Trabajador.id))).all()
    return render_template("salarios.html",salarios=salarios,trabajadores_sin_salario=trabajadores_sin_salario)

@app.route("/crear_salarios",methods=["POST","GET"])
@login_required
def crear_salario():
    if request.method == "POST":
        id_trabajador=request.form.get('producto')
        print(id_trabajador)
        salario_actual = request.form.get('precio_actual')
        estado=request.form.get('estado')
        precio = Salario(id_trabajador=id_trabajador, salario_actual=salario_actual, salario_anterior=0, estado=estado)
        db.session.add(precio)
        db.session.commit()
        flash("Se ha asignado correctamente el salario","success")
        return redirect('/salarios')
    else:
        flash("No se ha asignado ningun salario","error")
        return redirect('/salarios')
    
@app.route("/actualizar_salarios/<int:id>",methods=["POST","GET"])
@login_required
def actualizar_salario(id):
    precio = Salario.query.get(id)
    if request.method == "POST":
        
        precio_actual = request.form.get('precio_actual')
        precio_anterior=request.form.get('precio_anterior')
        estado=request.form.get('estado')
        if precio_actual and precio_actual.strip():  
            precio.salario_actual=precio_actual
            precio.salario_anterior=precio_anterior
            precio.estado=estado
            db.session.commit()
            flash("Se ha realizado correctamente la asignacion del nuevo salario","success")
            return redirect('/salarios')
        else:
            print("No se realizo el cambio")
            precio.estado=estado
            db.session.commit()
            return redirect('/salarios')
    return redirect('/salarios')

@app.route("/eliminar_salarios",methods=["POST","GET"])
@login_required
def eliminar_salario():
    id = request.form.get("id")
    
    productos = Salario.query.get(id)
    
    if productos:
        # Cambiar el estado de la categoría a inactivo (estado = 2)
        productos.estado = 2
        db.session.commit()
        flash("Se desactivado el salario","success")
        return redirect('/salarios')
    
    return redirect('/salarios')


#Usuarios
@app.route("/usuarios",methods=["GET","POST"])
@login_required
def usuarios():
    
    usuarios = Usuario.query.order_by(Usuario.id_grupo).all()
    trabajadores = Trabajador.query.outerjoin(Usuario, and_(Usuario.id_persona == Trabajador.id_persona)).filter(Usuario.id_persona.is_(None)).all()
    

    return render_template("usuarios.html", trabajadores=trabajadores,usuarios=usuarios)


def generar_contraseña():
    caracteres = string.ascii_letters + string.digits  # Letras mayúsculas, minúsculas y dígitos
    longitud = 8
    contraseña = ''.join(random.choice(caracteres) for _ in range(longitud))
    return contraseña


@app.route("/crear_usuarios",methods=["GET","POST"])
@login_required
def crear_usuarios():
    if request.method == "POST":
        persona=request.form.get('id_persona')
        correo = request.form.get('correo')
        contraseña=generar_contraseña()
        cuerpo = '''
    Estimado(a) ,

    Aquí tienes la contraseña para acceder a tu cuenta:

    Contraseña: {0}

    Por favor, asegúrate de cambiar tu contraseña una vez que hayas iniciado sesión en tu cuenta.

    Si tienes alguna pregunta o necesitas asistencia adicional, no dudes en contactarnos.

    ¡Gracias y ten un excelente día!

    Atentamente, Luxx ART
    '''.format(contraseña)
        msg = Message('Asignacion de contraseña - Acceso a cuenta', sender='ingsoftwar123@gmail.com', recipients=[correo])
        msg.body = cuerpo
        mail.send(msg)
        hashed_password = generate_password_hash(contraseña)
        usuario = Usuario(id_grupo=1, id_persona=persona, usuario=correo, contraseña=hashed_password, estado=0)
        db.session.add(usuario)
        db.session.commit()
        flash("Se agregado correctamente el usuario!","success")
        flash("Se ha enviado un correo correctamente con la contraseña para su accesso ala plataforma ","info")
        return redirect("usuarios")
    return render_template("usuarios.html")

@app.route("/verificar_usuarios",methods=["GET","POST"])
def verificar():
    if request.method == "POST":
        id=request.form.get('id')
        usuario = Usuario.query.get(id)
        trabajador = Trabajador.query.filter_by(id_persona=usuario.id_persona).first()
        cliente = Clientes.query.filter_by(id_persona=usuario.id_persona).first()

        if trabajador :
            if trabajador.estado == 2:
                flash("No se puede activar el usuario, el trabajador está inactivo", "Error")
                return redirect(url_for('usuarios'))
            else:
                if usuario:
                    print("Hola estoy aqui")
                    # Cambiar el estado del usuario a verificado (estado = 1)
                    usuario.estado = 1
                    db.session.commit()
                    flash("Se ha verificado el usuario correctamente", "success")
                    return redirect(url_for('usuarios'))
                
        if cliente:
            if cliente.estado == 2:
                flash("No se puede activar el usuario, el cliente está inactivo", "Error")
                return redirect(url_for('usuarios'))
            else:
                if usuario:
                    print("Hola estoy aqui")
                    # Cambiar el estado del usuario a verificado (estado = 1)
                    usuario.estado = 1
                    db.session.commit()
                    flash("Se ha verificado el usuario correctamente", "success")
                    return redirect(url_for('usuarios'))

        flash("No se ha realizado ninguna operación", "error")

    return redirect(url_for('usuarios'))


@app.route("/eliminar_usuario",methods=["GET","POST"])
def eliminar_usuario():
    if request.method == "POST":
        id=request.form.get('id')
        usuario=Usuario.query.get(id)
        if usuario:
        # Cambiar el estado de la categoría a inactivo (estado = 2)
            usuario.estado = 2
            db.session.commit()
        flash("Se ha desactivado el usuario correctamente","success")
        return redirect(url_for('usuarios'))
    
    
    
    return redirect(url_for('usuarios'))

@app.route("/cambiar_contraseña",methods=["GET","POST"])
@login_required
def cambiar_contraseña():
    if request.method == "POST":
        id=request.form.get('id')
        usuario=Usuario.query.get(id)
        print(usuario)
        contraseña_anterior=request.form.get('contraseña_actual')
        contraseña_nueva =request.form.get('contraseña_nueva')
        confirmacion=request.form.get('confirmacion')
        usuario = Usuario.query.get(id)
        if usuario is None:
         # Manejar el caso cuando el usuario no existe
            return "El usuario no existe"

  
        if not check_password_hash(usuario.contraseña, contraseña_anterior):
        # Manejar el caso cuando la contraseña actual no coincide
            flash("La contraseña actual no coincide", "error")
            return redirect(url_for('admin'))
    
        if contraseña_nueva != confirmacion:
            # Manejar el caso cuando la confirmación de contraseña no coincide
            flash("La contraseña nueva no coinciden.", "error")
            return redirect(url_for('admin'))
        
        hashed_password = generate_password_hash(contraseña_nueva)
        usuario.contraseña=hashed_password
        db.session.commit()
        flash("Se ha cambiado la contraseña correctamente", "success")
        return redirect(url_for('admin'))

    
    return redirect(url_for('admin'))

@app.route("/recuperar_contraseña",methods=["GET","POST"])
def recuperar_contraseña():
    if request.method == "POST":
        correos=request.form.get('correo')
        usuario=Usuario.query.filter_by(usuario=correos).first()
        print(usuario)
       
        if usuario is None:
         # Manejar el caso cuando el usuario no existe
             flash("Se ha enviando un codigo de verificacion al correo", "error")
             return redirect(url_for('recuperar_contraseña'))
        contraseña=generar_contraseña()
        cuerpo = '''
    Estimado(a) ,
    Aquí está tu código de seguridad para acceder al cambio de contraseña:   codigo de verficiacion: {0}
    Por favor, utiliza este código al realizar el cambio de contraseña en tu cuenta. Si tienes alguna pregunta o necesitas asistencia adicional, no dudes en contactarnos.
    ¡Gracias y ten un excelente día!

    Atentamente, Luxx ART
    '''.format(contraseña)
        msg = Message('Codigo de verificacion - Acceso a cuenta', sender='ingsoftwar123@gmail.com', recipients=[correos])
        msg.body = cuerpo
        mail.send(msg)
        hashed_password = generate_password_hash(contraseña)
        usuario.contraseña=hashed_password
        db.session.commit()
        flash("Se ha enviando un codigo de verificacion al correo", "success")
        return render_template("verficar_contraseña.html",correo=correos)


    
    return render_template("recuperar_contraseña.html")

@app.route("/nueva_contraseña", methods=["GET", "POST"])
def nueva_contraseña():
    
    if request.method == "POST":
        correos=request.form.get('correo')
        usuario = Usuario.query.filter_by(usuario=correos).first()
        contraseña_anterior = request.form.get('codigo_verficacion')
        contraseña_nueva = request.form.get('contraseña_nueva')
        confirmacion = request.form.get('confirmacion')
        print(contraseña_nueva)
        print(confirmacion)
        if usuario is None:
            # Manejar el caso cuando el usuario no existe
            flash("El código no coincide, revisa tu correo nuevamente", "error")
            return render_template("verficar_contraseña.html",correo=correos)

        if not check_password_hash(usuario.contraseña, contraseña_anterior):
            # Manejar el caso cuando la contraseña actual no coincide
            flash("El código no coincide, revisa tu correo nuevamente", "error")
            return render_template("verficar_contraseña.html",correo=correos)

        if contraseña_nueva != confirmacion:
            # Manejar el caso cuando la confirmación de contraseña no coincide
            flash("La contraseña nueva no coincide", "error")
            return render_template("verficar_contraseña.html",correo=correos)

        hashed_password = generate_password_hash(contraseña_nueva)
        usuario.contraseña = hashed_password
        db.session.commit()
        flash("Se ha cambiado la contraseña correctamente", "success")
        return redirect(url_for('login'))

    return render_template("verficar_contraseña.html")





@app.route("/login",methods=["GET","POST"])
def login():
 
    return render_template("login.html")



@app.route("/validar", methods=["GET", "POST"])
def validar():
    if request.method == "POST":
        usuario = request.form.get('usuario')
        contraseña = request.form.get('contraseña')

        # Obtener el usuario de la base de datos por nombre de usuario
        usuario_db = Usuario.query.filter_by(usuario=usuario).first()

        if usuario_db and check_password_hash(usuario_db.contraseña, contraseña):
            # Las contraseñas coinciden, el usuario es válido
            if usuario_db.id_grupo == 2 and usuario_db.estado ==1:
                
                cliente = Cliente.query.filter_by(id_persona=usuario_db.id_persona).first()
                persona = Persona.query.filter_by(id=usuario_db.id_persona).first()
                session['cliente_id'] = cliente.id
                session['cliente_foto'] = cliente.foto
                session['cliente_nombre'] = persona.nombre
                session['cliente_direccion'] = persona.direccion
                session['cliente_celular'] = persona.celular
                session['cliente_correo']=persona.correo
                session['cliente_usuario']=usuario_db.id
                client_ip = request.remote_addr
                user_agent = parse(request.headers.get('User-Agent'))
                browser = user_agent.browser.family
                version_browser=user_agent.browser.version
                os = user_agent.os.family
                os_version = user_agent.os.version_string
                dispositivo=user_agent.device.family
                version_dispositivo=user_agent.device.brand
                if version_dispositivo == None:
                    version_dispositivo="desconocido"
                
                nueva_conexion = Conexion(
                    id_usuario=usuario_db.id,  # Reemplaza con el ID del usuario correspondiente
                    ip=client_ip,
                    mac='',  # Puede ser difícil obtener la MAC desde el navegador
                    navegador=browser,
                    version_navegador=version_browser,
                    os=os,
                    version_os=os_version,
                    dispostivo=dispositivo,
                    version_dispositivos=version_dispositivo,
                    estado=1  # Estado por defecto
                )
                db.session.add(nueva_conexion)
                db.session.commit()
                session['id_conexion']=nueva_conexion.id

                return redirect(url_for('home'))            
            elif usuario_db.id_grupo == 1 and usuario_db.estado == 1 :
                
                 trabajador = Trabajador.query.filter_by(id_persona=usuario_db.id_persona).first()
                 persona = Persona.query.filter_by(id=usuario_db.id_persona).first()
                 session['user_id'] = trabajador.id
                 session['trabajador_foto'] = trabajador.foto
                 session['trabajador_nombre'] = persona.nombre
                 session['trabajador_direccion'] = persona.direccion
                 session['trabajador_celular'] = persona.celular
                 session['id_usuario']=usuario_db.id
                 client_ip = request.remote_addr
                 user_agent = parse(request.headers.get('User-Agent'))
                 browser = user_agent.browser.family
                 version_browser=user_agent.browser.version
                 os = user_agent.os.family
                 os_version = user_agent.os.version_string
                 dispositivo=user_agent.device.family
                 version_dispositivo=user_agent.device.brand
                 if version_dispositivo == None:
                    version_dispositivo="desconocido"
                 nueva_conexion = Conexion(
                    id_usuario=usuario_db.id,  # Reemplaza con el ID del usuario correspondiente
                    ip=client_ip,
                    mac='',  # Puede ser difícil obtener la MAC desde el navegador
                    navegador=browser,
                    version_navegador=version_browser,
                    os=os,
                    version_os=os_version,
                    dispostivo=dispositivo,
                    version_dispositivos=version_dispositivo,
                    estado=1  # Estado por defecto
                )
                 
                 db.session.add(nueva_conexion)
                 db.session.commit()
                 session['id_conexion']=nueva_conexion.id
                 flash("Bienvenido(a), "+ persona.nombre, "success")
                 return redirect(url_for('admin'))
            else:
                flash("Acceso denegado.", "error")
                return  redirect(url_for('login'))
        else:
            flash("Usuario y/o contraseña incorrectos. Acceso denegado.", "error")
           
            return redirect(url_for('login'))
    else:
        return render_template("login.html")


def obtener_productos():
    productos = Producto.query.all()
    lista_productos = []
    
    for producto in productos:
        precio = Precio.query.filter_by(id_producto=producto.id).first()
        precio_actual = precio.precio_actual if precio else None
        lista_productos.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'cantidad':producto.cantidad,
            'precio': precio_actual,
            'logo': producto.logo
        })
    
    return lista_productos

def obtener_cantidad_en_carrito(carrito, producto_id):
    for item in carrito:
        if item['id'] == producto_id:
            return item['cantidad']
    return 0


@app.route('/agregar', methods=['POST'])
def agregar():
    carrito = session.get('carrito', [])
    
    for key, value in request.form.items():
        if key.startswith('producto_id_'):
            producto_id = int(key.split('_')[2])  # Obtener el ID del producto del nombre de la clave
            cantidad_key = 'cantidad_' + str(producto_id)  # Construir la clave específica de cantidad
            cantidad = int(request.form.get(cantidad_key, 1))
            try:
                producto = Producto.query.get(producto_id)
                print("Producto:", producto)
            # Validar la cantidad disponible del producto
                producto = Producto.query.get(producto_id)
              
                cantidad_carrito = obtener_cantidad_en_carrito(carrito, producto_id)

                if producto and int(producto.cantidad) >= (int(cantidad) + cantidad_carrito):
                    for item in carrito:
                        if item['id'] == producto_id:
                            item['cantidad'] += cantidad
                            break
                    else:
                        producto = {'id': producto_id, 'cantidad': cantidad}
                        carrito.append(producto)
                        break  # Agrega el producto y sale del bucle principal
                else:
                    flash("Haz alcanzado el maximo de cantidad para este producto","info")
                    return redirect('/shop')
            except Exception as e:
                return jsonify({'message': 'Error al obtener el producto', 'error': str(e)}), 500
   
    print("Carrito actualizado:", carrito)
    session['carrito'] = carrito
    flash("Producto agregado al carrito", "success")
    return redirect('/shop')



# Ruta para mostrar el carrito
@app.route("/card", methods=["GET", "POST"])
@login_requirede
def card():
    carrito = session.get('carrito', [])
    productos = obtener_productos()

    carrito_actualizado = []
    total_carrito = 0  # Variable para almacenar el total del carrito

    for item in carrito:
        for producto in productos:
            if producto['id'] == item['id']:
                item_actualizado = {
                    'id': item['id'],
                    'nombre': producto['nombre'],
                    'precio': producto['precio'],
                    'logo': producto['logo'],
                    'cantidad': item['cantidad'] 
                }
                carrito_actualizado.append(item_actualizado)

                subtotal = item['cantidad'] * producto['precio']
                total_carrito += subtotal  # Sumar al total del carrito

                break

    # Guardar los detalles de la venta en la sesión
    session['detalles_venta'] = carrito_actualizado

    return render_template("card.html", carrito=carrito_actualizado, total_carrito=total_carrito)




# Ruta para eliminar productos del carrito
@app.route('/eliminar/<int:producto_id>')
def eliminar(producto_id):
    carrito = session.get('carrito', [])
    
    # Buscamos el producto en el carrito y lo eliminamos
    for item in carrito:
        if item['id'] == producto_id:
            carrito.remove(item)
            break
    
    # Actualizamos el carrito en la sesión
    session['carrito'] = carrito
    
    return redirect('/card')

@app.route('/registro')
def registro():
   
 
    return render_template("registro_usuario.html")




@app.route('/registrase', methods=["GET", "POST"])
def registrase():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        telefono = request.form.get("telefono")
        fecha_nacimiento = request.form.get("fecha")
        cedula = request.form.get("cedula")
        genero = request.form.get("genero")
        email = request.form.get("email")
        contraseña = request.form.get("contraseña")
        direccion = request.form.get("Direccion")
        secure_url = None
        if 'foto' in request.files:
            logo = request.files['foto']
            if logo:
                result = cloudinary.uploader.upload(logo ,transformation={"width": 300, "height": 300})
                secure_url = result["secure_url"]
        
        
        usuario_existente = Usuario.query.filter_by(usuario=email).first()
        if usuario_existente:
            flash("El email ya está registrado", "error")
            return redirect('/registrase')

        persona = Persona(nombre=nombre, correo=email, direccion=direccion, celular=telefono)
        persona_natural = PersonaNatural(id_persona=persona.id, apellido=apellido, cedula=cedula, fecha_nacimiento=fecha_nacimiento, genero=genero)
        persona.persona_natural = persona_natural
        db.session.add(persona)
        db.session.commit()
        hashed_password = generate_password_hash(contraseña)
        usuario = Usuario(id_grupo=2, id_persona=persona.id, usuario=email, contraseña=hashed_password, estado=1)
        persona.usuario = usuario
        cliente = Cliente(id_persona=persona.id, tipo_cliente="Normal", foto=secure_url, estado=1)
        persona.cliente = cliente
        db.session.add(usuario)
        db.session.add(cliente)
        db.session.commit()
        return redirect('/login')

    return render_template('registro_usuario.html')



@app.route('/guardar_venta', methods=['POST'])
def guardar_venta():
    if request.method == "POST":
        id_tipo = request.form.get('id_tipo')
        id_cliente = session['cliente_id']
        fecha = request.form.get('fecha')
        estado = request.form.get('estado')
        fecha_actual = datetime.now()
        fecha_postgresql = fecha_actual.strftime('%Y-%m-%d')
        ultima_venta = Venta.query.order_by(Venta.id.desc()).first()
        
        if ultima_venta:
            id_venta=ultima_venta.id +1
        else:
            id_venta = 1

        codigo = "V-00" + str(id_venta) 
        tipo_entrega=request.form.get('flexRadioDefault')
        direccion=request.form.get('direccion')
        print(direccion)
        print("-----------------------------","codigo de venta", codigo)
        print("fecha:",fecha_postgresql,"------------", "Tipo de venta:",id_tipo)
        print("------------------------------")
        print("Cliente:", id_cliente)
        print("------------------------------------------------------")
        print("------Tipo de entrega---------------")
        print("Lugar de entrega:",tipo_entrega)
        print("----------------------------------")
        lugar=tipo_entrega+" "+ direccion
        venta = Venta(id_tipo=1, id_cliente=id_cliente, fecha=fecha_postgresql,codigo=codigo,tipo_entrega=lugar, estado=1,fecha_entrega=fecha)
        db.session.add(venta)
        db.session.commit()   
        
    
        detalles = session.get('detalles_venta', [])
        for detalle in detalles:
            id_producto = detalle['id']
            subtotal = detalle['precio'] * detalle['cantidad']
            descuento = 0
            total = subtotal - descuento
            detalle_venta = DetalleVenta(id_venta=venta.id, id_producto=id_producto, subtotal=subtotal, descuento=descuento, total=total)
            db.session.add(detalle_venta)
        
        db.session.commit()
        for detalle in detalles:
            producto = Producto.query.get(detalle['id'])
            producto.cantidad -= detalle['cantidad']
            db.session.add(producto)

        db.session.commit()
        # Eliminar el carrito de la sesión
        session.pop('carrito', None)
        flash("Pedido ordenado existosamente", "success")
        return redirect('/shop')

    return redirect('/shop')
    

@app.route('/admin',methods=["GET"])
@login_required
def admin():
    # Obtener la fecha y hora actual
    now = datetime.now()

    # Obtener la hora actual
    hora_actual = now.hour
    minutos_actuales = now.minute

    # Determinar si es de mañana, tarde o noche
    if hora_actual >= 6 and hora_actual < 12:
        momento = "dias"
    elif hora_actual >= 12 and hora_actual < 18:
        momento = "tardes"
    else:
        momento = "noches"

    # Obtener la fecha actual
    fecha_actual = now.strftime("%d/%m/%Y")

    return render_template("inicio_admin.html", hora_actual=hora_actual,minutos_actuales=minutos_actuales,momento=momento,fecha_actual=fecha_actual)


@app.route('/servicios', methods=['POST','GET'])
@login_required
def servicios():
    servicios= Servicio.query.all()
    return render_template("servicios.html",servicios=servicios)

@app.route('/crear_servicios', methods=['POST','GET'])
def crear_servicios():
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    logo = None
    if 'foto' in request.files:
        logo = request.files['foto']
        if logo:
           result = cloudinary.uploader.upload(logo ,transformation={"width": 300, "height": 300})
           secure_url = result["secure_url"]
    estado = request.form.get('estado')

    servicio = Servicio(nombre=nombre, descripcion=descripcion, foto=secure_url, estado=estado)
    db.session.add(servicio)
    db.session.commit()
    flash("Se ha creado correctamente el servicios","success")
    return redirect('servicios')

@app.route('/actualizar_servicios/<int:servicio_id>', methods=['POST','GET'])
def actualizar_servicio(servicio_id):
    servicio = Servicio.query.get(servicio_id)

    if servicio:
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        estado = request.form.get('estado')
        logo=servicio.foto
        print(logo)
        if 'foto' in request.files:
            nueva_logo = request.files['foto']
            if nueva_logo:
                # Eliminar la imagen anterior si existe
                try:
                        if logo:
                                # Obtén el public_id de Cloudinary desde la URL de la imagen anterior
                            public_id_anterior = logo.split('/')[-1].split('.')[0]
                                # Intenta eliminar la imagen anterior de Cloudinary
                            try:
                                    cloudinary.api.delete_resources_by_prefix(public_id_anterior)
                            except cloudinary.exceptions.Error as delete_error:
                                print(f"Error al eliminar la imagen anterior: {delete_error}")

                            # Subir y transformar la nueva imagen
                        result = cloudinary.uploader.upload(nueva_logo,transformation={"width": 300, "height": 300})
                        secure_url = result["secure_url"]
                except cloudinary.exceptions.Error as upload_error:
                    flash("Error al actualizar la imagen: {}".format(str(upload_error)), "error")
                    return redirect('/servicios')  

        servicio.nombre = nombre
        servicio.descripcion = descripcion
        servicio.estado = estado
        servicio.foto=secure_url
        db.session.commit()
        flash("Se ha actualizado correctamente el servicios","success")
        return redirect('/servicios')
    else:
        return jsonify({'error': 'No se encontró el servicio'})


@app.route('/eliminar_servicio/<int:servicio_id>', methods=['POST','GET'])
def eliminar_servicio(servicio_id):
    servicio = Servicio.query.get(servicio_id)

    if servicio:
        servicio.estado = 2
        db.session.commit()
        flash("se ha desactivado el servicio","success")
        return redirect("/servicios")
    else:
        return jsonify({'error': 'No se encontró el servicio'})


@app.route("/precio_servicios",methods=["POST","GET"])
@login_required
def precio_servicios():
   Precios=PrecioServicio.query.options(joinedload(PrecioServicio.servicio)).all()
   servicio=Servicio.query.all()
   return render_template("precio_servicios.html",Precios=Precios,servicio=servicio)

@app.route("/crear_precio_servicio",methods=["GET","POST"])
@login_required
def crear_precio_servicio():
    if request.method == "POST":
        id_producto=request.form.get('producto')
        precio_actual = request.form.get('precio_actual')
        estado=request.form.get('estado')
        precio = PrecioServicio(id_servicios=id_producto, precio_actual=precio_actual, precio_anterior=0, estado=estado)
        db.session.add(precio)
        db.session.commit()
        flash("Se ha asignado correctamen el precio al servicios","success")
        return redirect(url_for('precio_servicios'))
    else:
        return redirect(url_for('precio_servicios'))
    


@app.route("/actualizar_precio_servicio/<int:id>",methods=["GET","POST"])
@login_required
def actualizar_precio_servicio(id):
    precio = PrecioServicio.query.get(id)
    if request.method == "POST":
        
        precio_actual = request.form.get('precio_actual')
        precio_anterior=request.form.get('precio_anterior')
        estado=request.form.get('estado')
        if precio_actual and precio_actual.strip():  
            precio.precio_actual=precio_actual
            precio.precio_anterior=precio_anterior
            precio.estado=estado
            db.session.commit()
            flash("Se ha actualizado el precio correctamente","success")
            return redirect(url_for('precio_servicios'))
        else:
            precio.estado=estado
            db.session.commit()
            return redirect(url_for('precio_servicios'))
        
    else:
        return redirect(url_for('/precio_servicios'))

@app.route("/eliminar_precio_servicio", methods=["POST"])
@login_required
def eliminar_precio_servicio():
    id = request.form.get("id")
    
    productos = PrecioServicio.query.get(id)
    
    if productos:
        # Cambiar el estado de la categoría a inactivo (estado = 2)
        productos.estado = 2
        db.session.commit()
    flash("Se ha desactivado el precio correctamente")
    return redirect(url_for('precio_servicios'))

#Clientes
@app.route("/clientes",methods=["POST","GET"])
@login_required
def cliente():
    clientes=Cliente.query.options(joinedload(Cliente.persona)).all()
    return render_template("cliente.html",clientes=clientes)


@app.route('/crear_cliente', methods=["GET", "POST"])
@login_required
def crear_cliente():
    if request.method == "POST":
        # Obtener los datos del formulario
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        telefono = request.form.get("celular")
        fecha_nacimiento = request.form.get("fecha")
        cedula = request.form.get("cedula")
        genero = request.form.get("genero")
        email = request.form.get("email")
        tipo=request.form.get("tipo")
        direccion = request.form.get("direccion")
        logo = None
        if 'foto' in request.files:
            logo = request.files['foto']
            if logo:
                result = cloudinary.uploader.upload(logo ,transformation={"width": 300, "height": 300})
                secure_url = result["secure_url"]
        
        
     

        # Crear una instancia de Persona y PersonaNatural
        persona = Persona(nombre=nombre, correo=email, direccion=direccion, celular=telefono)
        persona_natural = PersonaNatural(id_persona=persona.id, apellido=apellido, cedula=cedula, fecha_nacimiento=fecha_nacimiento, genero=genero)

        # Asociar Persona y PersonaNatural
        persona.persona_natural = persona_natural

        # Realizar las acciones necesarias para guardar los modelos en la base de datos
        db.session.add(persona)
        db.session.commit()

      
        # Crear una instancia de Cliente y asociarla a Persona
        cliente = Cliente(id_persona=persona.id, tipo_cliente=tipo, foto=secure_url, estado=1)
        persona.cliente = cliente

        # Agregar los objetos a la sesión de la base de datos y confirmar los cambios
       
        db.session.add(cliente)
        db.session.commit()

        # Redirigir al usuario a la página de inicio de sesión después del registro exitoso
        flash("Se ha agregado correctamente el nuevo cliente","success")
        return redirect('/clientes')

    return render_template('cliente.html')


@app.route('/actualizar_cliente/<int:id>', methods=["GET", "POST"])
@login_required
def actualizar_cliente(id):
   
    cliente = Cliente.query.get(id)
    print(cliente)
    if request.method == "POST":
        # Obtener los datos del formulario
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        telefono = request.form.get("celular")
        fecha_nacimiento = request.form.get("fecha_nacimiento")
        cedula = request.form.get("cedula")
        genero = request.form.get("genero")
        email = request.form.get("correo")
        tipo = request.form.get("tipo")
        direccion = request.form.get("direccion")
        estado=request.form.get("estado")
        logo = cliente.foto
        if 'foto' in request.files:
            archivo_foto = request.files['foto']
            if archivo_foto:
                try:
                    if logo:
                                # Obtén el public_id de Cloudinary desde la URL de la imagen anterior
                        public_id_anterior = logo.split('/')[-1].split('.')[0]
                                # Intenta eliminar la imagen anterior de Cloudinary
                        try:
                                cloudinary.api.delete_resources_by_prefix(public_id_anterior)
                        except cloudinary.exceptions.Error as delete_error:
                                print(f"Error al eliminar la imagen anterior: {delete_error}")

                            # Subir y transformar la nueva imagen
                        result = cloudinary.uploader.upload(archivo_foto,transformation={"width": 300, "height": 300})
                        secure_url = result["secure_url"]
                except cloudinary.exceptions.Error as upload_error:
                    flash("Error al actualizar la imagen: {}".format(str(upload_error)), "error")
                    return redirect('/servicios')  

                    
       
        # Actualizar los datos del cliente existente
        cliente.persona.nombre = nombre
        cliente.persona.correo = email
        cliente.persona.direccion = direccion
        cliente.persona.celular = telefono
        cliente.persona.persona_natural.apellido = apellido
        cliente.persona.persona_natural.cedula = cedula
        cliente.persona.persona_natural.fecha_nacimiento = fecha_nacimiento
        cliente.persona.persona_natural.genero = genero
        cliente.tipo_cliente = tipo
        cliente.foto = secure_url
        cliente.estado=estado
        db.session.add(cliente)
        db.session.commit()
        if int(estado) == 1:
            usuario=Usuario.query.filter_by(id_persona=cliente.id_persona).first()
            if usuario:
            # Cambiar el estado de la categoría a inactivo (estado = 2)
                usuario.estado = 1
                db.session.commit()
        flash("Se ha actualizado correctamente el cliente","success")
        return redirect('/clientes')

    return redirect('/clientes')


@app.route("/eliminar_cliente",methods=["GET","POST"])
def eliminar_cliente():
    if request.method == "POST":
        id=request.form.get('id')
        trabajador=Cliente.query.get(id)
        if trabajador:
        # Cambiar el estado de la categoría a inactivo (estado = 2)
            trabajador.estado = 2
            db.session.commit()
        

        usuario=Usuario.query.filter_by(id_persona=trabajador.id_persona).first()
        if usuario:
        # Cambiar el estado de la categoría a inactivo (estado = 2)
            usuario.estado = 2
            db.session.commit()
        flash("Se ha desactivado correctamente el cliente","success")
        return redirect('/clientes')
    
    
    
    return redirect('/clientes')

@app.route('/personalizacion', methods=['POST'])
def personalizacion():
    if request.method == "POST":
        cliente_id = request.form.get('cliente_id')
        descripcion = request.form.get('descripcion')
        presupuesto = request.form.get('presupuesto')
        foto = request.files['foto']

     
        logo = None
        if 'foto' in request.files: 
            logo = request.files['foto']
            result = cloudinary.uploader.upload(logo ,transformation={"width": 300, "height": 300})
            secure_url = result["secure_url"]

        personalizacion=Personalizacion(id_cliente=cliente_id,descripcion=descripcion,fotos=secure_url,presupuesto=presupuesto,estado=0)
        db.session.add(personalizacion)
        db.session.commit()
        return jsonify({
            'descripcion': descripcion,
            'presupuesto': presupuesto,
            'cliente_id': cliente_id,
            # Agrega aquí los demás campos que desees devolver
        })
    
    return redirect('/shop')
    



@app.route('/personalizaciones', methods=['POST','GET'])
@login_required
def personalizaciones():
    cantidad_pedidos = Personalizacion.query.filter(Personalizacion.estado == 0).count()
    pedido=Personalizacion.query.filter(Personalizacion.estado == 0).order_by(Personalizacion.id).all()
    rechazados=Personalizacion.query.filter(Personalizacion.estado == 1).all()
    enviados=DetallePersonalizacion.query.join(DetallePersonalizacion.personalizacion).filter(Personalizacion.estado == 2).all()
    detalle_pedidos = DetallePersonalizacion.query.join(DetallePersonalizacion.personalizacion).filter(Personalizacion.estado == 3).all()
    fecha_actual = datetime.now().date()
    return render_template("personalizacion.html",pedido=pedido, cantidad_pedidos=cantidad_pedidos,rechazados=rechazados,detalle_pedidos=detalle_pedidos,enviados=enviados,fecha_actual=fecha_actual)



@app.route('/modulos')
def obtener_modulos_con_submodulos():
    resultados = db.session.query(Modulo.id.label('modulo_id'), Modulo.nombre.label('modulo_nombre'),
                                 SubModulo.id.label('submodulo_id'), SubModulo.nombre.label('submodulo_nombre')) \
        .outerjoin(SubModulo, Modulo.id == SubModulo.id_modulo) \
        .all()

    resultado_final = []
    modulo_actual = None
    submodulos_actual = []

    for resultado in resultados:
        if resultado.modulo_id != modulo_actual:
            if modulo_actual is not None:
                resultado_final.append({'modulo': modulo_actual, 'submodulos': submodulos_actual})
            modulo_actual = resultado.modulo_id
            submodulos_actual = []
        
        submodulos_actual.append({'nombre': resultado.submodulo_nombre, 'id': resultado.submodulo_id})

    if modulo_actual is not None:
        resultado_final.append({'modulo': modulo_actual, 'submodulos': submodulos_actual})

    return render_template("modulos.html")


@app.route("/detalle_pedidos",methods=["GET","POST"])
def detalle_pedidos():
    if request.method == "POST":
        id=request.form.get('id')
        personalizacion=Personalizacion.query.get(id)
        nombre=personalizacion.cliente.persona.nombre
        correo=personalizacion.cliente.persona.correo
        numero=personalizacion.cliente.persona.celular
        estado=request.form.get("estado")
        
        costo_total=request.form.get("costo_total")
        nota=request.form.get("nota")
        fecha_entrega=request.form.get("fecha_entrega")
        if int(estado) == 1:
          
            personalizacion.estado=1
            db.session.add(personalizacion)
            db.session.commit()
            cuerpo = '''
            Estimado(a) {0},

            Lamentamos informarte que no podemos aceptar tu pedido en este momento. No contamos con los elementos o servicios que has solicitado. Nos disculpamos por cualquier inconveniente que esto pueda haber causado.
            Entendemos que este contratiempo puede ser frustrante, y nos gustaría asegurarte que tomamos en cuenta todas las solicitudes de nuestros clientes de manera cuidadosa. Sin embargo, en esta ocasión no podemos cumplir con tu pedido debido a limitaciones de inventario o capacidad.
            Apreciamos tu interés en nuestros productos/servicios y nos encantaría poder ayudarte en el futuro. Si tienes alguna otra consulta o necesitas asistencia adicional, no dudes en contactarnos. Estaremos encantados de brindarte cualquier información que necesites.
            Nuevamente, lamentamos los inconvenientes causados y agradecemos tu comprensión.
            Atentamente, Luxx ART '''.format(nombre)
            msg = Message('Resultado de solicitud de pedido', sender='ingsoftwar123@gmail.com', recipients=[correo])
            msg.body = cuerpo
            mail.send(msg)
            flash("Se ha rechazado el pedido personalizado con exito","success")

            return redirect('/personalizaciones')
        else :
            personalizacion.estado=2
            db.session.add(personalizacion)
            db.session.commit()
            detalle=DetallePersonalizacion(id_personalizacion=id, costo_total=costo_total, nota=nota, fecha_entrega=fecha_entrega,tipo_entrega='')
            db.session.add(detalle)
            db.session.commit()
            mensaje=f'''Estimado(a) {nombre},

            Nos complace informarte que tu pedido ha sido aceptado. A continuación, te proporcionamos los detalles de tu pedido:
            -Acerca de tu pedido:{nota}.
            -Total del va lor del pedido: {costo_total} Esto no incluye costo de envio.
            -Fecha de entrega: {fecha_entrega}.
            Para confirmar tu pedido y acceder a la confirmación, sigue estos pasos:

            1) Inicia sesión en tu cuenta en nuestro sitio web.
            2) Entra al apartado de productos y te va aparecer  el boton de confirmar
            Recuerda que debes iniciar sesión en tu cuenta antes de hacer clic en el enlace.

            Si tienes alguna pregunta o necesitas ayuda adicional, no dudes en contactarnos. ¡Estamos aquí para asistirte!

            ¡Gracias y que tengas un excelente día!

            Atentamente,
            Luxx Art'''
            flash("Se ha enviados los detalles del pedido al cliente","success")
            msg = Message('Resultado de solicitud de pedido', sender='ingsoftwar123@gmail.com', recipients=[correo])
            msg.body = mensaje
            mail.send(msg)
            
            return redirect('/personalizaciones')
                            
    return redirect("/personalizaciones")


@app.route("/confirmar/<int:id>", methods=["POST","GET"])
@login_requirede
def confirmar(id):
    if request.method == "GET":
        confirmar = DetallePersonalizacion.query.join(DetallePersonalizacion.personalizacion).filter(Personalizacion.estado == 2, Personalizacion.id == id).first()

        return render_template("confirmar.html", confirmar=confirmar)
    if request.method == "POST":
        id_personalizacion = request.form.get('id')
        tipo_entrega=request.form.get('tipo_entrega')
        estado = int(request.form.get('estado'))
        personalizacion = Personalizacion.query.get(id_personalizacion)
        detalle=DetallePersonalizacion.query.get(id_personalizacion)
        if personalizacion is not None:
            # Realiza las acciones necesarias con la personalización
            # según si se acepta o se rechaza
            if  estado == 3:
                # Acciones cuando se acepta
                personalizacion.estado = 3
                db.session.add(personalizacion)
                detalle.tipo_entrega=tipo_entrega
                db.session.add(detalle)
                db.session.commit()
                flash('La confirmación se ha realizado correctamente.', 'success')
                return redirect('/shop')
            elif estado == 4:
                # Acciones cuando se rechaza
                personalizacion.estado = 4
                db.session.add(personalizacion)
                db.session.commit()
                flash('Se ha rechazado correctamente el pedido.', 'success')
                return redirect('/shop')

       
           
        else:
            flash('No se encontró la personalización solicitada.', 'error')
            return redirect('/shop')

    return redirect('/shop')

@app.route("/terminar_pedido",methods=["GET","POST"])
def terminar_pedidos():
    if request.method == "POST":
        id=request.form.get('id')
        personalizaciones=DetallePersonalizacion.query.get(id)
        
        estado=request.form.get("estado") 
        personalizaciones.personalizacion.estado=estado
        db.session.add(personalizaciones)
        db.session.commit()
        flash("Se ha confirmado la culminicacion del pedido","success")
        return redirect('/personalizaciones')
                            
    return redirect("/personalizaciones")




@app.route('/ventas', methods=['GET'])
@login_required
def ventas():
    # Obtener todos los registros de los modelos
    ventas = Venta.query \
    .options(joinedload(Venta.tipo_venta), joinedload(Venta.cliente).joinedload(Cliente.persona)) \
    .filter(Venta.estado != 1) \
    .all()

    # Obtener todas las ventas con detalles de productos
    ventas_productos = DetalleVenta.query.options(joinedload(DetalleVenta.venta)).all()
    ventass = DetalleVenta.query.join(DetalleVenta.venta).filter(Venta.estado == 1).options(joinedload(DetalleVenta.venta)).all()

    # Obtener todas las ventas con detalles de personalizaciones
    ventas_personalizaciones = VentaPersonalizacion.query.options(joinedload(VentaPersonalizacion.venta)).all()

    confirmar = DetallePersonalizacion.query.join(DetallePersonalizacion.personalizacion).filter(Personalizacion.estado == 5).all()
    ventas_productos = (
        db.session.query(Venta, func.string_agg(DetalleVenta.id.cast(db.String), ',').label('detalle_ids'))
        .join(DetalleVenta.venta)
        .filter(Venta.estado == 1)
        .group_by(Venta)
        .all()
    )
    ventas_con_productos = []
    for venta, detalle_ids in ventas_productos:
        detalle_ids = [int(id) for id in detalle_ids.split(",")]
        detalles_venta = DetalleVenta.query.filter(DetalleVenta.id.in_(detalle_ids)).all()
        subtotal_venta = 0

        for detalle in detalles_venta:
            subtotal_venta += detalle.subtotal

        ventas_con_productos.append({
            'venta': venta,
            'detalles_venta': detalles_venta,
            'subtotal_venta': subtotal_venta
        })
    return render_template('venta.html', ventas=ventas,ventas_personalizaciones=ventas_personalizaciones, ventas_productos=ventas_productos,confirmar=confirmar,ventas_con_productos=ventas_con_productos)


@app.route('/crear_venta_pedido', methods=['GET','POST'])
@login_required
def crear_venta_pedido():
    if request.method == "POST":
        id=request.form.get('id')
        id_cliente= request.form.get('id_cliente')
        costo_total=request.form.get('costo_total')
        descuento=request.form.get('descuento')
        if descuento == '':
            descuento=0
        ultima_venta = Venta.query.order_by(Venta.id.desc()).first()
        fecha_actual = date.today()
        total  = int(costo_total) - int(descuento)
        pedido=Personalizacion.query.get(id)
        pedido.estado=6
        db.session.add(pedido)
        db.session.commit()
        # Formatear la fecha actual en el formato para PostgreSQL
        fecha = fecha_actual.strftime('%Y-%m-%d')
        if ultima_venta:
            id_venta=ultima_venta.id +1
        else:
            id_venta = 1

        codigo = "V-00" + str(id_venta) 
        venta= Venta(id_cliente=id_cliente,id_tipo=2,fecha=fecha,codigo=codigo,tipo_entrega="metro",estado=2)
        db.session.add(venta)
        db.session.commit()
        ultimo_id = venta.id

        detalle_venta=VentaPersonalizacion(id_venta=ultimo_id,id_personalizacion=id,subtotal=costo_total,descuento=descuento,total=total)
        db.session.add(detalle_venta)
        db.session.commit()
        flash("Se ha realizado la venta","success")
        return redirect('/ventas')
    
    return redirect('ventas')

def calcular_total_con_descuento(subtotal, descuento):
    subtotal = Decimal(subtotal)
    descuento = Decimal(descuento)
    total = subtotal - descuento
    return total

@app.route('/crear_venta_pedidos', methods=['GET','POST'])
@login_required
def crear_venta_pedidos():
    if request.method == "POST":
        id=request.form.get('id')
        descuento=request.form.get('descuento')
        fecha_entrega_str=request.form.get('fecha_entrega')
        fecha_entrega = datetime.strptime(fecha_entrega_str, '%Y-%m-%d').date()
        venta=Venta.query.get(id)
        venta.estado=2
        venta.fecha_entrega=fecha_entrega
        db.session.add(venta)
        db.session.commit()
        if descuento is None or not descuento.strip():
            descuento = Decimal('0.00')
        else:
            try:
                descuento = Decimal(descuento)
            except InvalidOperation:
                return "No se puede convertir"
       
        detalles_venta = DetalleVenta.query.filter_by(id_venta=id).all()
        for detalle in detalles_venta:
            detalle.descuento = descuento
            detalle.total = calcular_total_con_descuento(detalle.subtotal, descuento)  # Aquí debes implementar tu lógica para calcular el total con descuento
            db.session.add(detalle)

        db.session.commit()

      


        flash("Se ha realizado la venta","success")
        return redirect('/ventas')
    
    return redirect('ventas')


@app.route('/completar', methods=['GET','POST'])
@login_required
def completar():
    if request.method == "POST":
        id=request.form.get('id')
       
        venta=Venta.query.get(id)
        venta.estado=3
        db.session.add(venta)
        db.session.commit()
        flash("Se ha realizado la venta","success")
        return redirect('/ventas')
    
    return redirect('ventas')

@app.route('/anular', methods=['GET','POST'])
@login_required
def anular():
    if request.method == "POST":
        id=request.form.get('id')
       
        venta=Venta.query.get(id)
        venta.estado=4
        db.session.add(venta)
        db.session.commit()
        flash("Se ha realizado la venta","success")
        return redirect('/ventas')
    
    return redirect('ventas')


@app.route('/enviar_correo',methods=['GET','POST'])
def enviar_correo():
    nombre=request.form.get('nombre')
    correo=request.form.get('correo')
    mensaje=request.form.get('mensaje')
     # Crear el mensaje de correo
    subject = "Formulario de Contacto"
    message_body = f"Nombre: {nombre}\nCorreo: {correo}\nMensaje: {mensaje}"

    msg = Message(subject, sender=(correo, nombre), recipients=['ingsoftwar123@gmail.com'])
    msg.body = message_body
    print(msg)
   
        # Enviar el correo
    try:
        mail.send(msg)
        flash("Se ha enviado el correo","success")
        return redirect('/contacto')
    except Exception as e:
        print( "Error al enviar el correo: " + str(e))
        flash("No se pudo enviar el correo","error")
        return redirect('/contacto')
    
