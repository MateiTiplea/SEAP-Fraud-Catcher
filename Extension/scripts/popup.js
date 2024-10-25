function actualizeazaUI(date) {
  document.querySelector('.nume-ofertant').textContent = date.numeOfertant || "Ofertant necunoscut";
  document.querySelector('.cif-ofertant').textContent = date.cifOfertant || "CIF necunoscut";
  document.querySelector('.nume-autoritate').textContent = date.numeAutoritate || "Autoritate necunoscută";
  document.querySelector('.cif-autoritate').textContent = date.cifAutoritate || "CIF necunoscut";
  document.querySelector('.denumire-achizitie').textContent = date.denumireAchizitie || "Denumire necunoscută";
  document.querySelector('.descriere-achizitie').textContent = date.descriereAchizitie || "Descriere indisponibilă";
  document.querySelector('.valoare-estimata').textContent = date.valoareEstimata || "Valoare estimată necunoscută";
}

// se actualizeaza datele din storage
chrome.storage.local.get(['numeOfertant', 'cifOfertant', 'numeAutoritate', 'cifAutoritate', 'denumireAchizitie', 'descriereAchizitie', 'valoareEstimata'], function(result) {
  if (Object.keys(result).length > 0) {
      console.log("Date recuperate din chrome.storage:", result);
      actualizeazaUI(result); 
  } else {
      console.log('Nu există date salvate în chrome.storage.');
  }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log("Mesaj primit în popup.js:", message.numeOfertant);

  actualizeazaUI(message);

  chrome.storage.local.set({
      numeOfertant: message.numeOfertant,
      cifOfertant: message.cifOfertant,
      numeAutoritate: message.numeAutoritate,
      cifAutoritate: message.cifAutoritate,
      denumireAchizitie: message.denumireAchizitie,
      descriereAchizitie: message.descriereAchizitie,
      valoareEstimata: message.valoareEstimata
  }, function() {
      console.log('Datele au fost salvate în chrome.storage.');
  });
});
