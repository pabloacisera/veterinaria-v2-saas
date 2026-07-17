import { lazy, Suspense } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Navigate, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/shared/lib/AuthContext";
import { PageLoading } from "@/shared/ui/PageLoading";
import { RouteErrorBoundary } from "@/shared/ui/RouteErrorBoundary";

const Dashboard = lazy(() => import("@/pages/Dashboard"));
const DashboardHome = lazy(() => import("@/pages/DashboardHome"));
const DashboardClients = lazy(() => import("@/pages/DashboardClients"));
const DashboardPets = lazy(() => import("@/pages/DashboardPets"));
const DashboardConsultas = lazy(() => import("@/pages/DashboardConsultas"));
const DashboardInsumos = lazy(() => import("@/pages/DashboardInsumos"));
const DashboardCaja = lazy(() => import("@/pages/DashboardCaja"));
const DashboardTienda = lazy(() => import("@/pages/DashboardTienda"));
const DashboardPlanes = lazy(() => import("@/pages/DashboardPlanes"));
const DashboardChat = lazy(() => import("@/pages/DashboardChat"));
const DashboardConfiguracion = lazy(() => import("@/pages/DashboardConfiguracion"));
const DashboardComunidad = lazy(() => import("@/pages/DashboardComunidad"));
const Landing = lazy(() => import("@/pages/Landing"));
const Login = lazy(() => import("@/pages/Login"));
const Register = lazy(() => import("@/pages/Register"));
const ClienteAcceso = lazy(() => import("@/pages/ClienteAcceso"));
const ClienteInicio = lazy(() => import("@/pages/ClienteInicio"));
const AdminLoginPage = lazy(() => import("@/pages/AdminLogin"));
const AdminDashboard = lazy(() => import("@/pages/AdminDashboard"));

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 30_000 } },
});

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
    <AuthProvider>
    <BrowserRouter>
      <Suspense fallback={<PageLoading />}>
        <Routes>
          <Route path="/" element={<Landing />} errorElement={<RouteErrorBoundary />} />
          <Route path="/login" element={<Login />} errorElement={<RouteErrorBoundary />} />
          <Route path="/register" element={<Register />} errorElement={<RouteErrorBoundary />} />
          <Route path="/cliente" element={<Navigate to="/cliente/acceso" />} />
          <Route path="/cliente/acceso" element={<ClienteAcceso />} errorElement={<RouteErrorBoundary />} />
          <Route path="/cliente/inicio" element={<ClienteInicio />} errorElement={<RouteErrorBoundary />} />
          <Route path="/dashboard" element={<Dashboard />} errorElement={<RouteErrorBoundary />}>
            <Route index element={<DashboardHome />} errorElement={<RouteErrorBoundary />} />
            <Route path="clientes" element={<DashboardClients />} errorElement={<RouteErrorBoundary />} />
            <Route path="mascotas" element={<DashboardPets />} errorElement={<RouteErrorBoundary />} />
            <Route path="consultas" element={<DashboardConsultas />} errorElement={<RouteErrorBoundary />} />
            <Route path="insumos" element={<DashboardInsumos />} errorElement={<RouteErrorBoundary />} />
            <Route path="caja" element={<DashboardCaja />} errorElement={<RouteErrorBoundary />} />
            <Route path="comunidad" element={<DashboardComunidad />} errorElement={<RouteErrorBoundary />} />
            <Route path="chat" element={<DashboardChat />} errorElement={<RouteErrorBoundary />} />
            <Route path="tienda" element={<DashboardTienda />} errorElement={<RouteErrorBoundary />} />
            <Route path="planes" element={<DashboardPlanes />} errorElement={<RouteErrorBoundary />} />
            <Route path="configuracion" element={<DashboardConfiguracion />} errorElement={<RouteErrorBoundary />} />
          </Route>
          <Route path="/access_role/admin/developer" element={<AdminLoginPage />} errorElement={<RouteErrorBoundary />} />
          <Route path="/access_role/admin/developer/dashboard" element={<AdminDashboard />} errorElement={<RouteErrorBoundary />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
    </AuthProvider>
    </QueryClientProvider>
  );
}
