from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ClickEvent(BaseModel):
    """Zdarzenie kliknięcia w reklamę"""
    pixel_id: str = Field(..., description="ID pixela trackingowego")
    event_type: str = Field(default="click", description="Typ zdarzenia")
    
    # Tracking IDs
    click_id: Optional[str] = Field(None, description="fbclid, gclid, itp.")
    click_id_type: Optional[str] = Field(None, description="Typ click_id")
    session_id: str = Field(..., description="ID sesji użytkownika")
    
    # UTM Parameters
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_term: Optional[str] = None
    utm_content: Optional[str] = None
    
    # Page Data
    page_url: str = Field(..., description="URL strony")
    referrer: Optional[str] = None
    
    # User Fingerprint
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Timestamp
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)

class ConversionEvent(BaseModel):
    """Zdarzenie konwersji (zakup)"""
    session_id: str = Field(..., description="ID sesji z click eventu")
    order_id: str = Field(..., description="Unikalny ID zamówienia")
    
    # Revenue
    revenue: float = Field(..., gt=0, description="Wartość zamówienia")
    currency: str = Field(default="USD", description="Waluta")
    
    # Optional User Data (for CAPI)
    email: Optional[str] = None
    phone: Optional[str] = None
    
    # Timestamp
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)

class TrackResponse(BaseModel):
    """Odpowiedź z endpointu trackingu"""
    success: bool
    message: str
    event_id: Optional[str] = None

class ConversionResponse(BaseModel):
    """Odpowiedź z endpointu konwersji"""
    success: bool
    message: str
    attributed: bool
    campaign_id: Optional[str] = None
    conversion_id: Optional[str] = None
