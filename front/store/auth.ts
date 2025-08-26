// stores/auth.ts
import { defineStore } from "pinia";
import type { LoginResponse, User } from "~/types";
import { useRequestHeaders } from "nuxt/app";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null as null | User,
  }),

  actions: {
    setUser(user: User) {
      this.user = user;
    },
    clearUser() {
      this.user = null;
    },
    async loginUser(credentials: any): Promise<LoginResponse> {
      try {
        const res = await $fetch("/api/auth/login/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: credentials,
          credentials: "include",
        });
        this.user = res as User;
        return { success: true, message: "Connecté avec succès" };
      } catch (err: any) {
        let errorMessage = "Identifiants de connexion invalides.";
        if (err.response) {
          const status = err.response.status;
          if (status >= 500) {
            errorMessage = "Erreur du serveur, réessayez plus tard.";
          } else if (status === 400) {
            errorMessage = "Identifiants de connexion invalides.";
          }
        } else if (err.message) {
          errorMessage = "Problème de connexion au serveur.";
        }
        return { success: false, message: errorMessage };
      }
    },
    async fetchUser() {
      try {
        const headers = useRequestHeaders(["cookie"]);
        const data = await $fetch("/api/users/me/", {
          credentials: "include",
          headers,
        });
        if (data) this.setUser(data as User);
      } catch {
        this.clearUser();
        throw new Error("User fetch failed");
      }
    },
    async refreshToken() {
      try {
        const headers = useRequestHeaders(["cookie"]);
        await $fetch("/api/auth/token/refresh/", {
          method: "POST",
          credentials: "include",
          headers,
        });
      } catch {
        this.clearUser();
        throw new Error("Refresh failed");
      }
    },
    async logout() {
      await $fetch("/api/auth/logout/", {
        method: "POST",
        credentials: "include",
      });
      this.clearUser();
    },
    redirectUser(): string {
      const user = this.user;
      if (user) {
        if (user.is_superuser) {
          return "/home";
        }
        if (user.is_staff) {
          if (user.useraccess?.installation) {
            return "/home/installations";
          }
          if (user.useraccess?.offers) {
            return "/home/offers";
          }
          if (user.useraccess?.requests) {
            return "/home/requests";
          }
          // if (user.useraccess?.administrative_procedures) {
          //   return "/home/administrative_procedures";
          // }
          return "/home/settings/account";
        }
        return "/home/installations";
      }
      return "/login";
    },
  },
});
