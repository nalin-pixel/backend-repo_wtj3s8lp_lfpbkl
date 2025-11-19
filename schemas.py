"""
Database Schemas for OneLead CRM

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercase of the class name (e.g., Lead -> "lead").
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
from datetime import datetime

# -----------------------------
# Core CRM Schemas
# -----------------------------

class Lead(BaseModel):
    """
    Leads collection schema
    Collection: "lead"
    """
    first_name: str = Field(..., description="Lead first name")
    last_name: str = Field(..., description="Lead last name")
    email: Optional[EmailStr] = Field(None, description="Primary email")
    phone: Optional[str] = Field(None, description="Primary phone number")
    company: Optional[str] = Field(None, description="Company name")
    source: Optional[str] = Field("Manual", description="Lead source")
    status: Literal["new", "contacted", "qualified", "lost", "customer"] = Field(
        "new", description="Sales status"
    )
    owner: Optional[str] = Field(None, description="Owner/user id or name")
    notes: Optional[str] = Field(None, description="Free text notes")

class Activity(BaseModel):
    """
    Activities linked to a lead
    Collection: "activity"
    """
    lead_id: str = Field(..., description="Related lead _id as string")
    type: Literal["call", "email", "meeting", "note", "task"] = Field(
        "note", description="Activity type"
    )
    content: str = Field(..., description="Activity content/summary")
    scheduled_for: Optional[datetime] = Field(None, description="When it is scheduled")
    done: bool = Field(False, description="Whether completed")
    owner: Optional[str] = Field(None, description="Owner/user id or name")

# Optionally define a simple Pipeline model if needed later
class PipelineStage(BaseModel):
    name: str = Field(...)
    order: int = Field(..., ge=0)
