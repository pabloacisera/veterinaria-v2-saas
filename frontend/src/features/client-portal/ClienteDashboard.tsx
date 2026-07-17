import { useEffect, useState } from "react";
import { ClienteMascotas } from "./ClienteMascotas";
import { ClienteFacturas } from "./ClienteFacturas";
import { ClientePrescripciones } from "./ClientePrescripciones";
import type { Factura, Prescripcion } from "@/entities/client-portal";
import { fetchMisMascotas, fetchFacturas, fetchPrescripciones } from "./api";

export function ClienteDashboard() {
  const [pets, setPets] = useState<any[]>([]);
  const [facturas, setFacturas] = useState<Factura[]>([]);
  const [prescripciones, setPrescripciones] = useState<Prescripcion[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [petsData, facturasData, prescripcionesData] = await Promise.all([
          fetchMisMascotas(),
          fetchFacturas(),
          fetchPrescripciones(),
        ]);
        setPets(petsData);
        setFacturas(facturasData);
        setPrescripciones(prescripcionesData);
      } catch {
        // error handled silently
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="space-y-8">
      <section>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Mis Mascotas</h2>
        <ClienteMascotas pets={pets} loading={loading} />
      </section>

      <section>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Facturas</h2>
        <ClienteFacturas facturas={facturas} loading={loading} />
      </section>

      <section>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Prescripciones</h2>
        <ClientePrescripciones prescripciones={prescripciones} loading={loading} />
      </section>
    </div>
  );
}
