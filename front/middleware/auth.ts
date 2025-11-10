import { useAuthStore } from "~/store/auth";

export default defineNuxtRouteMiddleware(async (to, from) => {
  const auth = useAuthStore();

  // Routes publiques (où ce middleware ne doit pas rediriger)
  const publicRoutes = [
    "login",
    "forgot-password",
    "reset-password",
  ];
  
  // Si on vient d'une route publique, on n'interfère pas
  if (from.name && publicRoutes.includes(from.name as string)) {
    return;
  }

  // Si user pas chargé, tentative de récupération
  if (!auth.user) {
    try {
      await auth.fetchUser();
      return navigateTo('/home');
    } catch {
      try {
        await auth.refreshToken();
        if (import.meta.client) {
          try {
            await auth.fetchUser();
            auth.redirectUser();
          } catch (e) {
            console.warn("fetchUser failed even after refresh");
            console.log(e);
          }
        }
      } catch {
        return;
      }
    }
  } else {
    auth.redirectUser();
  }
});
