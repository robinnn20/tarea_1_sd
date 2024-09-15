import requests
import csv
import random
import time
api_url = 'http://127.0.0.1:5000/resolve'

dataset_path = '3rd_lev_domains.csv'
max_requests = 500  # Número total de consultas a realizar
max_data_size = 200  # Tamaño máximo del dataset

def generate_requests(dataset_path, max_requests, max_data_size):
    with open(dataset_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        next(reader, None)

        domains = [row[0] for idx, row in enumerate(reader) if idx < max_data_size]

        for _ in range(max_requests):
            # Elegir un dominio aleatorio
            domain = random.choice(domains)
            response = requests.post(api_url, json={'domain': domain})
            print(f'Sent: {domain} - Status Code: {response.status_code}')
            print(f'Response: {response.text}')  

            time.sleep(0.25)
if __name__ == '__main__':
    generate_requests(dataset_path, max_requests, max_data_size)
