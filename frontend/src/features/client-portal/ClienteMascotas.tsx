import { Card } from "@/shared/ui/Card";

interface Pet {
  id: string;
  name: string;
  species: string | null;
  breed: string | null;
  sex: string;
  photo_urls: string[];
}

interface Props {
  pets: Pet[];
  loading: boolean;
}

export function ClienteMascotas({ pets, loading }: Props) {
  if (loading) {
    return <p className="text-gray-500">Cargando mascotas...</p>;
  }

  if (pets.length === 0) {
    return <p className="text-gray-500">No hay mascotas registradas.</p>;
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {pets.map((pet) => (
        <Card key={pet.id} className="p-4">
          <h3 className="font-semibold text-gray-900">{pet.name}</h3>
          {pet.species && <p className="text-sm text-gray-500">Especie: {pet.species}</p>}
          {pet.breed && <p className="text-sm text-gray-500">Raza: {pet.breed}</p>}
          <p className="text-sm text-gray-500">
            Sexo: {pet.sex === "male" ? "Macho" : pet.sex === "female" ? "Hembra" : pet.sex}
          </p>
        </Card>
      ))}
    </div>
  );
}
