from email.message import EmailMessage
import requests
from send_msg import send
from jinja2 import Template
from apscheduler.schedulers.blocking import BlockingScheduler
from pytz import timezone
from datetime import datetime

# Email que será usado para enviar
sender_email = ""
# Email que irá receber
receiver_email = ""
# Lista de emails que serão copiados
cc_email = [
    
]

UNIDADE = "GIASA"
# URL para se comunicar com API interna
API_URL = 'http://10.10.12.200:8525/api/get_parametros_op'

def format_value(value):
    if value is None or value == '' or value == 'null':
        return '-'
    return str(value)

def send_email_parametros():
    try:
        response = requests.get(API_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Erro ao buscar os dados: {e}")
        data = []

    grupos = {}
    for item in data:
        grupo = item.get('grupo') or 'SEM GRUPO'
        if grupo not in grupos:
            grupos[grupo] = []
        grupos[grupo].append(item)

    meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun',
             'jul', 'ago', 'set', 'out', 'nov', 'dez']
    agora = datetime.now()
    data_exibir = f"{agora.day:02d}/{meses[agora.month - 1]}"

    with open('template.html', 'r', encoding='utf-8') as file:
        html_template = file.read()

    template = Template(html_template)
    html_final = template.render(
        unidade=UNIDADE,
        data=data_exibir,
        grupos=grupos,
        format_value=format_value
    )

    msg = EmailMessage()
    msg["to"] = receiver_email
    msg["cc"] = cc_email
    msg["from"] = sender_email
    msg["subject"] = f"Parâmetros Operacionais de Processo - {UNIDADE}"
    msg.set_content(html_final, subtype="html")
    msg.make_related()

    try:
        send(msg, sender_email)
        print("Email com parâmetros operacionais enviado com sucesso.", flush=True)
    except Exception as e:
        print(f"Erro ao disparar email via send_msg: {e}", flush=True)

if __name__ == "__main__":
    try:
        scheduler = BlockingScheduler(timezone=timezone('America/Sao_Paulo'))
        scheduler.add_job(
            send_email_parametros, "cron", hour="9,13,17,21,1,5", minute="0", id="job_parametros"
        )

        print("Agendador iniciado com sucesso.", flush=True)

        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Agendador encerrado.", flush=True)
    except Exception as e:
        print(f"Agendador encerrado devido a erro: {e}", flush=True)