import { useAuthStore } from "~/store/auth";

export default async function apiRequest<T>(requestFn: () => Promise<T>, toast: any): Promise<T | null> {
    try {
      return await requestFn();
    } catch (err: any) {
      if (err.response && err.response.status === 401) {
        try {
          const auth = useAuthStore();
          await auth.refreshToken();
          return await requestFn();
        } catch (refreshError) {
          console.error("Échec du rafraîchissement du token", refreshError);
          navigateTo("/login");
        }
      } else {
        catchErrors(err, toast);
      }
    }
    return null;
}