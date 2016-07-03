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

function ready() {
  var distros = ['archlinux', 'debian', 'ubuntu'];
  distros.forEach(function(dist) {
    var selector = '#' + dist + ' select';
    var info = [dist].concat(toArray($(selector)).map(function(e) {
      return e.options[e.selectedIndex].value;
    }));
    getCfg(info, function(err, data) {
      $('#' + dist + ' pre').textContent = data;
    });

    $('#' + dist + ' button').onclick = function(evt) {
      evt.preventDefault();
      var info = [dist].concat(toArray($(selector)).map(function(e) {
        return e.options[e.selectedIndex].value;
      }));
      var ele = document.createElement('a');
      ele.setAttribute('href', buildURL(info));
      ele.setAttribute('download', 'sources.list');
      document.body.appendChild(ele);
      ele.click();
      document.body.removeChild(ele);
    };
  });
}

function getCfg(info, cb) {
  var url = buildURL(info);
  var xhr = new XMLHttpRequest();
  xhr.onload = function() {
    if (xhr.status == 200) {
      cb(null, xhr.responseText.toString())
    } else {
      cb(new Error('Unknown Error'))
    }
  };
  xhr.open('GET', url, true); // async
  xhr.send();
}
