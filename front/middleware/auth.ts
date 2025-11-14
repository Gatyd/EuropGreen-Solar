import { useAuthStore } from "~/store/auth";

export default defineNuxtRouteMiddleware(async (to, from) => {
  const auth = useAuthStore();

  // Routes d'authentification (où ce middleware ne doit pas interférer)
  const authRoutes = [
    "login",
    "forgot-password",
    "reset-password",
  ];
  
  // Si on vient d'une route d'authentification, on n'interfère pas
  if (from.name && authRoutes.includes(from.name as string)) {
    console.log("Coming from auth route, skipping auth middleware.");
    return;
  }

  // Si user pas chargé, tentative de récupération
  if (!auth.user) {
    try {
      await auth.fetchUser();
      return navigateTo(from.query.from ? from.query.from as string : auth.redirectUser());
    } catch {
      try {
        await auth.refreshToken();
        if (import.meta.client) {
          try {
            await auth.fetchUser();
            return navigateTo(auth.redirectUser());
          } catch (e) {
            console.warn("fetchUser failed even after refresh");
            console.log(e);
          }
        }
      } catch {
        // await auth.logout();
        return;
      }
    }
  } else {
    return navigateTo(from.query.from ? from.query.from as string : auth.redirectUser());
  }
});
