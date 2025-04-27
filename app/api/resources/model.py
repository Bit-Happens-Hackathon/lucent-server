from typing import Optional
from pydantic import BaseModel, Field

class ResourceCreate(BaseModel):
    """
    Data model for creating a new resource.
    """
    type: str = Field(..., description="Type of resource")
    link: str = Field(..., description="Link to the resource")

class ResourceResponse(BaseModel):
    """
    Data model for resource response.
    """
    type: str
    link: str

class ResourceUpdate(BaseModel):
    """
    Data model for updating a resource.
    """
    link: Optional[str] = None