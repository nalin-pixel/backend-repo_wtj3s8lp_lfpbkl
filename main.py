import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Lead, Activity

app = FastAPI(title="OneLead CRM API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility to convert ObjectId to string in results

def serialize_doc(doc: dict):
    if not doc:
        return doc
    doc["id"] = str(doc.get("_id"))
    doc.pop("_id", None)
    # Convert nested ObjectIds if any
    for k, v in list(doc.items()):
        if isinstance(v, ObjectId):
            doc[k] = str(v)
    return doc


@app.get("/")
def read_root():
    return {"message": "OneLead CRM API running"}


# -----------------------------
# Lead Endpoints
# -----------------------------

@app.post("/api/leads", response_model=dict)
def create_lead(lead: Lead):
    lead_id = create_document("lead", lead)
    return {"id": lead_id}


@app.get("/api/leads", response_model=List[dict])
def list_leads(status: Optional[str] = None, limit: int = 100):
    filter_dict = {"status": status} if status else {}
    docs = get_documents("lead", filter_dict, limit)
    return [serialize_doc(d) for d in docs]


@app.get("/api/leads/{lead_id}", response_model=dict)
def get_lead(lead_id: str):
    doc = db["lead"].find_one({"_id": ObjectId(lead_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Lead not found")
    return serialize_doc(doc)


@app.put("/api/leads/{lead_id}", response_model=dict)
def update_lead(lead_id: str, lead: Lead):
    result = db["lead"].update_one({"_id": ObjectId(lead_id)}, {"$set": lead.model_dump()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
    doc = db["lead"].find_one({"_id": ObjectId(lead_id)})
    return serialize_doc(doc)


@app.delete("/api/leads/{lead_id}")
def delete_lead(lead_id: str):
    result = db["lead"].delete_one({"_id": ObjectId(lead_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"ok": True}


# -----------------------------
# Activity Endpoints
# -----------------------------

@app.post("/api/activities", response_model=dict)
def create_activity(activity: Activity):
    # validate lead exists
    lead_doc = db["lead"].find_one({"_id": ObjectId(activity.lead_id)})
    if not lead_doc:
        raise HTTPException(status_code=400, detail="Invalid lead_id")
    activity_id = create_document("activity", activity)
    return {"id": activity_id}


@app.get("/api/leads/{lead_id}/activities", response_model=List[dict])
def list_activities(lead_id: str, limit: int = 100):
    docs = get_documents("activity", {"lead_id": lead_id}, limit)
    return [serialize_doc(d) for d in docs]


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
