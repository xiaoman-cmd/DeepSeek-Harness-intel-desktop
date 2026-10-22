// Make Node's built-in global fetch() honor HTTP(S)_PROXY environment variables.
//
// Why: in the bypass-sandbox network mode, outbound HTTPS is only allowed via the
// local proxy at 127.0.0.1:53858. Node's undici fetch does NOT read proxy env vars
// by default, so every `fetch()` (electron via @electron/get, plus the harness
// primary-runtime Node/Python/wheel downloads) fails with "fetch failed".
//
// This bootstrap installs a global dispatcher using undici's official
// EnvHttpProxyAgent, which reads HTTP_PROXY/HTTPS_PROXY/NO_PROXY from the env.
// @electron/get v5 also calls the same initializeProxy() when ELECTRON_GET_USE_PROXY=true.
// Requires undici installed next to this file: run `npm install undici` in this buildtools/ directory.
const { setGlobalDispatcher, EnvHttpProxyAgent, ProxyAgent } = require('./node_modules/undici')
const proxy = process.env.HTTPS_PROXY || process.env.https_proxy || process.env.HTTP_PROXY || process.env.http_proxy
if (proxy) {
  try {
    if (typeof EnvHttpProxyAgent === 'function') setGlobalDispatcher(new EnvHttpProxyAgent())
    else setGlobalDispatcher(new ProxyAgent(proxy))
    process.stderr.write('[proxy-bootstrap] global fetch dispatcher enabled (proxy=' + proxy + ')\n')
  } catch (error) {
    try { setGlobalDispatcher(new ProxyAgent(proxy)) } catch (_) {}
    process.stderr.write('[proxy-bootstrap] EnvHttpProxyAgent failed, used ProxyAgent: ' + String(error) + '\n')
  }
}
