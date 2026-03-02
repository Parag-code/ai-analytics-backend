import xml.etree.ElementTree as ET
from sqlalchemy import create_engine, text
from app.database.db import engine  # Use your engine


file_path = "/app/app/data/data.xml"

def import_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    with engine.connect() as conn:

        # Insert into Observation Table
        for obs in root.find("OBSERVATIONS").findall("OBS"):
            data = {
                "REFOBS_ID": obs.findtext("REFOBS_ID"),
                "TYPE": obs.findtext("TYPE"),
                "REF_START_DATETIME": obs.findtext("REF_START_DATETIME"),
                "REF_END_DATETIME": obs.findtext("REF_END_DATETIME"),
                "ALONG_TRACK_TIME_OFFSET": int(obs.findtext("ALONG_TRACK_TIME_OFFSET") or 0),
                "LSAR_SQUINT_TIME_OFFSET": int(obs.findtext("LSAR_SQUINT_TIME_OFFSET") or 0),
                "SSAR_SQUINT_TIME_OFFSET": int(obs.findtext("SSAR_SQUINT_TIME_OFFSET") or 0),
                "LSAR_JOINT_OP_TIME_OFFSET": int(obs.findtext("LSAR_JOINT_OP_TIME_OFFSET") or 0),
                "SSAR_JOINT_OP_TIME_OFFSET": int(obs.findtext("SSAR_JOINT_OP_TIME_OFFSET") or 0),
                "PRIORITY": obs.findtext("PRIORITY"),
                "CMD_LSAR_START_DATETIME": obs.findtext("CMD_LSAR_START_DATETIME"),
                "CMD_LSAR_END_DATETIME": obs.findtext("CMD_LSAR_END_DATETIME"),
                "CMD_SSAR_START_DATETIME": obs.findtext("CMD_SSAR_START_DATETIME"),
                "CMD_SSAR_END_DATETIME": obs.findtext("CMD_SSAR_END_DATETIME"),
                "LSAR_PATH": obs.findtext("LSAR_PATH"),
                "SSAR_PATH": obs.findtext("SSAR_PATH"),
                "LSAR_CONFIG_ID": int(obs.findtext("LSAR_CONFIG_ID") or 0),
                "SSAR_CONFIG_ID": int(obs.findtext("SSAR_CONFIG_ID") or 0),
                "DATATAKE_ID": obs.findtext("DATATAKE_ID"),
                "SEGMENT_DATATAKE_ON_SSR": obs.findtext("SEGMENT_DATATAKE_ON_SSR"),
                "OBS_SUPPORT": obs.findtext("OBS_SUPPORT"),
                "INTRODUCED_IN": obs.findtext("INTRODUCED_IN")
            }

            insert_obs = text("""
                INSERT INTO observation VALUES (
                    :REFOBS_ID, :TYPE, :REF_START_DATETIME, :REF_END_DATETIME,
                    :ALONG_TRACK_TIME_OFFSET, :LSAR_SQUINT_TIME_OFFSET,
                    :SSAR_SQUINT_TIME_OFFSET, :LSAR_JOINT_OP_TIME_OFFSET,
                    :SSAR_JOINT_OP_TIME_OFFSET, :PRIORITY,
                    :CMD_LSAR_START_DATETIME, :CMD_LSAR_END_DATETIME,
                    :CMD_SSAR_START_DATETIME, :CMD_SSAR_END_DATETIME,
                    :LSAR_PATH, :SSAR_PATH,
                    :LSAR_CONFIG_ID, :SSAR_CONFIG_ID,
                    :DATATAKE_ID, :SEGMENT_DATATAKE_ON_SSR,
                    :OBS_SUPPORT, :INTRODUCED_IN
                )
            """)

            conn.execute(insert_obs, data)

        # Insert Session Mappings
        sessions = root.find("SSAR_SESSIONS")

        if sessions is not None:
            for sess in sessions.findall("S_IMG_SESSION"):
                sess_id = sess.findtext("SESS_ID")
                refobs_ids = sess.findtext("REFOBS_IDS")

                if refobs_ids:
                    for oid in refobs_ids.split():
                        conn.execute(
                            text("""
                                INSERT INTO session_observation (SESS_ID, REFOBS_ID)
                                VALUES (:sess_id, :refobs_id)
                            """),
                            {"sess_id": sess_id, "refobs_id": oid}
                        )

        conn.commit()

    return "XML Data Inserted Successfully"


if __name__ == "__main__":
    result = import_xml(file_path)
    print(result)