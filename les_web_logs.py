import requests
from datetime import date, datetime, timedelta
import time
import os
import glob
import logging
import akvut


idag = date.today().isoformat()
logger = akvut.lag_logger(f'loggfil-les_web_logs-{idag}.log')

# Finn alle filer som samsvarar med mønsteret "web_logs-*.txt"
filer = glob.glob("web_logs-*.txt")

# Dersom det er slike filer vert dei først sletta
if filer is not []:
    for fil in filer:
        try:
            os.remove(fil)
            logger.info(f"Slettet fil: {fil}")
        except OSError as e:
            logger.error(f"Error: {fil} : {e.strerror}")

# Hent access_token
access_token = akvut.les_access_token(logger)

if access_token is not None:  
    # Les tidspunkt for forrige oppdatering
    try:
        with open("sist_oppdatert_web_logs.txt", "r") as f_in:
            sist_oppdatert = f_in.read()
    except:
        sist_oppdatert = (datetime.now()-timedelta(days=1)).isoformat() + "Z"

    # Hent oppdateringane
    start_sjekk_status = time.perf_counter()
    requesturl = "https://api-gateway.instructure.com/dap/query/canvas_logs/table/web_logs/data"
    payload = '{"format": "csv", "since": \"%s\"}' % (sist_oppdatert)
    headers = {'x-instauth': access_token, 'Content-Type': 'text/plain'}
    logger.info(f"Sender (inkrementel) spørjing til {requesturl}")
    r = requests.request(
        "POST",
        requesturl,
        headers=headers,
        data=payload
    )
    if r.status_code == 200:
        respons = r.json()
        id = respons['id']
        vent = True
        while vent:
            logger.info(f"Sjekker status på jobb {id}")
            requesturl = f"https://api-gateway.instructure.com/dap//job/{id}"
            r2 = requests.request("GET", requesturl, headers=headers)
            respons2 = r2.json()
            if respons2['status'] == "complete":
                vent = False
            time.sleep(5)
        logger.info("Status oppdatert")
    else:
        logger.error(f"Feil i spørjing, kode {r.status_code}")
    antal = len(respons2['objects'])
    tidsbruk_sjekk_status = time.perf_counter() - start_sjekk_status
    logging.info(f"Totalt for sjekk_status: {tidsbruk_sjekk_status}")

    # Hent filane
    start_hent_filar = time.perf_counter()
    filar_i_dag = []
    for i in range(antal):
        innfil = respons2['objects'][i]['id']
        payload = f"{respons2['objects']}"
        f = akvut.hent_filar(innfil, access_token, payload, i, logger)
        filar_i_dag.append(f)
    tidsbruk_hent_filar = time.perf_counter() - start_hent_filar
    logging.info(f"Totalt for hent_filar: {tidsbruk_hent_filar}")
        # Skriv tidspunkt for siste oppdatering til fil
    with open('sist_oppdatert_web_logs.txt', 'w') as f_out:
        f_out.write(respons2['until'])

else:
    logger.error("Fant ikke access_token")