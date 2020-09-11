import requests
import settings

def send_warning(msg):

    return requests.post(
		settings.MAILGUN_BASEURL,
		auth=("api", settings.MAINGUN_API),
		data={"from": f"BOT PI-COVID <bot@{settings.MAINGUN_DOMAIN}>",
			"to": [settings.MAILGUN_TO],
			"subject": "PI-COVID: Erro na atualização",
			"text": msg}
    )