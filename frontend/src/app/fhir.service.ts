import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class FhirService {
  constructor(private http: HttpClient, private auth: AuthService) {}

  // Generic CRUD
  getResources<T>(type: string): Observable<T[]> {
    return this.http.get<T[]>(`/api/${type}/`, { headers: this.auth.getAuthorizationHeader() });
  }

  getResourceById<T>(type: string, id: string): Observable<T> {
    return this.http.get<T>(`/api/${type}/${id}/`, { headers: this.auth.getAuthorizationHeader() });
  }

  createResource<T>(type: string, resource: any): Observable<T> {
    return this.http.post<T>(`/api/${type}/`, resource, { headers: this.auth.getAuthorizationHeader() });
  }

  updateResource<T>(type: string, id: string, resource: any): Observable<T> {
    return this.http.put<T>(`/api/${type}/${id}/`, resource, { headers: this.auth.getAuthorizationHeader() });
  }

  deleteResource(type: string, id: string): Observable<void> {
    return this.http.delete<void>(`/api/${type}/${id}/`, { headers: this.auth.getAuthorizationHeader() });
  }

  // Nested actions
  getPatientObservations(patientId: string): Observable<any[]> {
    return this.http.get<any[]>(`/api/patients/${patientId}/observations/`, { headers: this.auth.getAuthorizationHeader() });
  }

  getPractitionerEncounters(practitionerId: string): Observable<any[]> {
    return this.http.get<any[]>(`/api/practitioners/${practitionerId}/encounters/`, { headers: this.auth.getAuthorizationHeader() });
  }
}
