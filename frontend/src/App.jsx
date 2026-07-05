import { useEffect, useState } from "react";
import { api } from "./api/client.js";
import Navbar from "./components/Navbar.jsx";
import CostForm from "./forms/CostForm.jsx";
import RouteForm from "./forms/RouteForm.jsx";
import TripForm from "./forms/TripForm.jsx";
import HomePage from "./pages/HomePage.jsx";
import RouteDetail from "./pages/RouteDetail.jsx";

export default function App() {
  const [page, setPage] = useState({ name: "home" });
  const [routes, setRoutes] = useState([]);
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function loadRoutes() {
    setLoading(true);
    setError("");
    try {
      const data = await api.get("/api/rutas");
      setRoutes(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function loadRoute(routeId) {
    setError("");
    const data = await api.get(`/api/rutas/${routeId}`);
    setSelectedRoute(data);
    return data;
  }

  function goHome() {
    setPage({ name: "home" });
    setSelectedRoute(null);
    loadRoutes();
  }

  async function goDetail(routeId) {
    try {
      const data = await loadRoute(routeId);
      setPage({ name: "detail", routeId: data.id });
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDeleteRoute(routeId) {
    if (!window.confirm("Estas seguro?")) return;
    try {
      await api.delete(`/api/rutas/${routeId}`);
      setMessage("Ruta eliminada.");
      goHome();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDeleteTrip(tripId, routeId) {
    if (!window.confirm("Eliminar este registro y sus costos?")) return;
    try {
      await api.delete(`/api/viajes/${tripId}`);
      setMessage("Registro eliminado.");
      await loadRoute(routeId);
      await loadRoutes();
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    loadRoutes();
  }, []);

  return (
    <>
      <Navbar onNavigate={setPage} />

      {page.name === "home" && (
        <HomePage
          routes={routes}
          loading={loading}
          onDetail={goDetail}
          onEdit={(route) => setPage({ name: "route-form", route })}
          onDelete={handleDeleteRoute}
        />
      )}

      {page.name === "route-form" && (
        <RouteForm
          route={page.route}
          nextId={routes.length + 1}
          onCancel={goHome}
          onSaved={async (route) => {
            setMessage(page.route ? "Ruta actualizada." : "Ruta guardada.");
            setRoutes((currentRoutes) => {
              const routeForList = {
                ...route,
                rentabilidad_estimada: route.rentabilidad_estimada || null,
              };
              if (page.route) {
                return currentRoutes.map((item) => item.id === route.id ? routeForList : item);
              }
              return [routeForList, ...currentRoutes];
            });
            setPage({ name: "home" });
            setSelectedRoute(null);
            setLoading(false);
            loadRoutes();
          }}
        />
      )}

      {page.name === "detail" && selectedRoute && (
        <RouteDetail
          route={selectedRoute}
          onBack={goHome}
          onNewTrip={() => setPage({ name: "trip-form", route: selectedRoute })}
          onCosts={(trip) => setPage({ name: "cost-form", route: selectedRoute, trip })}
          onDeleteTrip={handleDeleteTrip}
        />
      )}

      {page.name === "trip-form" && (
        <TripForm
          route={page.route}
          onCancel={() => goDetail(page.route.id)}
          onSaved={async (routeId) => {
            setMessage("Registro semanal guardado.");
            await goDetail(routeId);
            loadRoutes();
          }}
        />
      )}

      {page.name === "cost-form" && (
        <CostForm
          route={page.route}
          trip={page.trip}
          onCancel={() => goDetail(page.route.id)}
          onSaved={async () => {
            setMessage("Costos guardados.");
            await goDetail(page.route.id);
            loadRoutes();
          }}
        />
      )}
    </>
  );
}
