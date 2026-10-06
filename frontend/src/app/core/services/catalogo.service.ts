import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, shareReplay } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Catalogos } from '../models/catalogos';

@Injectable({ providedIn: 'root' })
export class CatalogoService {
  private http = inject(HttpClient);

  // Los catálogos casi no cambian: se piden una vez y se reutilizan.
  readonly catalogos$: Observable<Catalogos> = this.http
    .get<Catalogos>(`${environment.apiUrl}/catalogos`)
    .pipe(shareReplay(1));
}