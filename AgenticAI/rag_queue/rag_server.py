from fastapi import FastAPI, Query
from .client.rq_client import queue
from .queues.worker import process_query

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "server is up and running"}

@app.post("/query")
def chat(query: str = Query(..., description="The query to process")):
    # Enqueue the query for processing in the background worker
    job = queue.enqueue(process_query, query)
    return {"status": "Query received and is being processed", "job_id": job.get_id()}

@app.get("/job_status")
def get_job_status(job_id: str = Query(..., description="The ID of the job to check")):
    job = queue.fetch_job(job_id)
    if job is None:
        return {"status": "Job not found"}
    elif job.is_finished:
        return {"status": "Job finished", "result": job.result}
    elif job.is_failed:
        return {"status": "Job failed", "error": str(job.exc_info)}
    else:
        return {"status": "Job is still processing"}