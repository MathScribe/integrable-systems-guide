(function () {
  if (
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1"
  ) {
    return;
  }

  var script = document.createElement("script");
  script.setAttribute("data-goatcounter", "https://nono6.goatcounter.com/count");
  script.setAttribute("async", "true");
  script.setAttribute("src", "https://gc.zgo.at/count.js");
  document.head.appendChild(script);
})();
