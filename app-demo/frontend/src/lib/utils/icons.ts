// Mappa delle categorie a icone generiche di fallback
const CATEGORY_ICONS: Record<string, string> = {
    'Generale': 'fa-circle-info',
    'Fitness & Wellness': 'fa-dumbbell',
    'Food & Dining': 'fa-utensils',
    'Outdoor': 'fa-tree',
    'Services': 'fa-bell-concierge',
    'Comfort': 'fa-couch',
    'Entertainment': 'fa-tv',
    'Bathroom': 'fa-shower',
    'Security': 'fa-shield-halved',
    'View & Space': 'fa-panorama'
};

// stiamo considerando font-awesome

export function getAmenityIcon(amenityName: string, category: string = '', type: 'property' | 'room' = 'property'): string {
    const name = amenityName.toLowerCase();
    
    // MARCH NOME

    // Property specific
    if (name.includes('wifi') || name.includes('internet')) return 'fa-wifi';
    if (name.includes('pool') || name.includes('piscina')) return 'fa-swimming-pool';
    if (name.includes('parking') || name.includes('parcheggio') || name.includes('auto')) return 'fa-square-parking';
    if (name.includes('gym') || name.includes('palestra') || name.includes('fitness')) return 'fa-dumbbell';
    if (name.includes('spa') || name.includes('wellness') || name.includes('sauna') || name.includes('massage')) return 'fa-spa';
    if (name.includes('restaurant') || name.includes('ristorante') || name.includes('cena')) return 'fa-utensils';
    if (name.includes('bar') || name.includes('drink') || name.includes('cocktail')) return 'fa-martini-glass-citrus';
    if (name.includes('beach') || name.includes('spiaggia') || name.includes('mare')) return 'fa-umbrella-beach';
    if (name.includes('pet') || name.includes('animali') || name.includes('cane') || name.includes('gatto')) return 'fa-paw';
    if (name.includes('reception') || name.includes('concierge')) return 'fa-bell-concierge';
    if (name.includes('colazione') || name.includes('breakfast')) return 'fa-mug-hot';
    if (name.includes('laundry') || name.includes('lavanderia')) return 'fa-shirt';

    // Room specific
    if (name.includes('air') || name.includes('aria') || name.includes('ac')) return 'fa-wind';
    if (name.includes('tv') || name.includes('television') || name.includes('netflix')) return 'fa-tv';
    if (name.includes('hair') || name.includes('asciuga') || name.includes('phon')) return 'fa-wind'; // o fa-soap
    if (name.includes('minibar') || name.includes('fridge') || name.includes('frigo')) return 'fa-wine-bottle';
    if (name.includes('safe') || name.includes('cassa') || name.includes('sicurezza')) return 'fa-lock';
    if (name.includes('balcony') || name.includes('balcone') || name.includes('terrazza')) return 'fa-person-through-window';
    if (name.includes('view') || name.includes('vista')) return 'fa-mountain-sun';
    if (name.includes('coffee') || name.includes('caffè') || name.includes('tea')) return 'fa-mug-saucer';

    // 2. FALLBACK SULLA CATEGORIA (Se il nome non matcha nessuna icona)
    if (category && CATEGORY_ICONS[category]) {
        return CATEGORY_ICONS[category];
    }

    // 3. DEFAULT TOTALE
    return 'fa-circle-check'; 
}