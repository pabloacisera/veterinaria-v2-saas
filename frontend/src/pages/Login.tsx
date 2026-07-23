import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Card } from "@/shared/ui/Card";
import { PageLoading } from "@/shared/ui/PageLoading";
import { LoginForm } from "@/features/auth/LoginForm";
import { useAuth } from "@/shared/lib/AuthContext";
import { fetchCurrentUser } from "@/features/auth/api";

export function Login() {
  const navigate = useNavigate();
  const { login, isAuthenticated } = useAuth();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(false);
  const activated = searchParams.get("activated") === "true";
  const googleSuccess = searchParams.get("google") === "success";

  useEffect(() => {
    let extractedToken: string | null = null;
    const hash = window.location.hash;
    if (hash && hash.includes("access_token=")) {
      const params = new URLSearchParams(hash.substring(1));
      extractedToken = params.get("access_token");
      if (extractedToken) {
        localStorage.setItem("access_token", extractedToken);
        window.history.replaceState({}, "", window.location.pathname + window.location.search);
      }
    }

    if (googleSuccess && extractedToken) {
      setLoading(true);
      fetchCurrentUser()
        .then((userData) => {
          login(extractedToken, { email: userData.email, name: userData.name });
          navigate("/dashboard", { replace: true });
        })
        .catch(() => setLoading(false));
    }
  }, []);

  async function handleSuccess(token: string) {
    try {
      const userData = await fetchCurrentUser();
      login(token, { email: userData.email, name: userData.name });
    } catch {
      // /auth/me may fail; dashboard guard will redirect if unauthenticated
    }
    navigate("/dashboard");
  }

  if (loading) return <PageLoading />;

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-gray-50">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <button
            onClick={() => navigate("/")}
            className="text-2xl font-bold text-primary-600"
          >
            Veter
          </button>
        </div>

        {activated && (
          <div className="mb-6 rounded-lg bg-green-50 border border-green-200 p-3 text-sm text-green-700 text-center">
            Cuenta activada correctamente. Ya podés iniciar sesión.
          </div>
        )}

        <Card>
          <h1 className="text-xl font-bold text-gray-900 mb-6">
            Iniciar sesión
          </h1>
          <LoginForm onSuccess={handleSuccess} />
        </Card>
      </div>
    </div>
  );
}

export default Login;
