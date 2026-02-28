import requests

# Configuración
TOKEN_URL = 'http://127.0.0.1:8000/o/token/'
API_URL = 'http://127.0.0.1:8000/api/libros/'

CLIENT_ID = '9ch0LE7JyQyL7KGjTqe8QzwAbPiRE727x7RtMz8w'
CLIENT_SECRET =  "R7QiAPMMItjzroaMpCgdtF1UQuVwGJ1mbRFWXW5fMX5MQSca7pgGl7hEJK9cePBZyX7E8L7qMGrQ74uBryy4AOk5xgZQ6uHmFIVXoBKTv5sbvNoTh9vfJimJVXGz4TKM"
USERNAME = 'admin'
PASSWORD = 'admin123'

print("=== Obteniendo Token OAuth 2.0 ===")

# Obtener token
response = requests.post(TOKEN_URL, data={
    'grant_type': 'password',
    'username': USERNAME,
    'password': PASSWORD,
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'scope': 'read write'
})

if response.status_code == 200:
    token_data = response.json()
    access_token = token_data['access_token']
    
    print(f"✅ Token obtenido: {access_token[:50]}...")
    
    # Usar token para acceder a API
    headers = {'Authorization': f'Bearer {access_token}'}
    api_response = requests.get(API_URL, headers=headers)
    
    print(f"Status Code: {api_response.status_code}")
    print(f"Data: {api_response.json()}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.json())