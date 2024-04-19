from flask import Flask, request
import requests
from flask import Response
import re

app = Flask(__name__)

# URL da outra API para a qual os dados serão redirecionados
AUTH_URL = "https://autenticacao.dev.ufopa.edu.br/"
API_SIGAA_URL = "https://api.dev.ufopa.edu.br/"

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def catch_all(path):
    # Obtém os dados da requisição
    data = request.get_data()
    headers = dict(request.headers)  # Converte EnvironHeaders para um dicionário

    # Remove o cabeçalho "Host" do dicionário de cabeçalhos
    if 'Host' in headers:
        del headers['Host']  # Não sei por que, mas da erro

    # Monta a URL da outra API
    if path.startswith('api/'):
        target_url = API_SIGAA_URL + re.sub('api/', '', path, 1)
    elif path.startswith('api'):
        target_url = API_SIGAA_URL + re.sub('api', '', path, 1)
    else:
        target_url = AUTH_URL + path
    
    try:
        response = requests.request(
            method=request.method,
            url=target_url,
            data=data,
            headers=headers,
            params=request.args,
            verify=False,
            timeout=10  # Defina o timeout desejado
        )

        # Criando uma resposta do Flask com os cabeçalhos da resposta original
        flask_response = Response(response.content, status=response.status_code)
        for key, value in response.headers.items():
            # Ajusta o cabeçalho 'Content-Encoding' se o conteúdo foi descomprimido
            if key.lower() == 'content-encoding' and 'gzip' in value:
                continue
            flask_response.headers[key] = value

        return flask_response
    except requests.RequestException as e:
        print(e)
        # Lida com erros de requisição
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
