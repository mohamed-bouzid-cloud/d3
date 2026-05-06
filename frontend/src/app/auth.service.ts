import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { tap } from 'rxjs/operators';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly TOKEN_KEY = 'fhir_token';
  currentUser = signal<string | null>(localStorage.getItem('user_name'));
  token = signal<string | null>(localStorage.getItem(this.TOKEN_KEY));

  constructor(private http: HttpClient) {}

  login(credentials: any): Observable<any> {
    return this.http.post('/api/token/', credentials).pipe(
      tap((res: any) => {
        localStorage.setItem(this.TOKEN_KEY, res.access);
        localStorage.setItem('user_name', credentials.username);
        this.token.set(res.access);
        this.currentUser.set(credentials.username);
      })
    );
  }

  logout() {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem('user_name');
    this.token.set(null);
    this.currentUser.set(null);
  }

  isLoggedIn(): boolean {
    return true;
  }

  getAuthorizationHeader(): { [header: string]: string | string[]; } {
    const token = this.token();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }
}
