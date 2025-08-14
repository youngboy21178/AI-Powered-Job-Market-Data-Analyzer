import sqlite3
from sqlite3 import Connection, Cursor

from models import *

def _get_connection(db_path:str="data_base/main_data_base.db") -> Connection:
    return sqlite3.connect(db_path) 

def create_jobs_table() -> None:
    conn: Connection = _get_connection()
    try:
        cursor: Cursor = conn.cursor()
        cursor.execute(CREATE_JOBS_TABLE)
        conn.commit()
    finally:
        conn.close()

def _insert_job(job: JobDescription , conn: Connection) -> None:
    try:
        cursor: Cursor = conn.cursor()
        cursor.execute(INSERT_TO_JOBS_TABLE, (job.job_title, job.company_name, job.location, job.salary, job.job_type, job.hard_skills, job.soft_skills, job.work_mode))
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred while inserting job data: {e}")

def insert_jobs(jobs: list[JobDescription]) -> None:
    conn: Connection = _get_connection()
    for job in jobs:
        _insert_job(job, conn)
    conn.close()

def get_jobs(count: int = 25) -> list[dict]:
    conn: Connection = _get_connection()
    try:
        conn.row_factory = sqlite3.Row  
        cursor: Cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM jobs LIMIT ?", (count,))
        rows = cursor.fetchall()
        job_description_list = [dict(row) for row in rows] 
        for job in job_description_list:
            for hard_skill in job.get("hard_skills", []):
                hard_skill = hard_skill.strip().lower()
            for soft_skill in job.get("soft_skills", []):
                soft_skill = soft_skill.strip().lower()
            job["work_mode"] = job.get("work_mode", "").strip().lower()
        result = []
        for job in job_description_list:
            _job_description = JobDescription(**job)
            result.append(_job_description)
        return result
    finally:
        conn.close()

def clear_jobs():
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM jobs;")
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

