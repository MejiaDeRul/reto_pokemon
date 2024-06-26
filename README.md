# API reto pokemon seguro
Hola, bienvenido a mi API.
En esta se logran 4 retos:
- Obtener los tipos de un pokemon dado
- Obtener un pokemon al azar de un tipo dado
- Obtener el pokemon con el nombre mas largo de un tipo dado
- Obtener un pokemon al azar de el mejor tipo de mi zona y que contenga las letras 'i', 'a' o 'm' en su nombre

Esta API se conecta a otras dos para lograr los resultados:
- Poke-Api para obtener los datos de los pokemons
- Open-Meteo para obtener la temperatura de mi zona

## Usar API de manera local
Si quieres usar la API en tu ordenador de manera local debes seguir los siguientes pasos:
- Clonar el repositorio con -> git clone
- Crear un archivo '.env', este es el unico archivo a crear debido a que aqui se exponen datos sensibles
- Añadir las variables de entorno como estan en el archivo '.env.example' y cambiar los valores de cada una de las variables
- Para las dos variables de llave secreta, usar este comando para generar las llaves (Pegarlo en la terminal de tu ordenador, es necesario tener python) -> python -c 'import secrets; print(secrets.token_hex())'
- Debes ingresar ademas un correo valido de outlook con su contraseña, sino quieres hacerlo he creado uno solo para el caso, preguntame por el
- Por ultimo en '.env' defines un usuario y contraseña para la base de datos de mongo
- Luego de tener este archivo listo Iniciar Docker Desktop o instalarlo sino cuenta con el
- En la terminal ejecutar -> docker compose up
- Si todo funciona correctamente, en su navegador de preferencia ir a esta direccion -> http://127.0.0.1:5000
- Listo, ya puedes empezar a usar la API, empezando por registrar el primer usuario

## Documentacion de la API
La API tiene una documentacion creada con swagger para mostrar ejemplo de que solicitan y responden los endpoints dentro de esta. Para acceder a esta ingresa -> http://127.0.0.1:5000/apidocs

## Esquemas de autenticacion
La API cuenta con 4 esquemas de autenticacion:
- **Registro de usuario y confirmacion de correo electronico**: Al registrar un usuario, se solicitan datos basicos, dentro de ellos un usuario y un correo electronico. Despues de crear una cuenta se envia un link al correo electronico ingresado para verificar y confirmar el correo.
- **Inicio de sesion con usuario y contraseña**: El usuario ingresa a su cuenta de la API ingresando su usuario y contraseña, los cuales seran verificados para decidir si darle acceso o no.
- **Verificacion de doble factor**: Luego de verificar los datos al iniciar sesion y ser correctos, se envia un codigo de un solo uso (OTP) al correo del usuario, este mismo debe ingresar el codigo para completar el inicio de sesion.
- **Token JWT**: Luego de iniciar sesion correctamente, se genera un token JWT (JSON Web Token) para ciertas funcionalidades de la aplicacion.

## Notas
- Se crean dos containers de Docker, uno para una base de datos MongoDB y el otro para cargar la API, al estar activos la base de datos se puede visualizar por ejemplo en visual studio code con la extension de MongoDB, solo cambiar 'monguito' por 'localhost' dentro de las variables de entorno en 'MONGO_URI'
- Si sale algun error, en el archivo logs sale mas legible tambien los errores del servidor
- Algunas acciones pueden tardar un poco pero ya depende de la conexion a internet y la potencia del ordenador
- Tambien al iniciar la API la primera vez puede que salga ya directamente en los puntos de los retos, si pasa solo hay que darle cerrar sesion
- Si algo no sale bien contactarse conmigo
