import { isRouteErrorResponse, useRouteError } from "react-router-dom";

export function RouteErrorBoundary() {
  const error = useRouteError();

  if (isRouteErrorResponse(error)) {
    return (
      <div className="min-h-[400px] flex items-center justify-center p-8">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 max-w-md w-full text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center">
            <span className="text-red-600 text-2xl font-bold">{error.status}</span>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            {error.statusText}
          </h2>
          <p className="text-gray-500 mb-6">
            {error.data?.message || "La página que buscás no existe o no está disponible."}
          </p>
          <a
            href="/dashboard"
            className="inline-block px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            Volver al inicio
          </a>
        </div>
      </div>
    );
  }

  const err = error as Error;
  return (
    <div className="min-h-[400px] flex items-center justify-center p-8">
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 max-w-md w-full text-center">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center">
          <span className="text-red-600 text-2xl font-bold">!</span>
        </div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Algo salió mal
        </h2>
        <p className="text-gray-500 mb-6">
          Ocurrió un error inesperado. Intentá recargar la página.
        </p>
        {err.message && (
          <details className="text-left mb-6">
            <summary className="text-sm text-gray-400 cursor-pointer hover:text-gray-600">
              Detalles técnicos
            </summary>
            <pre className="mt-2 text-xs text-red-600 bg-red-50 rounded-lg p-3 overflow-auto max-h-32">
              {err.message}
            </pre>
          </details>
        )}
        <button
          onClick={() => window.location.reload()}
          className="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
        >
          Recargar página
        </button>
      </div>
    </div>
  );
}
