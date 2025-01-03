<template>
  <MainLayout>
    <!-- Afișează detalii tranzacție sau turometrul în funcție de stare -->
    <div v-if="!isFraudCheckActive" class="items-left m-4 flex flex-col justify-between bg-white p-2 px-5 font-mono">
      <div id="data-container">
        <div class="achizitie">
          <div class="ofertant mb-4">
            <h2><span class="font-semibold text-[#1AC2FF]">Ofertant: </span><span>{{ data.numeOfertant }}</span></h2>
            <p><span class="font-semibold text-[#1AC2FF]">CIF: </span><span>{{ data.cifOfertant }}</span></p>
          </div>

          <div class="autoritate-contractanta mb-4">
            <h2><span class="font-semibold text-[#1AC2FF]">Autoritate Contractanta: </span>
              <span>{{ data.numeAutoritate }}</span>
            </h2>
            <p><span class="font-semibold text-[#1AC2FF]">CIF: </span><span>{{ data.cifAutoritate }}</span></p>
          </div>

          <div class="detalii-achizitie">
            <h2><span class="font-semibold text-[#1AC2FF]">Denumire Achizitie: </span>
              <span>{{ data.denumireAchizitie }}</span>
            </h2>
            <p><span class="font-semibold text-[#1AC2FF]">Descriere: </span><span>{{ data.descriereAchizitie }}</span></p>
            <p><span class="font-semibold text-[#1AC2FF]">Valoare Estimata: </span><span>{{ data.valoareEstimata }}</span></p>
          </div>
        </div>
      </div>
      <div class="p-4m flex flex-col items-center justify-between bg-white px-5 font-mono">
        <Button :loading="isLoading" @click="startFraudCheck">
          Este Frauda?
        </Button>
      </div>
    </div>

    <!-- Afișează turometrul -->
    <div v-else class="items-center flex flex-col justify-center bg-white p-4">
      <FraudMeter :score="fraudStore.fraudScore ?? 0" />
      <Button @click="goBack" class="mt-4">
        Go Back
      </Button>
    </div>
  </MainLayout>
</template>



<script setup lang="ts">
import { ref, onMounted, watch, computed } from "vue";
import MainLayout from "@/layouts/MainLayout.vue";
import Button from "@/components/Button.vue";
import { useFraudStore } from "@/stores/fraude.store";
import { useToast } from "vue-toastification";
import FraudMeter from "@/components/FraudMetter.vue"; // Import componenta

const data = ref({
  numeOfertant: "Ofertant necunoscut",
  cifOfertant: "CIF necunoscut",
  numeAutoritate: "Autoritate necunoscută",
  cifAutoritate: "CIF necunoscut",
  denumireAchizitie: "Achiziție necunoscută",
  descriereAchizitie: "Descriere indisponibilă",
  valoareEstimata: "Valoare estimată necunoscută",
});

const isFraudCheckActive = ref(false);

const startFraudCheck = async () => {
  chrome.storage.local.get("acquisitionId", async (result) => {
    const acquisitionId = result.acquisitionId;
    if (acquisitionId) {
      try {
        await fraudStore.checkFraud(acquisitionId);

        // Verifică dacă există erori
        if (fraudStore.error) {
          isFraudCheckActive.value = false; // Nu afișa turometrul
          toast.error(fraudStore.error); // Afișează mesajul de eroare
          console.log("Fraud check failed:", fraudStore.error);
        } else {
          isFraudCheckActive.value = true; // Afișează turometrul doar dacă nu există erori
          console.log("Fraud check passed");
        }
      } catch (e) {
        toast.error("A apărut o eroare neașteptată.");
        console.error(e);
      }
    } else {
      toast.error("Acquisition ID nu este disponibil în chrome.storage.");
    }
  });
};


const goBack = () => {
  isFraudCheckActive.value = false; 
};




const actualizeazaDate = (newData: any) => {
  data.value = {
    numeOfertant: newData.numeOfertant || "Ofertant necunoscut",
    cifOfertant: newData.cifOfertant || "CIF necunoscut",
    numeAutoritate: newData.numeAutoritate || "Autoritate necunoscută",
    cifAutoritate: newData.cifAutoritate || "CIF necunoscut",
    denumireAchizitie: newData.denumireAchizitie || "Achiziție necunoscută",
    descriereAchizitie: newData.descriereAchizitie || "Descriere indisponibilă",
    valoareEstimata: newData.valoareEstimata || "Valoare estimată necunoscută",
  };
};

watch(data, (newData, oldData) => {
  console.log("Datele au fost actualizate:");
  console.log("Date vechi:", oldData);
  console.log("Date noi:", newData);

}, { deep: true });

onMounted(() => {
  chrome.storage.local.get(
    [
      "numeOfertant",
      "cifOfertant",
      "numeAutoritate",
      "cifAutoritate",
      "denumireAchizitie",
      "descriereAchizitie",
      "valoareEstimata",
    ],
    (result) => {
      if (Object.keys(result).length > 0) {
        console.log("Date recuperate din chrome.storage:", result);
        actualizeazaDate(result);
      } else {
        console.log("Nu există date salvate în chrome.storage.");
      }
    }
  );

  chrome.runtime.onMessage.addListener((message) => {
    actualizeazaDate(message);

    chrome.storage.local.set(message, () => {
      console.log("Datele au fost salvate cu succes în chrome.storage.");
    });
  });
});

const fraudStore = useFraudStore();
const toast = useToast();
const { error } = fraudStore;

const isLoading = computed(() => fraudStore.loading);


</script>
