document.getElementById("uname-login").onclick = logIn;


function logIn() {
  // Get a value saved in a form.
  var theValue = uname.value;
  // Check that there's some code there.
  if (!theValue) {

    return;
  }
  // Save it using the Chrome extension storage API.
  chrome.storage.sync.set({'value': theValue}, function() {

  });

  var screenWidth = screen.availWidth;
  var screenHeight = screen.availHeight;
  var width = 800;
  var height = 550;

  chrome.app.window.create('client.html', {
    id: "clientID",
    bounds: {
      width: width,
      height: height,
      left: Math.round((screenWidth-width)/2),
      top: Math.round((screenHeight-height)/2)
    }
  });

  chrome.app.window.current().close()
}
