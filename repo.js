document.addEventListener('DOMContentLoaded', function() {
  ready()
}, false);

window.$ = window.$ || function() {
  var nodes = document.querySelectorAll.apply(document, arguments);
  return nodes.length == 1 ? nodes[0] : nodes;
};

function buildURL(info) {
  return 'conf/' + info.join('-');
}

function toArray(arr) {
  return Array.prototype.slice.call(arr);
}

function getInfo(dist) {
  var selector = '#' + dist + ' select';
  return [dist].concat(toArray($(selector)).map(function(e) {
    return e.options[e.selectedIndex].value;
  }));
}

function ready() {
  var distros = ['archlinux', 'debian', 'ubuntu'];

  // Download cfg
  $('#content').onclick = function(evt) {
    if (evt.target.tagName !== 'BUTTON') return;
    evt.preventDefault();
    var dist = evt.target.className;
    var ele = document.createElement('a');
    ele.setAttribute('href', buildURL(getInfo(dist)));
    ele.setAttribute('download', evt.target.name);
    document.body.appendChild(ele);
    ele.click();
    document.body.removeChild(ele);
  }

  // Change cfg
  $('#content').onchange = function(evt) {
    var dist = evt.target.className;
    var warn = $('#' + dist + '-warn');
    getCfg(getInfo(dist), function(err, data) {
      if (err) {
        warn.style.display = '';
        warn.style.color = 'red';
        warn.textContent = err.toString();
      } else {
        var select;
        switch (dist) {
          case 'ubuntu':
            select = $('select.ubuntu')[2];
            if (select.options[select.selectedIndex].className === 'end-of-life') {
              warn.style.display = '';
              warn.style.color = 'red';
              warn.textContent = 'Warn: You have selected an End-of-life releases. Use it at your own risk';
            } else {
              warn.style.display = 'none';
            }
            break;

          case 'debian':
            select = $('select.debian')[0];
            if (select.options[select.selectedIndex].value === 'https') {
              warn.style.display = '';
              warn.textContent = 'Tips: Remember to install package <apt-transport-https>';
            } else {
              warn.style.display = 'none';
            }
            break;

          default:
            warn.style.display = 'none';
        }
      }
      $('pre.' + dist).textContent = data;
    });
  }

  distros.forEach(function(dist) {
    // Initialize
    getCfg(getInfo(dist), function(err, data) {
      var warn = $('#' + dist + '-warn');
      if (err) {
        warn.style.display = '';
        warn.textContent = err.toString();
      }
      $('#' + dist + ' pre').textContent = data;
    });

  });

  var select = $('select.debian')[0];
  if (select.options[select.selectedIndex].value === 'https') {
    var warn = $('#debian-warn');
    warn.style.display = '';
    warn.textContent = 'Tips: Remember to install package <apt-transport-https>';
  }
}

function getCfg(info, cb) {
  var url = buildURL(info);
  var xhr = new XMLHttpRequest();
  xhr.timeout = 5000;
  xhr.responseType = 'text';
  xhr.onload = function() {
    if (xhr.status == 200) {
      cb(null, xhr.responseText.toString())
    } else {
      cb(new Error(xhr.statusText))
    }
  };
  xhr.open('GET', url, true); // async
  xhr.send();
}
