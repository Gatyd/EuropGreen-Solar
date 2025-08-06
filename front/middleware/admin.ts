import { useAuthStore } from "~/store/auth";

export default defineNuxtRouteMiddleware(async (to, from) => {
  const auth = useAuthStore();

  return navigateTo(
    auth.user && !auth.user.is_superuser
      ? auth.redirectUser()
      : `/login?from=${to.path}`
  );
});
