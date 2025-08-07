import { useAuthStore } from "~/store/auth";

export default defineNuxtRouteMiddleware(async (to, from) => {
  const auth = useAuthStore();
  if (auth.user && !auth.user.is_superuser) {
    return navigateTo(auth.redirectUser());
  }
});
