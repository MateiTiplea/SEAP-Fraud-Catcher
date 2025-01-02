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
  
      // Verifică cache-ul din chrome.storage.local
      chrome.storage.local.get(`fraud_${acquisitionId}`, async (cachedData) => {
        if (cachedData[`fraud_${acquisitionId}`]) {
          console.log("Date recuperate din cache:", cachedData[`fraud_${acquisitionId}`]);
          const data = cachedData[`fraud_${acquisitionId}`];
          this.fraudScore = data.fraud_score ?? null;
          this.fraudScorePerItem = data.fraud_score_per_item ?? {};
          this.loading = false;
          return;
        }
  
        // Dacă nu există în cache, fă cererea către API
        const baseUrl = import.meta.env.VITE_API_ENDPOINT;
        try {
          const response = await fetch(
            `${baseUrl}/acquisitions/${acquisitionId}/fraud_score`
          );
  
          if (!response.ok) {
            toast.error("Eroare la încărcare scor fraudă");
            throw new Error(`Failed to fetch fraud score: ${response.status}`);
          }
  
          const data = await response.json();
          this.fraudScore = data.result.fraud_score ?? null;
          this.fraudScorePerItem = data.result.fraud_score_per_item ?? {};
  
          // Salvează datele în cache
          chrome.storage.local.set({ [`fraud_${acquisitionId}`]: data.result }, () => {
            console.log("Datele au fost salvate în cache.");
          });
  
        } catch (err: unknown) {
          toast.error("Eroare la încărcare scor fraudă");
          this.error = err instanceof Error ? err.message : "Unknown error";
          console.error("Error fetching fraud score:", this.error);
        } finally {
          this.loading = false;
        }
      });
    },
  },
  
  getters: {},
});
