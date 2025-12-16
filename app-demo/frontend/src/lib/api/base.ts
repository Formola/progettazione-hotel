const BASE_URL = 'http://localhost:8000';

export class BaseApi {
    protected async request<T>(endpoint: string, method: string = 'GET', body?: any): Promise<T> {
        const headers: HeadersInit = {
            'Content-Type': 'application/json'
        };

        const response = await fetch(`${BASE_URL}${endpoint}`, {
            method,
            headers,
            body: body ? JSON.stringify(body) : undefined,
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }
        return response.json();
    }
}