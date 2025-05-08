class Feature2Schema(BaseModel):
    id: Optional[int] = Field(None, description="Unique identifier for the feature1 item")
    name: str = Field(..., description="Name of the feature1 item")
    description: Optional[str] = Field(None, description="Description of the feature1 item")
    created_at: Optional[str] = Field(None, description="Creation timestamp of the feature1 item")
    updated_at: Optional[str] = Field(None, description="Last update timestamp of the feature1 item")