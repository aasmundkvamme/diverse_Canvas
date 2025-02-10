import requests
from datetime import date, datetime, timedelta
import time
import logging
import akvut
import pandas as pd


idag = date.today().isoformat()
logging = akvut.lag_logger(f'loggfil-les_web_logs-{idag}.log')


def ny_les_web_logs():
    # Hent access_token
    access_token = akvut.les_access_token(logging)

    if access_token is not None:  
        # Les tidspunkt for forrige oppdatering
        sist_oppdatert = akvut.akv_finn_sist_oppdatert("web_logs")

        # Hent oppdateringane
        start_sjekk_status = time.perf_counter()
        requesturl = "https://api-gateway.instructure.com/dap/query/canvas_logs/table/web_logs/data"
        payload = '{"format": "csv", "since": \"%s\"}' % (sist_oppdatert)
        headers = {'x-instauth': access_token, 'Content-Type': 'text/plain'}
        logging.info(f"payload er {payload}")
        logging.info(f"Sender (inkrementel) spørjing til {requesturl}")
        r = requests.request(
            "POST",
            requesturl,
            headers=headers,
            data=payload
        )
        if 200 <= r.status_code < 300:
            respons = r.json()
            id = respons['id']
            vent = True
            while vent:
                logging.info(f"Sjekker status på jobb {id}")
                requesturl = f"https://api-gateway.instructure.com/dap//job/{id}"
                r2 = requests.request("GET", requesturl, headers=headers)
                respons2 = r2.json()
                if respons2['status'] == "complete":
                    vent = False
                time.sleep(5)
            logging.info("Status oppdatert")
        else:
            logging.error(f"Feil i spørjing, kode {r.status_code}\n{r.content}")
            return None
        antal = len(respons2['objects'])
        tidsbruk_sjekk_status = time.perf_counter() - start_sjekk_status
        logging.info(f"Totalt for sjekk_status: {tidsbruk_sjekk_status}")

        # Hent filane
        start_hent_filar = time.perf_counter()
        web_logs_liste = []
        for i in range(antal):
            innfil = respons2['objects'][i]['id']
            payload = f"{respons2['objects']}"
            f = akvut.ny_hent_filar(innfil, access_token, payload, i, logging)
            web_logs_liste.append(f)
        web_logs = pd.concat(web_logs_liste)
        tidsbruk_hent_filar = time.perf_counter() - start_hent_filar
        logging.info(f"Totalt for hent_filar: {tidsbruk_hent_filar}")
        # logging.info(f"web_logs er {web_logs.info()}")
        # Skriv tidspunkt for siste oppdatering til fil
        akvut.akv_skriv_sist_oppdatert("web_logs", respons2['until'])
        return web_logs

    else:
        logging.error("Fant ikkje access_token") 
        return None

ny_les_web_logs()