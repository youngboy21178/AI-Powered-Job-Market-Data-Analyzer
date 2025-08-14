from typing import Optional
from pydantic import BaseModel, Field

class GeoId(BaseModel):
    geo_id: str = Field(..., description="Geographical identifier")
    country: str = Field(..., description="Country associated with the geo ID")

class JobDescription(BaseModel):
    job_title: Optional[str] = Field(..., description="Title of the job")
    company_name: Optional[str] = Field(..., description="Name of the company")
    location: Optional[str] = Field(..., description="Location of the job")
    job_type: Optional[str] = Field(..., description="Type of job (e.g., full-time, part-time, contract)")

    salary: Optional[str] = Field(..., description="Salary offered for the job")
    hard_skills: Optional[str] = Field(..., description="Required hard skills for the job")
    soft_skills: Optional[str] = Field(..., description="Required soft skills for the job")
    work_mode: Optional[str] = Field(..., description="Work mode: remote, office, or hybrid")

CREATE_GEO_ID_TABLE = (
    "CREATE TABLE IF NOT EXISTS geo_id (" 
    "id INTEGER PRIMARY KEY AUTOINCREMENT, " 
    "geo_id TEXT NOT NULL, " 
    "country TEXT NOT NULL)" 
)
CREATE_JOBS_TABLE = (
    "CREATE TABLE IF NOT EXISTS jobs ("
    "id INTEGER PRIMARY KEY AUTOINCREMENT,"
    "job_title TEXT,"
    "company_name TEXT,"
    "location TEXT,"
    "hard_skills TEXT,"
    "soft_skills TEXT,"
    "work_mode TEXT," 
    "salary TEXT,"
    "job_type TEXT)"
)

INSERT_TO_JOBS_TABLE = (
    "INSERT INTO jobs (job_title, company_name, location, salary, job_type, hard_skills, soft_skills, work_mode) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
)
AI_PROMPT = """
You are an information extraction system.

JOB DESCRIPTION:
{description}

TASK:
Extract ONLY ONE valid JSON object with EXACTLY these fields:
- job_title: string | null
- company_name: string | null
- location: string | null
- salary: string | null
- job_type: string | null  (e.g., full-time, part-time, contract)
- work_mode: string | null (remote, office, hybrid)
- soft_skills: list[string] | null
- hard_skills: list[string] | null

RULES:
1. If any field is missing, set its value to null.
2. Output ONLY one JSON object.
3. Do NOT repeat the JSON.
4. Do NOT write explanations or thoughts.
5. The first character of your output must be `{{` and the last must be `}}`.
6. Stop immediately after the closing `}}`.
7. Follow the example format exactly.

EXAMPLE OUTPUT:
{{\"job_title\": \"Example\", \"company_name\": null, \"location\": null, \"salary\": null, \"job_type\": null, \"work_mode\": null, \"soft_skills\": null, \"hard_skills\": null}}

NOW RETURN THE JSON
"""

