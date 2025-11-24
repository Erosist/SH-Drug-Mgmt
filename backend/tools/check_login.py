from app import create_app
app=create_app()
client=app.test_client()
resp=client.post('/api/auth/login', json={'username':'admin','password':'admin666'})
print('status', resp.status_code)
print(resp.data.decode('utf-8'))
