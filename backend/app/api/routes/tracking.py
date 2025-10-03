from fastapi import APIRouter, HTTPException, Request
from app.models.schemas import ClickEvent, ConversionEvent, TrackResponse, ConversionResponse
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/events", tags=["tracking"])

# Tymczasowe przechowywanie w pamięci (póżniej będzie baza)
clicks_storage = {}
conversions_storage = {}

@router.post("/track", response_model=TrackResponse)
async def track_click(event: ClickEvent, request: Request):
    """
    Endpoint do trackowania kliknięć w reklamy.
    Wywoływany przez pixel JS.
    """
    try:
        # Generuj unikalny ID eventu
        event_id = str(uuid.uuid4())
        
        # Dodaj IP z requestu jeśli nie ma w evencie
        if not event.ip_address:
            event.ip_address = request.client.host
        
        # Zapisz w pamięci (tymczasowo)
        clicks_storage[event.session_id] = {
            "event_id": event_id,
            "click_id": event.click_id,
            "utm_source": event.utm_source,
            "utm_campaign": event.utm_campaign,
            "timestamp": event.timestamp,
            "data": event.dict()
        }
        
        print(f"✅ Click tracked: {event_id} | Session: {event.session_id} | Source: {event.utm_source}")
        
        return TrackResponse(
            success=True,
            message="Click tracked successfully",
            event_id=event_id
        )
    
    except Exception as e:
        print(f"❌ Error tracking click: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversion", response_model=ConversionResponse)
async def track_conversion(event: ConversionEvent):
    """
    Endpoint do trackowania konwersji (zakupów).
    Wywoływany przez webhook z platformy e-commerce.
    """
    try:
        # Sprawdź czy istnieje session_id w clicks
        if event.session_id not in clicks_storage:
            print(f"⚠️  Session not found: {event.session_id}")
            return ConversionResponse(
                success=True,
                message="Conversion tracked but not attributed (session not found)",
                attributed=False,
                conversion_id=str(uuid.uuid4())
            )
        
        # Pobierz dane z click eventu
        click_data = clicks_storage[event.session_id]
        conversion_id = str(uuid.uuid4())
        
        # Zapisz konwersję
        conversions_storage[event.order_id] = {
            "conversion_id": conversion_id,
            "session_id": event.session_id,
            "click_id": click_data["click_id"],
            "utm_source": click_data["utm_source"],
            "utm_campaign": click_data["utm_campaign"],
            "revenue": event.revenue,
            "currency": event.currency,
            "timestamp": event.timestamp
        }
        
        print(f"✅ Conversion tracked: {conversion_id} | Order: {event.order_id} | Revenue: {event.revenue} {event.currency}")
        print(f"   Attributed to: {click_data['utm_source']} / {click_data['utm_campaign']}")
        
        return ConversionResponse(
            success=True,
            message="Conversion tracked and attributed",
            attributed=True,
            campaign_id=click_data.get("utm_campaign"),
            conversion_id=conversion_id
        )
    
    except Exception as e:
        print(f"❌ Error tracking conversion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_stats():
    """Proste statystyki - ile mamy kliknięć i konwersji"""
    total_clicks = len(clicks_storage)
    total_conversions = len(conversions_storage)
    total_revenue = sum(c["revenue"] for c in conversions_storage.values())
    
    return {
        "total_clicks": total_clicks,
        "total_conversions": total_conversions,
        "total_revenue": round(total_revenue, 2),
        "conversion_rate": round((total_conversions / total_clicks * 100) if total_clicks > 0 else 0, 2)
    }
