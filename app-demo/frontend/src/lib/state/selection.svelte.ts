import type { PropertyData } from '$lib/types';

class SelectionState {
    value = $state<PropertyData | null>(null);

    set(data: PropertyData | null) {
        this.value = data;
    }
    
    reset() {
        this.value = null;
    }
}

export const selectedProperty = new SelectionState();