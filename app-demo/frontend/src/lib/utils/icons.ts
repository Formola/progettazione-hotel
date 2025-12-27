/**
 * Utility functions per mappare amenities a icone Font Awesome
 * Solo le amenities più importanti e comuni
 */

// ==========================================
// PROPERTY AMENITIES (Hotel/Struttura)
// ==========================================

export function getPropertyAmenityIcon(amenityName: string): string {
    const name = amenityName.toLowerCase();
    
    // 1. WiFi
    if (name.includes('wifi') || name.includes('internet')) 
        return 'fa-wifi';
    
    // 2. Piscina
    if (name.includes('pool') || name.includes('piscina')) 
        return 'fa-swimming-pool';
    
    // 3. Parcheggio
    if (name.includes('parking') || name.includes('parcheggio')) 
        return 'fa-square-parking';
    
    // 4. Palestra
    if (name.includes('gym') || name.includes('palestra') || name.includes('fitness')) 
        return 'fa-dumbbell';
    
    // 5. Spa
    if (name.includes('spa') || name.includes('wellness')) 
        return 'fa-spa';
    
    // 6. Ristorante
    if (name.includes('restaurant') || name.includes('ristorante')) 
        return 'fa-utensils';
    
    // 7. Bar
    if (name.includes('bar') || name.includes('lounge')) 
        return 'fa-martini-glass-citrus';
    
    // 8. Spiaggia
    if (name.includes('beach') || name.includes('spiaggia')) 
        return 'fa-umbrella-beach';
    
    // 9. Animali ammessi
    if (name.includes('pet') || name.includes('animali')) 
        return 'fa-paw';
    
    // 10. Reception 24h
    if (name.includes('reception') || name.includes('24') || name.includes('concierge')) 
        return 'fa-clock';
    
    return 'fa-circle-check'; // Icona default
}


// ==========================================
// ROOM AMENITIES (Camera/Stanza)
// ==========================================

export function getRoomAmenityIcon(amenityName: string): string {
    const name = amenityName.toLowerCase();
    
    // 1. Aria Condizionata
    if (name.includes('air') || name.includes('conditioning') || name.includes('aria')) 
        return 'fa-wind';
    
    // 2. TV
    if (name.includes('tv') || name.includes('television')) 
        return 'fa-tv';
    
    // 3. Asciugacapelli
    if (name.includes('hairdryer') || name.includes('asciugacapelli') || name.includes('phon')) 
        return 'fa-shower'; // Icona più generica per bagno
    
    // 4. Minibar
    if (name.includes('minibar') || name.includes('mini bar') || name.includes('fridge')) 
    return 'fa-wine-bottle';
    
    // 5. Cassaforte
    if (name.includes('safe') || name.includes('cassaforte')) 
        return 'fa-lock';
    
    // 6. Balcone/Vista
    if (name.includes('balcony') || name.includes('balcone') || name.includes('view') || name.includes('vista')) 
        return 'fa-house-flag';
    
    return 'fa-circle-check'; // Icona default
}


// ==========================================
// HELPER: Determina automaticamente il tipo
// ==========================================

export function getAmenityIcon(amenityName: string, type: 'property' | 'room' = 'property'): string {
    return type === 'property' 
        ? getPropertyAmenityIcon(amenityName)
        : getRoomAmenityIcon(amenityName);
}

// const iconClass = getAmenityIcon('WiFi', 'property'); // Restituisce 'fa-wifi'
