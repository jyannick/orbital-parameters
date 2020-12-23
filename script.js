document.addEventListener("readystatechange", async (event) => {
  // When window loaded ( external resources are loaded too- `css`,`src`, etc...)
  if (event.target.readyState === "complete") {
    await new Promise((r) => setTimeout(r, 50));
    document
      .getElementsByClassName("update_button")[0]
      .getElementsByClassName("bk-btn-default")[0]
      .click();
  }
});
