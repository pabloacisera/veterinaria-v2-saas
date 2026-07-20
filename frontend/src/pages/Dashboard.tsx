import { useEffect, useState } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { DashboardLayout } from "@/widgets/DashboardLayout";
import { OnboardingWizard } from "@/features/onboarding/OnboardingWizard";
import { fetchClients } from "@/features/clients/api";
import { useAuth } from "@/shared/lib/AuthContext";

export function Dashboard() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }

    const onboardingDone = localStorage.getItem("onboarding_done") === "true";
    if (onboardingDone) {
      setChecking(false);
      return;
    }

    fetchClients({ limit: 1 })
      .then((clients) => {
        if (!Array.isArray(clients) || clients.length === 0) {
          setShowOnboarding(true);
        }
        setChecking(false);
      })
      .catch(() => {
        setChecking(false);
      });
  }, [isAuthenticated, navigate]);

  if (checking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <p className="text-gray-500">Cargando...</p>
      </div>
    );
  }

  if (showOnboarding) {
    return (
      <OnboardingWizard
        onComplete={() => {
          setShowOnboarding(false);
        }}
      />
    );
  }

  return (
    <DashboardLayout title="">
      <Outlet />
    </DashboardLayout>
  );
}

export default Dashboard;
