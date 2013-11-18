onload = function init() {
  var un = "none";

  chrome.storage.sync.get("value", function(obj) {
    un = obj.value;
    document.getElementById("uname_h1").innerText = "Welcome " + un;
  });
}
