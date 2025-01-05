import { defineStore } from "pinia";
import { ref } from "vue";
import { API_ENDPOINTS } from "@/utils/apiEndpoints";
import { useToast } from "vue-toastification";

const toast = useToast();

export const useFraudStore = defineStore({
  id: "fraudStore",

  state: () => ({
    fraudScore: null as number | null,
    fraudScorePerItem: {} as Record<string, number>,
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
          `${baseUrl}/acquisitions/${acquisitionId}/fraud_score`,
        );

        if (!response.ok) {
          if (response.status === 404) {
            this.error = "Tranzacția nu a fost găsită în baza de date.";
          } else if (response.status === 500) {
            this.error =
              "Eroare internă a serverului. Te rugăm să încerci din nou.";
          } else {
            this.error = `Eroare necunoscută: ${response.status}`;
          }
          throw new Error(this.error); // Aruncă eroarea pentru a opri fluxul
        }

        const data = await response.json();
        this.fraudScore = data.result.fraud_score ?? null;
        this.fraudScorePerItem = data.result.fraud_score_per_item ?? {};

        chrome.storage.local.set(
          { [`fraud_${acquisitionId}`]: data.result },
          () => {
            console.log("Datele au fost salvate în cache.");
          },
        );
      } catch (err: unknown) {
        console.error("Error fetching fraud score:", err);
        this.error = this.error ?? "Eroare necunoscută la încărcarea scorului.";
      } finally {
        this.loading = false;
      }
    },
  },

  getters: {},
});
