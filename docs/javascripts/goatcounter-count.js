// Local GoatCounter-compatible pageview tracker for this MkDocs site.
// It avoids loading https://gc.zgo.at/count.js while still sending hits to the
// GoatCounter endpoint configured by data-goatcounter.
(function () {
  "use strict";

  function isLocalHost() {
    return (
      window.location.hostname === "localhost" ||
      window.location.hostname === "127.0.0.1" ||
      window.location.hostname === "0.0.0.0"
    );
  }

  function getEndpoint() {
    var script = document.querySelector("script[data-goatcounter]");
    return script ? script.getAttribute("data-goatcounter") : "";
  }

  function getPath() {
    var canonical = document.querySelector('link[rel="canonical"][href]');
    if (canonical) {
      try {
        var canonicalUrl = new URL(canonical.href, window.location.href);
        if (canonicalUrl.hostname.replace(/^www\./, "") === window.location.hostname.replace(/^www\./, "")) {
          return canonicalUrl.pathname + canonicalUrl.search;
        }
      } catch (error) {
        // Fall back to location below.
      }
    }
    return window.location.pathname + window.location.search || "/";
  }

  function queryString(data) {
    var parts = [];
    Object.keys(data).forEach(function (key) {
      var value = data[key];
      if (value !== "" && value !== null && value !== undefined && value !== false) {
        parts.push(encodeURIComponent(key) + "=" + encodeURIComponent(value));
      }
    });
    return "?" + parts.join("&");
  }

  function sendPageview() {
    if (isLocalHost()) {
      return;
    }

    var endpoint = getEndpoint();
    if (!endpoint) {
      return;
    }

    var url = endpoint + queryString({
      p: getPath(),
      r: document.referrer,
      t: document.title,
      e: false,
      s: window.screen ? window.screen.width : undefined,
      b: navigator.webdriver ? 153 : 0,
      q: window.location.search,
      rnd: Math.random().toString(36).slice(2, 7)
    });

    if (!navigator.sendBeacon || !navigator.sendBeacon(url)) {
      var img = document.createElement("img");
      img.src = url;
      img.alt = "";
      img.setAttribute("aria-hidden", "true");
      img.style.position = "absolute";
      img.style.bottom = "0";
      img.style.width = "1px";
      img.style.height = "1px";
      img.style.opacity = "0";
      img.addEventListener("load", function () {
        if (img.parentNode) {
          img.parentNode.removeChild(img);
        }
      });
      document.body.appendChild(img);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", sendPageview, false);
  } else {
    sendPageview();
  }
})();
