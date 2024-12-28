import { defineStore } from "pinia";
import { ref } from "vue";
import { API_ENDPOINTS } from "@/utils/apiEndpoints";

export const useFraudStore = defineStore({
  id: "fraudStore",

  state: () => ({
    fraudScore: null as number | null,
    loading: false,
    error: null as string | null,
  }),

  actions: {
    async checkFraud(acquisitionId: number) {
      this.loading = true;
      this.error = null;
      const baseUrl = import.meta.env.VITE_API_ENDPOINT;
      try {
        const response = await fetch(
          `${baseUrl}/acquisitions/${acquisitionId}/fraud_score`
        );

        if (!response.ok) {
          throw new Error(`Failed to fetch fraud score: ${response.status}`);
        }

        const data = await response.json();
        this.fraudScore = data?.fraud_score ?? null;

      } catch (err: unknown) {
        this.error = err instanceof Error ? err.message : "Unknown error";
        console.error("Error fetching fraud score:", this.error);
      } finally {
        this.loading = false;
      }
    },
  },

  getters: {},
});
