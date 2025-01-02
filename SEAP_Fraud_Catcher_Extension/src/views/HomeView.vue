<template>
  <MainLayout>
    <div class="items-left m-4 flex flex-col justify-between bg-white p-2 px-5 font-mono">
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
    </div>
    <div class="p-4m flex flex-col items-center justify-between bg-white px-5 font-mono">
      <Button :loading="isLoading" @click="checkIfFraud">
        Este Frauda?
      </Button>
    </div>

    <!-- Blocul cu informații despre fraudă -->
    <div v-if="fraudStore.fraudScore !== null" class="detalii-frauda mt-4 p-4 bg-gray-100 rounded">
      <h2 class="font-semibold text-[#1AC2FF]">Scor total de fraudă: {{ fraudStore.fraudScore }}</h2>
      <div v-if="Object.keys(fraudStore.fraudScorePerItem).length">
        <h3 class="font-semibold text-[#1AC2FF]">Scoruri pe item:</h3>
        <ul>
          <li v-for="(score, item) in fraudStore.fraudScorePerItem" :key="item">
            <span class="font-bold">{{ item }}:</span> {{ score }}
          </li>
        </ul>
      </div>
    </div>
  </MainLayout>
</template>


<script setup lang="ts">
import { ref, onMounted, watch, computed } from "vue";
import MainLayout from "@/layouts/MainLayout.vue";
import Button from "@/components/Button.vue";
import { useFraudStore } from "@/stores/fraude.store";
import { useToast } from "vue-toastification";

const data = ref({
  numeOfertant: "Ofertant necunoscut",
  cifOfertant: "CIF necunoscut",
  numeAutoritate: "Autoritate necunoscută",
  cifAutoritate: "CIF necunoscut",
  denumireAchizitie: "Achiziție necunoscută",
  descriereAchizitie: "Descriere indisponibilă",
  valoareEstimata: "Valoare estimată necunoscută",
});

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

// Watch pentru actualizarea datelor
watch(data, (newData, oldData) => {
  console.log("Datele au fost actualizate:");
  console.log("Date vechi:", oldData);
  console.log("Date noi:", newData);

  // Logică suplimentară dacă este necesar
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

  // Ascultă mesaje noi
  chrome.runtime.onMessage.addListener((message) => {
    actualizeazaDate(message);

    // Salvează datele primite
    chrome.storage.local.set(message, () => {
      console.log("Datele au fost salvate cu succes în chrome.storage.");
    });
  });
});

const fraudStore = useFraudStore();
const toast = useToast();
const { error } = fraudStore;

const isLoading = computed(() => fraudStore.loading);

const checkIfFraud = () => {
  chrome.storage.local.get("acquisitionId", async (result) => {
    const acquisitionId = result.acquisitionId;
    console.log("CHECKING")
    if (acquisitionId) {
      await fraudStore.checkFraud(acquisitionId);
    } else {
      toast.error("Teapa")
      console.error("Acquisition ID nu este disponibil în chrome.storage.");
    }
  });
};
</script>
