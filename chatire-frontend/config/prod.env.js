'use strict'
module.exports = {
  NODE_ENV: '"production"',
  API_URL: JSON.stringify(process.env.API_URL || 'https://chatire-production.up.railway.app'),
  WS_URL: JSON.stringify(process.env.WS_URL || 'wss://chatire-websockets-production.up.railway.app')
}
