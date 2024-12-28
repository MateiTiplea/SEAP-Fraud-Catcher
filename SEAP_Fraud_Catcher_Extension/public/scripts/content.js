function trimiteDate() {
  try {
    const numeOfertant = document
      .querySelector(
        "#container-sizing > div.direct-acq-su-view > div:nth-child(1) > div.widget-body > ng-transclude > div > div > div:nth-child(1) > div > span:nth-child(2) > span",
      )
      .textContent.trim();
      console.log(numeOfertant);
    const cifOfertant = document
      .querySelector(
        "#container-sizing > div.direct-acq-su-view > div:nth-child(1) > div.widget-body > ng-transclude > div > div > div:nth-child(1) > div > span.u-displayfield__field.ng-binding",
      )
      .textContent.trim();
    const numeAutoritate = document
      .querySelector(
        "#container-sizing > div.direct-acq-su-view > div:nth-child(2) > div.widget-body > ng-transclude > div > div > div:nth-child(1) > div > span:nth-child(2) > a",
      )
      .textContent.trim();
    const cifAutoritate = document
      .querySelector(
        "#container-sizing > div.direct-acq-su-view > div:nth-child(2) > div.widget-body > ng-transclude > div > div > div:nth-child(1) > div > span.u-displayfield__field.ng-binding",
      )
      .textContent.trim();
    const denumireAchizitie = document
      .querySelector(
        "#container-sizing > div.direct-acq-su-view > div:nth-child(3) > div.widget-body > ng-transclude > div > div:nth-child(1) > div.margin-top-10 > div > p",
      )
      .textContent.trim();
    const descriereAchizitie = document
      .querySelector(
        "#container-sizing > div.direct-acq-su-view > div:nth-child(3) > div.widget-body > ng-transclude > div > div:nth-child(1) > div.margin-top-10 > div > p",
      )
      .textContent.trim();
    const valoareEstimata = document
      .querySelector(
        "#container-sizing > div.direct-acq-su-view > div:nth-child(3) > div.widget-body > ng-transclude > div > div:nth-child(2) > div > div > div:nth-child(2) > div.indent.padding-bottom-10.ng-binding.ng-scope",
      )
      .textContent.trim();

    chrome.storage.local.set(
      {
        //chrome storage
        numeOfertant: numeOfertant,
        cifOfertant: cifOfertant,
        numeAutoritate: numeAutoritate,
        cifAutoritate: cifAutoritate,
        denumireAchizitie: denumireAchizitie,
        descriereAchizitie: descriereAchizitie,
        valoareEstimata: valoareEstimata,
      },
      function () {
        console.log("Datele au fost salvate în chrome.storage");
      },
    );

    chrome.runtime.sendMessage(
      {
        numeOfertant: numeOfertant,
        cifOfertant: cifOfertant,
        numeAutoritate: numeAutoritate,
        cifAutoritate: cifAutoritate,
        denumireAchizitie: denumireAchizitie,
        descriereAchizitie: descriereAchizitie,
        valoareEstimata: valoareEstimata,
      },
      (response) => {
        console.log("Răspunsul de la background.js ", response);
      },
    );
  } catch (error) {
    console.error("Elementele nu au fost găsite pe pagină.");
  }
}

// se verifica schimbarea url-ului in fiecare secunda
let lastUrl = location.href;

function handleUrlChange() {
  const currentUrl = location.href;
  if (currentUrl !== lastUrl) {
    console.log(`URL-ul s-a schimbat de la ${lastUrl} la ${currentUrl}`);
    lastUrl = currentUrl;
    trimiteDate();
  }
}

// Observă schimbările în DOM
const observer = new MutationObserver(() => {
  console.log("DOM-ul s-a modificat, se verifică datele...");
  trimiteDate();
});

observer.observe(document.body, {
  childList: true,
  subtree: true,
});

// Verificare periodică a URL-ului
setInterval(handleUrlChange, 1000);

// La încărcare
window.onload = function () {
  trimiteDate();
};
