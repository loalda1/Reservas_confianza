# Tu web de reservas de confianza 📅🌐

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2.10-092E20?logo=django&logoColor=white)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-Fetch_API-F7DF1E?logo=javascript&logoColor=black)
![Interface](https://img.shields.io/badge/UI-English-blue)

**Clientes, fechas y reservas en una aplicación web con Django.**

Reservas_confianza es un sistema de gestión de reservas desarrollado como proyecto de **Progettazione e Sviluppo Web**. Permite registrar reservas por cliente, consultar su estado y gestionarlas mediante una interfaz web y el panel administrativo de Django.

Combina modelos relacionales, formularios, autenticación, permisos y vistas renderizadas en el servidor. La interfaz está en inglés; los nombres internos de modelos, campos y rutas conservan el español.

## ✨ Características

- 📝 **Registro público** — Cuenta y perfil de cliente vinculados, contraseñas validadas por Django y permisos de consulta y creación.

- 📅 **Gestión de reservas** — Creación, consulta, edición y eliminación con permisos de Django.
- 👥 **Gestión de clientes** — Nombre, correo único, teléfono y vinculación opcional con una cuenta de usuario.
- 🔍 **Búsqueda** — Filtrado de reservas por nombre o correo del cliente.
- 📄 **Paginación** — Listado organizado en páginas de cinco reservas.
- ✅ **Validación de fechas** — Impide fechas de inicio pasadas y fechas de fin anteriores al inicio en las vistas de creación y edición.
- 🛑 **Detección de solapamientos** — Comprueba si un cliente ya tiene una reserva que coincide con el intervalo solicitado.
- 🚦 **Estados de reserva** — Pending, Confirmed, Cancelled y Completed; confirmación y cancelación mediante acciones específicas.
- 👤 **Área personal** — Consulta de las reservas asociadas al perfil del usuario.
- 🔐 **Autenticación y permisos** — Inicio y cierre de sesión, grupos y permisos para las operaciones.
- ⚙️ **Administración integrada** — Panel Django Admin con búsqueda y filtros.
- 💬 **Mensajes de resultado** — Avisos de éxito y errores de validación.
- 🧠 **Sesiones** — Registro de la última búsqueda y del número de visitas al listado.
- ⚡ **Código AJAX incluido** — Endpoints JSON y JavaScript con Fetch API para actualizar estados; actualización del estado en el listado sin recargar la página.

## 🏗️ Estructura del proyecto

El ZIP contiene la aplicación dentro de `Reservas_confianza/`. Las rutas de esta documentación parten de la carpeta que contiene `manage.py`.

| Ruta | Descripción |
| --- | --- |
| `manage.py` | Comandos de administración y servidor de desarrollo. |
| `webapp/settings.py` | Configuración, SQLite, sesiones e idioma. |
| `webapp/urls.py` | Rutas globales, administración y autenticación. |
| `webapp/asgi.py` y `webapp/wsgi.py` | Puntos de entrada del servidor. |
| `main/models.py` | Modelos `Cliente` y `Reserva`. |
| `main/forms.py` | Formulario `ReservaForm`. |
| `main/views.py` | CRUD, búsquedas, validaciones y cambios de estado. |
| `main/urls.py` | Rutas de la aplicación. |
| `main/admin.py` | Registro y configuración del panel administrativo. |
| `main/migrations/` | Historial de cambios del esquema y traducción de etiquetas. |
| `main/templates/` | Plantillas de inicio, reservas y login. |
| `main/static/css/styles.css` | Estilos de la interfaz. |
| `main/static/js/reservas.js` | JavaScript de actualización de estados. |
| `main/tests.py` | 30 pruebas automatizadas de acceso, formularios y reglas de negocio. |
| `requirements.txt` | Dependencia de Django para la instalación. |
| `.gitignore` | Exclusión de entornos, datos locales y credenciales. |

## 🚀 Inicio rápido

### Requisitos

- Python **3.11 o superior** para reproducir el entorno incluido con Django 5.2.10.
- pip y un entorno virtual propio.
- Un navegador web.

El proyecto incluye `requirements.txt` con Django 5.2.10. El entorno virtual se crea localmente.

### Instalación

1. **Descarga o clona el repositorio** y abre la carpeta que contiene `manage.py`.

   Si trabajas directamente con el ZIP original:

   ```bash
   cd Reservas_confianza
   ```

2. **Crea un entorno virtual nuevo.**

   ```bash
   python -m venv .venv
   ```

   En Linux o macOS:

   ```bash
   source .venv/bin/activate
   ```

   En Windows PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   Utiliza tu propio entorno; la entrega no incluye un entorno virtual.

3. **Instala Django.**

   ```bash
   python -m pip install -r requirements.txt
   ```

4. **Aplica las migraciones.**

   ```bash
   python manage.py migrate
   ```

   La entrega no incluye base de datos ni usuarios. Este comando crea una base de datos nueva.

5. **Crea tu administrador.**

   ```bash
   python manage.py createsuperuser
   ```

6. **Inicia el servidor.**

   ```bash
   python manage.py runserver
   ```

   Abre [http://127.0.0.1:8000/](http://127.0.0.1:8000/) y entra en [Django Admin](http://127.0.0.1:8000/admin/) con la cuenta creada.

### Registro de clientes

Los visitantes pueden crear su cuenta desde **Create account** en el inicio, la navegación o el login. El formulario pide usuario, nombre completo, correo, teléfono opcional y contraseña con confirmación. Después del registro se redirige al login.

La cuenta se vincula automáticamente con un `Cliente` y recibe el grupo `customers` y permisos `view_reserva` y `add_reserva`. No recibe privilegios de administración. El registro rechaza correos ya asociados a usuarios o clientes; los clientes existentes deben vincularse desde Admin, sin apropiarse de perfiles por correo. No hay verificación de correo ni recuperación de contraseña en esta versión.

### Configuración de usuarios

Desde Django Admin puedes crear usuarios, clientes y grupos, y asignar los permisos correspondientes.

| Perfil de uso | Configuración |
| --- | --- |
| **Administrador** | Superusuario para administrar usuarios, clientes, reservas y permisos. |
| **Empleado** | Usuario con los permisos `view_reserva`, `add_reserva`, `change_reserva` y, si procede, `delete_reserva`. |
| **Cliente** | Usuario del grupo `customers`, vinculado al campo `usuario` de un `Cliente`, con `view_reserva` y, si puede reservar, `add_reserva`. |

La detección del perfil cliente admite los grupos `customer`, `customers`, `cliente` y `clientes`, sin distinguir mayúsculas. Los nombres de grupo de empleados o administradores no conceden permisos automáticamente.

En una base de datos nueva debes crear los grupos manualmente: la migración de traducción renombra grupos existentes, pero no los crea.

En ambas rutas de creación, los usuarios cliente quedan vinculados a su propio perfil. En el formulario genérico el campo cliente está deshabilitado para ellos, y el servidor ignora cualquier ID ajeno enviado. La edición y eliminación se limitan a reservas propias y requieren el permiso correspondiente. El panel de gestión y los cambios de estado están reservados a usuarios que no pertenecen al grupo cliente y tienen los permisos necesarios.

## 📖 Cómo funciona

### Modelo de datos

- **`Cliente`** almacena nombre, correo único, teléfono y una relación opcional de uno a uno con el usuario de Django.
- **`Reserva`** pertenece a un cliente y almacena fecha de inicio, fecha de fin, estado y fecha de creación.
- Un cliente puede tener varias reservas.
- Una reserva nueva comienza en estado **Pending**.

### Flujo de reserva

1. Un usuario autorizado introduce el cliente y las fechas; la ruta personal obtiene el cliente del usuario conectado.
2. El formulario utiliza la validación central del modelo para fechas y solapamientos; Django Admin utiliza las mismas reglas.
3. Si la entrada es válida, guarda la reserva y muestra un mensaje de éxito.
4. Un usuario con permiso de modificación puede confirmar o cancelar la reserva.
5. El cliente puede consultar sus reservas en el área personal.

Los extremos de los intervalos cuentan como solapamiento. Solo las reservas Pending y Confirmed bloquean intervalos. Cancelled y Completed no bloquean nuevas reservas. Confirmar una reserva cancelada vuelve a comprobar los solapamientos.

### Estados

| Valor interno | Etiqueta de la interfaz | Gestión |
| --- | --- | --- |
| `pendiente` | Pending | Estado inicial. |
| `confirmada` | Confirmed | Acción de confirmación. |
| `cancelada` | Cancelled | Acción de cancelación. |
| `finalizada` | Completed | Disponible en el modelo y en Django Admin. |

## 📂 Rutas principales

| Ruta | Función |
| --- | --- |
| `/` | Página de inicio y accesos según permisos. |
| `/accounts/register/` | Registro público de clientes. |
| `/accounts/login/` | Inicio de sesión. |
| `/accounts/logout/` | Cierre de sesión mediante POST. |
| `/reservas/` | Listado, búsqueda y paginación. |
| `/reservas/crear/` | Creación mediante `ReservaForm`. |
| `/reservas/<id>/` | Detalle de una reserva. |
| `/reservas/<id>/editar/` | Edición. |
| `/reservas/<id>/eliminar/` | Confirmación y eliminación mediante POST. |
| `/reservas/<id>/confirmar/` | Confirmación mediante POST; admite respuesta JSON. |
| `/reservas/<id>/cancelar/` | Cancelación mediante POST; admite respuesta JSON. |
| `/gestion-reservas/` | Panel de gestión. |
| `/mis-reservas/` | Reservas vinculadas al usuario. |
| `/crear-reserva/` | Creación con selección automática del cliente para usuarios del grupo cliente. |
| `/admin/` | Administración de Django. |

## 🛠️ Desarrollo

### Comprobación del proyecto

```bash
python manage.py check
python manage.py showmigrations
```

`python manage.py check` comprueba la configuración de Django. Utiliza la suite de tests para verificar las reglas de negocio y los permisos.

### Pruebas

```bash
python manage.py test
```

`main/tests.py` incluye 30 pruebas de acceso, propiedad, formularios, fechas, solapamientos, estados, CSRF, paginación, sesiones y descubrimiento de JavaScript. Ejecuta la suite con `python manage.py test`.

## 🐛 Resolución de problemas

### Error 403

Comprueba los permisos del usuario. Un cliente necesita pertenecer al grupo `customers` y estar vinculado al campo `usuario` de un registro `Cliente`. La coincidencia de correo no concede acceso. Los clientes no pueden utilizar la gestión global ni cambiar estados.

### No puedo crear una reserva

El inicio debe ser hoy o posterior y el final no puede ser anterior al inicio. Las reservas activas del mismo cliente no pueden compartir fechas, incluidos los extremos del intervalo. Los errores aparecen en el formulario conservando los valores introducidos.

### Faltan datos al instalar

La entrega no incluye usuarios ni datos. Ejecuta las migraciones, crea un superusuario y configura clientes, usuarios y permisos desde Admin.

### Reglas de acceso

El listado requiere autenticación y `main.view_reserva`. Los usuarios del grupo cliente solo ven sus reservas; para clientes sin perfil explícito vinculado, el acceso se rechaza. El detalle, la edición y la eliminación buscan únicamente dentro de las reservas accesibles al usuario. Los cambios de estado y la gestión global rechazan a usuarios cliente, incluso si recibieron permisos de modificación por error.

## 🔐 Configuración y archivos locales

La clave secreta se obtiene de `DJANGO_SECRET_KEY`. Si no se define, se genera una clave local persistente en `.django-secret-key`, excluida por `.gitignore`. Define `DJANGO_SECRET_KEY` para el despliegue y no publiques la clave local. `DJANGO_DEBUG` controla el modo de depuración y `DJANGO_ALLOWED_HOSTS` admite hosts separados por comas.

Ejemplo en Linux/macOS:

```bash
export DJANGO_SECRET_KEY="tu-clave-aleatoria-propia"
export DJANGO_DEBUG="false"
export DJANGO_ALLOWED_HOSTS="tu-dominio.example"
```

El archivo `.env.example` documenta las variables; la aplicación no carga `.env` automáticamente. El despliegue también requiere configurar el servidor y los archivos estáticos.

La entrega excluye base de datos, documentos PDF y entornos virtuales. `.gitignore` evita incorporar los principales archivos locales; revisa cualquier archivo adicional antes de publicarlo.

## 🤝 Contribuciones

1. Crea una rama para tu mejora.
2. Implementa el cambio y añade pruebas cuando corresponda.
3. Actualiza la documentación.
4. Abre una pull request explicando el comportamiento y su validación.

Ideas para continuar: añadir filtros de estado, mejorar la presentación móvil y ampliar las pruebas de interfaz.

## 📄 Licencia

El proyecto adjunto no incluye un archivo `LICENSE`. Añade la licencia que corresponda antes de indicar condiciones de reutilización.

## 🙏 Contexto académico

Proyecto de **David López**, desarrollado en el contexto de **Progettazione e Sviluppo Web**, aplicando Django, HTML, CSS y JavaScript a la gestión de reservas.

---

**Organiza las reservas. Conecta clientes y fechas. 📅**

## ✅ Validación

- 30 tests automatizados superados.
- Migraciones aplicadas desde una base de datos vacía.
- `makemigrations --check --dry-run`: modelos y migraciones sincronizados.
- `collectstatic`: archivos estáticos recogidos correctamente.

La validación también se aplica en los formularios de Django Admin. Como ocurre en Django, operaciones directas como `QuerySet.update()` no ejecutan `clean()`; cualquier código futuro que escriba datos directamente debe validar las reglas. SQLite es adecuado para esta demostración local; no se ha probado la concurrencia ni un despliegue de producción. Las pruebas automatizadas comprueban las respuestas de Django; la comprobación visual de la interfaz se realiza por separado.
