export const ssr = false;
export const prerender = false;

import type { PageLoad } from './$types';

export const load: PageLoad = () => {
    // Verifichiamo di essere nel browser e che i dati esistano nello stato
    if (typeof window !== 'undefined' && window.history.state?.property) {
        return {
            property: window.history.state.property
        };
    }
    
    // Se l'utente ricarica la pagina o il dato non c'è
    return {
        property: null
    };
};