(function() {
  'use strict';
  
  // Konfiguracja
  const config = {
    apiUrl: 'http://localhost:8000/api/events/track',
    pixelId: 'px_demo_001', // Unikalny ID pixela (później z dashboard)
  };
  
  // Funkcja do generowania session ID
  function getSessionId() {
    let sessionId = getCookie('_track_session');
    if (!sessionId) {
      sessionId = 'sess_' + generateUUID();
      setCookie('_track_session', sessionId, 30); // 30 dni
    }
    return sessionId;
  }
  
  // Generowanie UUID
  function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }
  
  // Cookie helpers
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  }
  
  function setCookie(name, value, days) {
    const expires = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = `${name}=${value}; expires=${expires}; path=/; SameSite=Lax`;
  }
  
  // Pobieranie parametrów UTM z URL
  function getUrlParams() {
    const params = new URLSearchParams(window.location.search);
    return {
      utm_source: params.get('utm_source'),
      utm_medium: params.get('utm_medium'),
      utm_campaign: params.get('utm_campaign'),
      utm_term: params.get('utm_term'),
      utm_content: params.get('utm_content'),
      fbclid: params.get('fbclid'),
      gclid: params.get('gclid'),
    };
  }
  
  // Zbieranie fingerprint
  function getFingerprint() {
    return {
      screen_width: window.screen.width,
      screen_height: window.screen.height,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      language: navigator.language,
      platform: navigator.platform,
    };
  }
  
  // Główna funkcja trackowania
  function trackEvent() {
    const urlParams = getUrlParams();
    const sessionId = getSessionId();
    
    // Wykryj click_id (fbclid lub gclid)
    let clickId = null;
    let clickIdType = null;
    
    if (urlParams.fbclid) {
      clickId = urlParams.fbclid;
      clickIdType = 'fbclid';
    } else if (urlParams.gclid) {
      clickId = urlParams.gclid;
      clickIdType = 'gclid';
    }
    
    // Przygotuj dane eventu
    const eventData = {
      pixel_id: config.pixelId,
      event_type: 'click',
      session_id: sessionId,
      click_id: clickId,
      click_id_type: clickIdType,
      utm_source: urlParams.utm_source,
      utm_medium: urlParams.utm_medium,
      utm_campaign: urlParams.utm_campaign,
      utm_term: urlParams.utm_term,
      utm_content: urlParams.utm_content,
      page_url: window.location.href,
      referrer: document.referrer || null,
      user_agent: navigator.userAgent,
    };
    
    // Wyślij do API
    fetch(config.apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(eventData),
    })
    .then(response => response.json())
    .then(data => {
      console.log('✅ Tracking pixel fired:', data);
    })
    .catch(error => {
      console.error('❌ Tracking pixel error:', error);
    });
  }
  
  // Uruchom tracking po załadowaniu strony
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', trackEvent);
  } else {
    trackEvent();
  }
  
  // Eksportuj funkcję do manualnego trackowania konwersji
  window.trackConversion = function(orderData) {
    const sessionId = getSessionId();
    
    fetch('http://localhost:8000/api/events/conversion', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
        order_id: orderData.order_id,
        revenue: orderData.revenue,
        currency: orderData.currency || 'USD',
        email: orderData.email,
      }),
    })
    .then(response => response.json())
    .then(data => {
      console.log('✅ Conversion tracked:', data);
    })
    .catch(error => {
      console.error('❌ Conversion tracking error:', error);
    });
  };
  
})();
