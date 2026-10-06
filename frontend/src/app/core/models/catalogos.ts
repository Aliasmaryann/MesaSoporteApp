export interface ItemCatalogo {
  id: number;
  nombre: string;
}

export interface Usuario extends ItemCatalogo {
  correo: string;
}

export interface Catalogos {
  solicitantes: Usuario[];
  responsables: Usuario[];
  categorias: ItemCatalogo[];
  prioridades: ItemCatalogo[];
  estados: ItemCatalogo[];
}