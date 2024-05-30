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
- Luego de tener este archivo list Iniciar Docker Desktop o instalarlo sino cuenta con el
- En la terminal ejecutar -> docker compose up
- Si todo funciona correctamente, en su navegador de preferencia ir a esta direccion -> http://127.0.0.1:5000
- Listo, ya puedes empezar a usar la API, empezando por registrar el primer usuario
  

