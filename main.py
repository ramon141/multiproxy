from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

# URL da outra API para a qual os dados serão redirecionados
API_SIGAA_URL = "https://sigaa-api.up.railway.app/"
AUTH_URL = "http://localhost/"

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def catch_all(path):
    # Obtém os dados da requisição
    data = request.get_data()
    headers = dict(request.headers)  # Converte EnvironHeaders para um dicionário

    # Remove o cabeçalho "Host" do dicionário de cabeçalhos
    if 'Host' in headers:
        del headers['Host'] # Não sei por que, mas da erro
    
    # Monta a URL da outra API
    if path.startswith('api/'):
        target_url = API_SIGAA_URL + re.sub('api/', '', path, 1)
    elif path.startswith('auth/'):
        target_url = AUTH_URL + re.sub('auth/', '', path, 1)
    if path.startswith('api'):
        target_url = API_SIGAA_URL + re.sub('api', '', path, 1)
    elif path.startswith('auth'):
        target_url = AUTH_URL + re.sub('auth', '', path, 1)
    else:
        return f"A rota {path} não é reconhecida", 500
    
    try:
        # Faz a chamada para a outra API
        response = requests.request(
            method=request.method,
            url=target_url,
            data=data,
            headers=headers,
            params=request.args,
            verify=False,
            timeout=10  # Defina o timeout desejado
        )

        # Retorna os resultados da outra API
        return response.text, response.status_code
    except requests.RequestException as e:
        print(e)
        # Lida com erros de requisição
        return str(e), 500


if __name__ == '__main__':
    app.run(debug=True)
