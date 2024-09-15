
## Descripción
Este proyecto consiste en un script en Python que envía solicitudes a una API para resolver dominios. Utiliza un conjunto de datos descargado de Kaggle que contiene dominios, y realiza un número configurado de solicitudes a la API.

Descargar liberia 

```bash
pip install requests
```
instalara docker
```bash
sudo apt-get install docker-ce
```
Instalar docker-compose
```bash
sudo apt install docker-compose
```
Construir los contenedores
```bash
sudo docker-compose build 
```
Inicializar los contenedores
```bash
sudo docker-compose up -d 
```
Inicalmente comienza con una particion por lo que para cambiar las particiones +
2 particiones
```bash
curl -X POST http://localhost:5000/update-partitions -H "Content-Type: application/json" -d '{"partitions": 2}'
```
4 particiones
```bash
curl -X POST http://localhost:5000/update-partitions -H "Content-Type: application/json" -d '{"partitions": 4}'
```
8 particiones
```bash
curl -X POST http://localhost:5000/update-partitions -H "Content-Type: application/json" -d '{"partitions": 8}'
```
Iniciar el generador de solicitudes
```bash
sudo python3 traffic_generator.py
```
En el buscador ingresar el siguiente link pra mostrar la grafica hitt y miss rate
```bash
localhost:5000/stats
```
En el buscador ingresar el siguiente link pra mostrar la grafica de response time
```bash
localhost:5000/stats/response-time
```
En el buscador ingresar el siguiente link pra mostrar la grafica de balanceador de carga
```bash
localhost:5000/stats/load-balance
```
