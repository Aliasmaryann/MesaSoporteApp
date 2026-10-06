import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListaTicketsComponent } from './lista-tickets.component';

describe('ListaTicketsComponent', () => {
  let component: ListaTicketsComponent;
  let fixture: ComponentFixture<ListaTicketsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ListaTicketsComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(ListaTicketsComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
