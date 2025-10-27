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
    if (!user.value.is_staff && to.path.includes("/installations")) {
      return false;
    }
    return (
      (to.path.includes("/requests") && !user.value?.useraccess?.requests) ||
      (to.path.includes("/offers") && !user.value?.useraccess?.offers) ||
      (to.path.includes("/installations") && !user.value?.useraccess?.installation)
    );
  }

  // Routes publiques qui ne nécessitent pas d'authentification
  const publicRoutes = [
    "login",
    "forgot-password",
    "reset-password",
    "print",
    "offers"
  ];

  // Si c'est une route publique, on laisse passer
  if (to.name && publicRoutes.includes((to.name as string).split("-")[0])) {
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
