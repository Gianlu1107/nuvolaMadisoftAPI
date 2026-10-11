import axios, { AxiosInstance } from 'axios';
import * as fs from 'fs';

interface NuvolaSession {
  token?: string;
  refreshToken?: string;
  expires_at?: number;
}

export class NuvolaClient {
  private baseURL = 'https://nuvola.madisoft.it/api-studente/v1';
  private sessionPath: string;
  private session: NuvolaSession = {};
  private http: AxiosInstance;

  constructor(sessionPath = './nuvola_session.json') {
    this.sessionPath = sessionPath;
    this.http = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Accept': 'application/json',
        'User-Agent': 'okhttp/4.9.2'
      }
    });
    this.loadSession();
  }

  private loadSession() {
    if (fs.existsSync(this.sessionPath)) {
      try {
        this.session = JSON.parse(fs.readFileSync(this.sessionPath, 'utf8'));
      } catch (err) {
        this.session = {};
      }
    }
  }

  private saveSession() {
    fs.writeFileSync(this.sessionPath, JSON.stringify(this.session, null, 2), 'utf8');
  }

  async login(username: string, password: string): Promise<void> {
    const res = await this.http.post('/login', { username, password });
    const now = Math.floor(Date.now() / 1000);
    this.session = {
      token: res.data.token,
      refreshToken: res.data.refreshToken,
      expires_at: now + 1740 // 29 minuti
    };
    this.saveSession();
  }

  async refresh(): Promise<boolean> {
    if (!this.session.refreshToken) return false;
    try {
      // NOTA CRITICA: il body richiede "refresh_token" in snake_case!
      const res = await this.http.post('/refresh-token', {
        refresh_token: this.session.refreshToken
      });
      const now = Math.floor(Date.now() / 1000);
      this.session.token = res.data.token;
      if (res.data.refreshToken) {
        this.session.refreshToken = res.data.refreshToken;
      }
      this.session.expires_at = now + 1740;
      this.saveSession();
      return true;
    } catch {
      return false;
    }
  }

  async getToken(): Promise<string> {
    const now = Math.floor(Date.now() / 1000);
    if (this.session.token && this.session.expires_at && now < (this.session.expires_at - 60)) {
      return this.session.token;
    }
    const success = await this.refresh();
    if (!success || !this.session.token) {
      throw new Error('Autenticazione richiesta');
    }
    return this.session.token;
  }

  async getAlunni() {
    const token = await this.getToken();
    const res = await this.http.get('/alunni', {
      headers: { Authorization: `Bearer ${token}` }
    });
    return res.data.valori;
  }

  async getCompiti(alunnoId: number, dataDDMMYYYY: string) {
    const token = await this.getToken();
    const res = await this.http.get(`/alunno/${alunnoId}/compito/elenco/${dataDDMMYYYY}`, {
      params: { contextAlunno: alunnoId },
      headers: { Authorization: `Bearer ${token}` }
    });
    return res.data.valori;
  }
}
