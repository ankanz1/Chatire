'use strict'
const merge = require('webpack-merge')
const prodEnv = require('./prod.env')

module.exports = merge(prodEnv, {
  NODE_ENV: '"development"',
  API_URL: '("http://" + window.location.hostname + ":8000")',
  WS_URL: '("ws://" + window.location.hostname + ":8081")'
})
