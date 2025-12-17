import { writable } from 'svelte/store';
import type { PropertyData } from '$lib/types';

// Store che contiene la proprietà selezionata per il dettaglio
export const selectedProperty = writable<PropertyData | null>(null);