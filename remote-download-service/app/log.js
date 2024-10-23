const fs = require('fs')
const logger = exports
const os = require('os');

function getLocalIP() {
  const interfaces = os.networkInterfaces();
  for (let iface in interfaces) {
    for (let i = 0; i < interfaces[iface].length; i++) {
      const address = interfaces[iface][i];
      if (address.family === 'IPv4' && !address.internal) {
        return address.address;
      }
    }
  }
  return '127.0.0.1';
}

logger.dest = '/app/remote-download-service/logs/remote-download-service.log'

logger.init = function (dest = '/app/remote-download-service/logs/remote-download-service.log', customMsg = 'remote-download-service started') {
  const green = '\x1b[32m';
  const reset = '\x1b[0m';
  const localIP = getLocalIP();

  this.dest = dest;
  fs.appendFileSync(this.dest, time() + '[INIT] ' + customMsg + '\n');
  console.log(time() + '[INIT] ' + customMsg);

  console.log(time() + '[INIT] ' + 'service monitor:          ' + green + `http://${localIP}:8080/metrics` + reset);
  console.log(time() + '[INIT] ' + 'service health check: ' + green + `    http://${localIP}:8080/health` + reset);
}

logger.succ = function (file, URL) {
  fs.appendFileSync(this.dest, time() + '[SUCC] ' + URL + ' -> ' + file + '\n')
  console.log(time() + '[SUCC] ' + URL + ' -> ' + file)
}

logger.fail = function (file, URL, errmsg) {
  fs.appendFileSync(this.dest, time() + '[FAIL] ' + URL + ' -> ' + file + ': ' + errmsg + '\n')
  console.log(time() + '[ERROR] ' + URL + ' -> ' + file + ': ' + errmsg)
}

function time () {
  const dateObj = new Date()
  return '[' + dateObj.getFullYear() + '-' + dateObj.getMonth() + '-' + dateObj.getDate() + ' ' + dateObj.getHours() + ':' + dateObj.getMinutes() + ']'
}
