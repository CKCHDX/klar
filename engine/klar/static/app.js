document.getElementById("search-button").addEventListener("click", () => {
  const query = document.getElementById("search-input").value;
  if (!query) return;
  const resultsDiv = document.getElementById("results");
  resultsDiv.innerHTML = "Söker...";
  // Send query to Python app backend function (to be connected via PyQt bridge)
  // Placeholder: simulate a fetch
  setTimeout(() => {
    resultsDiv.innerHTML = `<p>Resultat för "${query}" skulle visas här.</p>`;
  }, 1000);
});
