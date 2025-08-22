import { useAuthStore } from "~/store/auth";

export default defineNuxtRouteMiddleware(async (to, from) => {
  const auth = useAuthStore();
  const { user } = storeToRefs(useAuthStore());

  function haveNotAccess(): boolean {
    if (!user.value) {
      return true;
    }
    if (user.value.is_superuser) {
      return false;
    }
    return (
      (to.path.includes("/requests") && !user.value?.useraccess?.requests) ||
      (to.path.includes("/offers") && !user.value?.useraccess?.offers)
    );
  }

  // Routes publiques qui ne nécessitent pas d'authentification
  const publicRoutes = [
    "login",
    "register",
    "auth",
    "forgot-password",
    "reset-password",
    "terms",
    "privacy",
    "evolution",
    "print",
  ];

  // Si c'est une route publique, on laisse passer
  if (publicRoutes.includes(to.name as string)) {
    return;
  }

  // Si user pas chargé, tentative de récupération
  if (!auth.user) {
    try {
      await auth.fetchUser();
      if (haveNotAccess()) {
        return auth.redirectUser();
      }
    } catch {
      try {
        await auth.refreshToken();
        if (import.meta.client) {
          try {
            await auth.fetchUser();
            if (haveNotAccess()) {
              return auth.redirectUser();
            }
          } catch (e) {
            console.warn("fetchUser failed even after refresh");
            console.log(e);
          }
        }
      } catch {
        // await auth.logout();
        if (to.name?.toString().split("-")[0] === "home") {
          return navigateTo(`/login?from=${to.path}`);
        }
      }
    }
  } else {
    if (haveNotAccess()) {
      return auth.redirectUser();
    }
  }
});
