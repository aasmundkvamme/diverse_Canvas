import pandas as pd
import glob
import os
import pyodbc
import akvut
from datetime import date, timedelta

today = date.today()
idag = today.isoformat()
igår = (today - timedelta(days=1)).isoformat()

# logging = akvut.lag_logger(f'loggfil-ny_history-{idag}.log')

# filer = glob.glob("web_logs-*.txt")

try:
    data = akvut.ny_les_web_logs()

    logging.info(f"Les {len(filer)} filer")
    # data = pd.concat([pd.read_csv(f) for f in filer])
    # data = data.astype(str)
    antal = len(data)
    logging.info(f"Antall linjer: {antal}")
    temp = data[['value.timestamp', 'value.url', 'value.user_id', 'value.course_id', 'value.web_application_controller', 'value.web_application_action', 'value.web_application_context_type']]
    temp = temp[~temp['value.url'].str.contains("/api/")]
    temp = temp[~temp['value.web_application_action'].str.contains("retrieve")]
    med_user_id = temp[temp['value.user_id'].notna()]
    # med_user_id.to_csv(f"/home/aasmund/diverse_Canvas/ny_history.csv", index=False)
    conn_str = os.environ['Connection_SQL']
    with pyodbc.connect(conn_str) as connection:
        cursor = connection.cursor()
        try:
            query = """
                INSERT INTO [dbo].[akv_ny_canvas_history] ([timestamp], [user_id], [course_id], [web_application_controller], [web_application_action], [web_application_context_type], [url])
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            for index, row in med_user_id.iterrows():
                timestamp = row['value.timestamp']
                url = row['value.url']
                course_id = row['value.course_id']
                user_id = row['value.user_id']
                web_application_controller = row['value.web_application_controller']
                web_application_action = row['value.web_application_action']
                web_application_context_type = row['value.web_application_context_type']
                cursor.execute(query, (timestamp, user_id, course_id, web_application_controller, web_application_action, web_application_context_type, url))
            connection.commit()
        except pyodbc.Error as exc:
            logging.error(exc)
    # med_user_id.to_csv("/home/aasmund/diverse_Canvas/ny_history.csv", index=False)
except:
    logging.info("Feil ved opplastinga")