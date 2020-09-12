import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import connectmongo
import my_logger
from datetime import datetime
import time
from send_mail import send_warning
import settings

logger = my_logger.get_logger('PI-COVID')
logger.info("Começando atualização")


# Seleciona escopo de acesso
scope = ['https://www.googleapis.com/auth/spreadsheets']

# # Credenciais
# credentials = service_account.Credentials.from_service_account_file(filename="credentials.json")
# scopedCreds = credentials.with_scopes(scope)
# gc = gspread.Client(auth=scopedCreds)
# gc.session = AuthorizedSession(scopedCreds)

# Autoriza acesso
creds = ServiceAccountCredentials.from_json_keyfile_name(filename=settings.CRED_PATH, scopes=scope)
gc = gspread.authorize(creds)

# Informações da planilha
PICOVID = gc.open_by_key(settings.SPREAD_ID)
PAGINAS = PICOVID.worksheets()
REGEX_FALSE = r'^=IF\(\$A.*<>\"\";false;""\)$'



# Percorre todas páginas (cidades)

for P in PAGINAS:

    # carrega nome e define coleção do BD
    CITYNAME = P.__dict__['_properties']['title']
    collection = connectmongo.banco['atualizacao']

    # recupera dados
    DATA = P.get_all_values()

    # caso a pagina esteja vazia
    if (len(DATA) == 0):
        msg = f"{CITYNAME} - documento vazio"
        logger.info(msg)

        logger.debug(f"{CITYNAME} - enviando e-mail - {send_warning(msg)}")

        msg = f"{CITYNAME} - Saindo."
        logger.info(msg)

        continue


    # cria DataFrame
    df = pd.DataFrame(DATA[1:], columns=DATA[0])


    # verifica se proxima data é maior (compara 2 últimas)
    if df.shape[0] > 1:
        msg = f"{CITYNAME} - tem mais que uma linha. Conferir data."
        logger.debug(msg)

        checkDate = df.tail(2)

        d1, d2 = list(checkDate['date'])

        newD1, newD2 = time.strptime(d1, '%Y-%m-%d'), time.strptime(d2, '%Y-%m-%d')

        if newD2 > newD1:
            msg = f"{CITYNAME} - Data na última linha maior que da penúltima linha ({d2} > {d1})."
            logger.info(msg)
        else:
            msg = f"{CITYNAME} - Data na última linha MENOR ou IGUAL que penúltima linha ({d2} <= {d1})."
            logger.warning(msg)

            logger.debug(f"{CITYNAME} - enviando e-mail - {send_warning(msg)}")

            msg = f"{CITYNAME} - Saindo."
            logger.warning(msg)

            continue



    df['cityName'] = [str(i).lower() for i in df['cityName']]
    df['state'] = [str(i).lower() for i in df['state']]



    # calcula diferenças e transformar em inteiro
    diff_calc = pd.DataFrame.copy(df)

    # quais colunas não converter para inteiro?
    NOT_INT = ('date', 'processed', 'cityName', 'state', 'IBGECode')

    # quais colunas não calcular diferença?
    NOT_DIFF = ('date', 'processed', 'cityName', 'state', 'epidemiologicalWeek', 'estimatedPopulation2019', 'estimatedPopulation2020', 'IBGECode', 'daysAfterFirstCase')




    isRaised = False

    for C in diff_calc.columns:

        if C not in NOT_INT:
            try:
                diff_calc[C] = pd.to_numeric(diff_calc[C], errors='raise')
            except:
                isRaised = True
                msg = f"{CITYNAME} - houve erro ao ler números inteiros em {C}. Verifique se as informações estão corretas."
                logger.warning(msg)

                logger.debug(f"{CITYNAME} - enviando e-mail - {send_warning(msg)}")

                msg = f"{CITYNAME} - Saindo do loop."
                logger.warning(msg)
                continue


        if C not in NOT_DIFF:
            newCol = 'today' + C[0].upper() + C[1:]
            diff_calc[newCol] = diff_calc[C].diff()


    if isRaised:

        msg = f"{CITYNAME} - Saindo."
        logger.warning(msg)
        continue




    # popula banco de dados apenas com valores ainda nao atualizados
    temp_df = diff_calc[diff_calc['processed'] == 'FALSE']
    temp_df = temp_df.drop(columns='processed')


    df['processed'] = df['processed'].replace('FALSE', 'TRUE')


    # # tenta calcular ativos
    # try:
    #
    #     temp_df['totalActive'] = temp_df['totalConfirmed'].astype(int) - temp_df['totalDeath'].astype(int)  - temp_df['totalCured'].astype(int)
    #
    # except:
    #     msg = f"{CITYNAME} - houve erro ao calcular casos ativos. Verifique se as informações estão corretas."
    #     logger.warning(msg)
    #
    #     logger.debug(f"{CITYNAME} - enviando e-mail - {send_warning(msg)}")
    #
    #     msg = f"{CITYNAME} - Saindo."
    #     logger.warning(msg)
    #
    #     continue


    try:
        # Tratamento de timezone
        temp_df['isoDate'] = temp_df['date'].apply(
            lambda x: datetime.strptime(x, '%Y-%m-%d').replace(hour=3)
        )
    except:
        msg = f"{CITYNAME} - houve erro ao processar data. Verifique se o formato está %Y-%m-%d."
        logger.warning(msg)

        logger.debug(f"{CITYNAME} - enviando e-mail - {send_warning(msg)}")

        msg = f"{CITYNAME} - Saindo."
        logger.warning(msg)

        continue

    toInsert = temp_df.to_dict(orient='records')


    # insere no BD se tiver atualizaçao
    if not toInsert:
        msg = f"{CITYNAME} - não há alterações a serem realizadas no banco"
        logger.info(msg)

    else:
        msg = f"{CITYNAME} - BD foi atualizado"
        collection.insert_many(toInsert)
        logger.info(msg)
        logger.info(f"{CITYNAME} - {len(toInsert)} entrada(s) foram inserida(s) no BD")


    df = df.fillna(0)
    P.update([df.columns.values.tolist()] + df.values.tolist(),  value_input_option='USER_ENTERED')



logger.info("Finalizando atualização")



