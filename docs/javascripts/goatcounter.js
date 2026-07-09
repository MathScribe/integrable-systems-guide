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

  var currentScript = document.currentScript;
  var localScriptUrl = currentScript && currentScript.src
    ? new URL("goatcounter-count.js", currentScript.src).toString()
    : "/integrable-systems-guide/javascripts/goatcounter-count.js";

  script.setAttribute("src", localScriptUrl);
  document.head.appendChild(script);
})();
