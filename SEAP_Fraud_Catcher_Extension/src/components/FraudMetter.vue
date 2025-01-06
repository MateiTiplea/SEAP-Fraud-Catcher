<template>
  <div class="fraud-meter">
    <div class="gauge-container">
      <svg viewBox="0 0 100 50" class="gauge">
        <path
          d="M 10 50 A 40 40 0 0 1 90 50"
          fill="none"
          stroke="#e0e0e0"
          stroke-width="10"
        />
        <path
          d="M 10 50 A 40 40 0 0 1 90 50"
          fill="none"
          :stroke="gaugeColor"
          stroke-width="10"
          stroke-dasharray="126"
          :stroke-dashoffset="126 - (score / 100) * 126"
        />
      </svg>
    </div>

    <div class="score-container">
      <p class="score">{{ animatedScore }}</p>
      <span class="unit">%</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, defineProps, computed } from "vue";

const props = defineProps({
  score: {
    type: Number,
    required: true,
  },
});

const animatedScore = ref(0);

const gaugeColor = computed(() => {
  if (props.score <= 30) return "green";
  if (props.score <= 70) return "yellow";
  return "red";
});

// Animație pentru scor
watch(
  () => props.score,
  (newScore) => {
    animatedScore.value = 0;
    const duration = 2000;
    const step = newScore / (duration / 50);

    let currentScore = 0;
    const interval = setInterval(() => {
      if (currentScore >= newScore) {
        clearInterval(interval);
      } else {
        currentScore += step;
        animatedScore.value = Math.round(currentScore);
      }
    }, 50);
  },
  { immediate: true },
);
</script>

<style scoped>
.fraud-meter {
  display: flex;
  flex-direction: column; /* Turometrul deasupra scorului */
  justify-content: center;
  align-items: center;
  margin-top: 1rem;
}

.gauge-container {
  position: relative;
  width: 200px;
  height: 100px; /* Dimensiune pentru semicerc */
}

.gauge {
  width: 100%;
  height: 100%;
  transform: rotate(0deg);
}

.score-container {
  display: flex;
  align-items: center; /* Aliniază textul și procentul pe aceeași linie */
  margin-top: 0rem; /* Spațiu între turometru și scor */
}

.score {
  font-size: 2rem;
  font-weight: bold;
  margin-right: 0.1rem; /* Spațiu între scor și procent */
}

.unit {
  font-size: 1.5rem;
  color: #666;
}
</style>
