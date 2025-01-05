<template>
  <MainLayout>
    <div
      v-if="!isOnAcquisitionPage"
      class="flex flex-col items-center justify-center mt-12"
    >
      <IconError/>
      <p class="mt-6 mb-4 px-16 text-center text-lg font-semibold text-red-600">
        Nu sunteți pe o pagină validă de achiziție. Vă rugăm să navigați pe o
        pagină de achiziție pentru a utiliza aplicația.
      </p>
      <div class="mt-6 flex items-center justify-center">
        <Button @click="openSeap"> SEAP </Button>
      </div>
    </div>

    <div
      v-else-if="!isFraudCheckActive"
      class="items-left m-4 flex flex-col justify-between bg-white p-2 px-5 font-mono"
    >
      <div id="data-container">
        <div class="achizitie">
          <div class="ofertant mb-4">
            <h2>
              <span class="font-semibold text-[#1AC2FF]">Ofertant: </span
              ><span>{{ data.numeOfertant }}</span>
            </h2>
            <p>
              <span class="font-semibold text-[#1AC2FF]">CIF: </span
              ><span>{{ data.cifOfertant }}</span>
            </p>
          </div>

          <div class="autoritate-contractanta mb-4">
            <h2>
              <span class="font-semibold text-[#1AC2FF]"
                >Autoritate Contractanta:
              </span>
              <span>{{ data.numeAutoritate }}</span>
            </h2>
            <p>
              <span class="font-semibold text-[#1AC2FF]">CIF: </span
              ><span>{{ data.cifAutoritate }}</span>
            </p>
          </div>

          <div class="detalii-achizitie">
            <h2>
              <span class="font-semibold text-[#1AC2FF]"
                >Denumire Achizitie:
              </span>
              <span>{{ data.denumireAchizitie }}</span>
            </h2>
            <p>
              <span class="font-semibold text-[#1AC2FF]">Descriere: </span
              ><span>{{ data.descriereAchizitie }}</span>
            </p>
            <p>
              <span class="font-semibold text-[#1AC2FF]"
                >Valoare Estimata: </span
              ><span>{{ data.valoareEstimata }}</span>
            </p>
          </div>
        </div>
      </div>
      <div
        class="flex flex-col items-center justify-between bg-white p-4 px-5 font-mono"
      >
        <Button :loading="isLoading" @click="startFraudCheck">
          Este Frauda?
        </Button>
      </div>
    </div>

    <!-- Afișează turometrul -->
    <div v-else class="flex flex-col items-center justify-center bg-white p-4">
      <FraudMeter :score="fraudStore.fraudScore ?? 0" />
      <Button @click="goBack" class="mt-4"> Go Back </Button>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import MainLayout from "@/layouts/MainLayout.vue";
import Button from "@/components/Button.vue";
import { useFraudStore } from "@/stores/fraude.store";
import { useToast } from "vue-toastification";
import FraudMeter from "@/components/FraudMetter.vue";
import IconError from "@/components/icons/IconError.vue";

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
const currentUrl = ref<string>("");

const isOnAcquisitionPage = computed(() => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs[0] && tabs[0].url) {
      currentUrl.value = tabs[0].url;
      console.log("URL curent obținut:", currentUrl.value);
    } else {
      console.error("Nu s-a putut obține URL-ul tab-ului activ.");
      currentUrl.value = "";
    }
  });

  const pattern =
    /^https:\/\/e-licitatie\.ro\/pub\/direct-acquisition\/view\/\d+/;
  return pattern.test(currentUrl.value);
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

const openSeap = () => {
  window.open(
    "https://e-licitatie.ro/pub/direct-acquisitions/list/1",
    "_blank",
  );
};
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
      actualizeazaDate(result);
    },
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

const startFraudCheck = async () => {
  chrome.storage.local.get("acquisitionId", async (result) => {
    const acquisitionId = result.acquisitionId;
    if (acquisitionId) {
      try {
        await fraudStore.checkFraud(acquisitionId);

        if (fraudStore.error) {
          isFraudCheckActive.value = false;
          toast.error(fraudStore.error);
        } else {
          isFraudCheckActive.value = true;
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

const isLoading = computed(() => fraudStore.loading);
</script>
