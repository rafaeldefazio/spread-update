# spread-update

Script para atualização do BD via Google Spreadsheet, contendo informações epidemiológicas de cidades participantes do PI-COVID (Painel Interativo do Coronavírus).


# Instalação
1. Clone o repositório
1. Instale uma ambiente virtual no diretório baixado (`python3 -m venv .`)
1. Ative o ambiente virtual (`source bin/activate`)
1. Instale as dependências (`pip install -r requirements.txt`)
1. Crie `.venv` com as variáveis escritas em `settings.py`
1. Não esqueça de baixar as credenciais da Conta de Serviço do Google (mais na [documentação do gspread](https://gspread.readthedocs.io/en/latest/oauth2.html#for-bots-using-service-account))

# Execução períodica
A fim de executar o script a cada 1 hora, foi adicionado ao `crontab` do sistema, por meio do `crontab -e`:

```sh
0 * * * * <caminho-absoluto>/spread-update/bin/python3 <caminho-absoluto>/spread-update/main.py >> <caminho-absoluto>/spread-update/cron.log 2>&1
```

A cada hora (ou seja, quando os minutos estiverem zerados), o script `main.py` é executado através do _python3_ localizado no ambiente virtual criado anteriormente. Os outputs do cron são gravados no arquivo `cron.log`, para debug.


# Configurações do .env
- `SPREAD_ID:` ID do Google Spreadsheet
- `CRED_PATH:` Caminho absoluto das credenciais da Conta de Serviços do Google (`.json`)
- `LOG_PATH:` Caminho absoluto para arquivo de log
- `MONGO_URL`: URL do MongoDB
- `MONGO_PORT`: PORT do MongoDB
- `MONGO_DB`: Database do MongoDB
- `MAILGUN_BASEURL`: Base URL fornecido pelo Mailgun
- `MAINGUN_API`: API Key fornecida pelo Mailgun
- `MAINGUN_DOMAIN`: Domínio utilizado para envio de emails (from)
