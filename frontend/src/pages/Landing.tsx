import { useNavigate } from "react-router-dom";
import { Button } from "@/shared/ui/Button";

export function Landing() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col">
      <header className="px-6 py-4 border-b border-gray-100">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <span className="text-xl font-bold text-primary-600">Veter</span>
          <div className="flex items-center gap-3">
            <Button variant="ghost" onClick={() => navigate("/login")}>
              Iniciar sesión
            </Button>
            <Button onClick={() => navigate("/register")}>
              Registrarse
            </Button>
          </div>
        </div>
      </header>

      <main className="flex-1">
        <section className="px-6 pt-20 pb-16 md:pt-32 md:pb-24">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-gray-900 leading-tight">
              Gestioná tu veterinaria
              <span className="text-primary-600"> de forma inteligente</span>
            </h1>
            <p className="mt-6 text-lg md:text-xl text-gray-500 max-w-2xl mx-auto leading-relaxed">
              Facturación, historial clínico, stock, caja y un agente de IA
              que conoce todos tus datos — en un solo lugar.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button size="lg" onClick={() => navigate("/register")}>
                Comenzar gratis
              </Button>
              <Button
                variant="outline"
                size="lg"
                onClick={() => navigate("/login")}
              >
                Ya tengo cuenta
              </Button>
            </div>
          </div>
        </section>

        <section className="px-6 py-16 bg-gray-50">
          <div className="max-w-5xl mx-auto">
            <h2 className="text-2xl md:text-3xl font-bold text-center text-gray-900">
              Todo lo que necesitás
            </h2>
            <div className="mt-12 grid gap-6 md:grid-cols-3">
              {[
                {
                  title: "Clientes y Mascotas",
                  desc: "Fichas completas, historial clínico, búsqueda instantánea y soft-delete.",
                },
                {
                  title: "Consultas y Facturación",
                  desc: "Wizard multi-step con borrador automático, prescripción y factura electrónica.",
                },
                {
                  title: "Stock y Caja",
                  desc: "Control de insumos, movimientos de caja, venta directa desde la tienda.",
                },
              ].map((feature) => (
                <div
                  key={feature.title}
                  className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm"
                >
                  <h3 className="text-lg font-semibold text-gray-900">
                    {feature.title}
                  </h3>
                  <p className="mt-2 text-gray-500 text-sm leading-relaxed">
                    {feature.desc}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="px-6 py-16">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-2xl md:text-3xl font-bold text-gray-900">
              ¿Listo para empezar?
            </h2>
            <p className="mt-4 text-gray-500">
              Creá tu cuenta en segundos y empezá a gestionar tu veterinaria.
            </p>
            <div className="mt-8">
              <Button size="lg" onClick={() => navigate("/register")}>
                Crear cuenta gratis
              </Button>
            </div>
          </div>
        </section>
      </main>

      <footer className="px-6 py-6 border-t border-gray-100">
        <div className="max-w-6xl mx-auto text-center text-sm text-gray-400">
          &copy; {new Date().getFullYear()} Veter. Todos los derechos reservados.
        </div>
      </footer>
    </div>
  );
}

export default Landing;
