# Crea crazygames/index.html partendo dalla beta.
# Versione per CrazyGames (Basic Launch): niente account, niente server, niente link esterni,
# multiplayer solo con codice stanza, testi in inglese, niente richiesta "aggiungi alla Home". Salvataggio solo sul dispositivo.
import re, os, sys
QUI = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(QUI, '..', 'beta', 'index.html'), encoding='utf-8').read()

def sost(vecchio, nuovo, n=1):
    global s
    c = s.count(vecchio)
    if c != n: sys.exit(f'ERRORE: trovato {c} volte (attese {n}): {vecchio[:90]}')
    s = s.replace(vecchio, nuovo)

TESTA = r'''<script>
/* ===== versione CrazyGames ===== */
window.CG_BUILD = true;
(() => {
  // al server vanno solo il multiplayer (stanze) e il conteggio anonimo delle visite; account, classifiche, diario e aggiornamenti restano spenti
  const permesso = u => /supabase\.co\/rest\/v1\/rpc\/(ds_stanza_[a-z_]+|ds_traccia)$/.test(u);
  const blocca = u => { u = String(u); return permesso(u) ? false : /supabase\.co|version\.json|unpkg\.com|jsdelivr\.net|github\.io/.test(u); };
  const f0 = window.fetch.bind(window);
  window.fetch = (u, o) => blocca(u && u.url || u) ? Promise.resolve(new Response('null', {status: 503, headers: {'Content-Type': 'application/json'}})) : f0(u, o);
  window.open = () => null;
  try { localStorage.setItem('difendi-smerillo-home', '1'); localStorage.setItem('difendi-smerillo-voto', 'cg'); } catch(e){}
})();
</script>
<style id="cgNascondi">
/* parti che non servono su CrazyGames */
.cr-tab[data-tab="classifica"], #pfAcc, .fd-inv, .st-cond, .cl-card, #hmProf .pf-acc, [onclick*="privacy"], .acc-priv, #amInv { display: none !important; }
</style>
'''
sost('<meta charset="utf-8">', '<meta charset="utf-8">\n' + TESTA)
# niente manifest / icona da app installabile (il gioco gira dentro la pagina di CrazyGames)
s = re.sub(r'<link rel="manifest"[^>]*>', '', s)

# 1) schermata d'ingresso: niente account, solo il tocco per entrare (serve anche per accendere la musica)
sost("else { try { ACC.cancello(ld, () => { if (uscito) return; uscito = true; clearInterval(tiT); ld.classList.add('via'); setTimeout(() => ld.remove(), 420); }); } catch(e){ console.error(e); if (via){ via.hidden = false; via.onclick = esci; } } }",
     "else { if (via){ via.hidden = false; via.onclick = esci; } else esci(); }")
# 2) nessun obbligo di creare l'account, nessuna finestra account
sost("function devRegistrarsi(){ try { if (ACC.account) return false; }", "function devRegistrarsi(){ if (window.CG_BUILD) return false; try { if (ACC.account) return false; }")
sost("  function apri(tab, op = {}){ if (provaAttiva()){", "  function apri(tab, op = {}){ if (window.CG_BUILD) return; if (provaAttiva()){")
# 3) menu: niente schede Amici e Classifica
sost("['amici', 'amici', 'Amici', false], ['classifica', 'coppa', 'Classifica', false]];", "['amici', 'amici', 'Amici', false], ['classifica', 'coppa', 'Classifica', false]].filter(x => !window.CG_BUILD || x[0] !== 'classifica');")

sost("pgs = [...c.querySelectorAll('.cr-pg')];", "pgs = [...c.querySelectorAll('.cr-pg')].filter(p => !window.CG_BUILD || p.dataset.tab !== 'classifica' || (p.remove(), false));")

# 4) conteggio delle visite da CrazyGames (anonimo: un numero a caso per dispositivo, nessun dato personale)
sost("const DA = (() => { const m = /[?&]da=", "const DA = (() => { if (window.CG_BUILD) return 'crazygames'; const m = /[?&]da=")
sost("vero = /github\\.io$/.test(location.hostname) && !/\\/beta\\//.test(location.pathname);", "vero = !!window.CG_BUILD || (/github\\.io$/.test(location.hostname) && !/\\/beta\\//.test(location.pathname));")

# 5) pulsante lingua nel pannello "Altro"
sost('''<button class="big alt" data-p="home">Indietro</button></div>`;
  } else if (pannello === 'profilo')''', '''${window.CG_LINGUA === 'it' ? '<button class="big alt" onclick="cambiaLingua()">🌐 English</button>' : '<button class="big alt" onclick="cambiaLingua()">🌐 Italiano</button>'}
      <button class="big alt" data-p="home">Indietro</button></div>`;
  } else if (pannello === 'profilo')''')
sost('window.CG_BUILD = true;', '''window.CG_BUILD = true; window.CG_LINGUA = '@@LINGUA@@';
/* salvataggio sul cloud di CrazyGames (SDK, Data module) e tasto muto di CrazyGames */
(() => {
  const SDK = () => window.CG_SDK_OK && window.CrazyGames && window.CrazyGames.SDK;
  const tutto = () => { const o = {}; for (let i = 0; i < localStorage.length; i++){ const k = localStorage.key(i); if (/^difendi-smerillo/.test(k)) o[k] = localStorage.getItem(k); } return o; };
  let t = null; const scrivi = () => { const S = SDK(); if (!S) return; try { S.data.setItem('ds-salvataggio', JSON.stringify(tutto())); } catch(e){} };
  const salva = () => { clearTimeout(t); t = setTimeout(scrivi, 1500); };
  const sI = Storage.prototype.setItem, rI = Storage.prototype.removeItem;
  Storage.prototype.setItem = function(k, v){ sI.call(this, k, v); if (this === window.localStorage && /^difendi-smerillo/.test(k)) salva(); };
  Storage.prototype.removeItem = function(k){ rI.call(this, k); if (this === window.localStorage && /^difendi-smerillo/.test(k)) salva(); };
  window.addEventListener('pagehide', () => { if (t){ clearTimeout(t); scrivi(); } });
  let gioca = false;
  window.CG_GP = on => { const S = SDK(); if (!S || on === gioca) return; gioca = on; try { on ? S.game.gameplayStart() : S.game.gameplayStop(); } catch(e){} };
  window.CG_CARICATO = () => { const S = SDK(); if (S) try { S.game.loadingStop(); } catch(e){} };
  const S = SDK(); if (!S) return;
  let mutoCG = false;
  const applica = st => { try { const m = !!(st && st.muteAudio); window.CG_MUTO = m; const A = window.SUONI_CG; if (!A) return; if (m) A.muto = true; else if (mutoCG) A.muto = false; mutoCG = m; } catch(e){} };
  try { S.game.addSettingsChangeListener(applica); } catch(e){}
  window.addEventListener('load', () => { try { applica(S.game.settings); } catch(e){} });
})();
window.cambiaLingua = () => { try { localStorage.setItem('difendi-smerillo-lingua', window.CG_LINGUA === 'it' ? 'en' : 'it'); } catch(e){} location.reload(); };''')

sost("localStorage.setItem('difendi-smerillo-audio', v ? 'no' : 'si'); } catch(e){} } };\n})();", "localStorage.setItem('difendi-smerillo-audio', v ? 'no' : 'si'); } catch(e){} } };\n})();\nwindow.SUONI_CG = SUONI;")

# 5c) avvisi a CrazyGames: fine caricamento, inizio e fine partita; il loro "muto" vince sul nostro
sost("const esci = () => { if (uscito) return; uscito = true;", "const esci = () => { if (uscito) return; uscito = true; try { window.CG_CARICATO && CG_CARICATO(); window.CG_GP && CG_GP(true); } catch(e){}")
sost("function mostraMenu(", "function mostraMenu(){ try { window.CG_GP && CG_GP(false); } catch(e){} return mostraMenu0.apply(this, arguments); }\nfunction mostraMenu0(")
sost("function nuovaPartita(", "function nuovaPartita(){ try { window.CG_GP && CG_GP(true); } catch(e){} return nuovaPartita0.apply(this, arguments); }\nfunction nuovaPartita0(")
sost("function apri(modo){ provenienza = 'menu';", "function apri(modo){ try { window.CG_GP && CG_GP(true); } catch(e){} provenienza = 'menu';")
sost("function apri(dopo){ APRI_DOPO = dopo || null;", "function apri(dopo){ try { window.CG_GP && CG_GP(true); } catch(e){} APRI_DOPO = dopo || null;")
sost("set muto(v){ muto = v;", "set muto(v){ if (!v && window.CG_MUTO) return; muto = v;")

# 6) testi in inglese (CrazyGames chiede l'inglese come lingua principale)
from traduci import traduci_html
s_en, n = traduci_html(s)
print('testi tradotti:', n)
s_it = s.replace('@@LINGUA@@', 'it'); s_en = s_en.replace('@@LINGUA@@', 'en')

# 7) un solo file con le due lingue: sceglie la lingua salvata, altrimenti quella del telefono (italiano se è in italiano, se no inglese)
import base64
b64 = lambda x: base64.b64encode(x.encode('utf-8')).decode('ascii')
VIEW = re.search(r'<meta name="viewport"[^>]*>', s).group()
s = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">{VIEW}<title>Difendi Smerillo</title></head>
<body style="margin:0;background:#0b0f2e">
<script type="text/plain" id="v-it">{b64(s_it)}</script>
<script type="text/plain" id="v-en">{b64(s_en)}</script>
<script>
(function(){{
  // 1) SDK di CrazyGames: se c'è, riporta i progressi salvati sul cloud prima di aprire il gioco
  var fatto = false;
  function via(ok){{ if (fatto) return; fatto = true; window.CG_SDK_OK = false;
    try {{ var S = ok && window.CrazyGames && window.CrazyGames.SDK;
      if (S && S.environment !== 'disabled'){{ window.CG_SDK_OK = true; try {{ S.game.loadingStart(); }} catch(e){{}} var b = S.data.getItem('ds-salvataggio');
        if (b){{ var o = JSON.parse(b); for (var k in o) if (/^difendi-smerillo/.test(k)) localStorage.setItem(k, o[k]); }} }}
    }} catch(e){{}}
    apri(); }}
  try {{ var sc = document.createElement('script'); sc.src = 'https://sdk.crazygames.com/crazygames-sdk-v3.js';
    sc.onload = function(){{ try {{ window.CrazyGames.SDK.init().then(function(){{ via(true); }}, function(){{ via(false); }}); }} catch(e){{ via(false); }} }};
    sc.onerror = function(){{ via(false); }}; document.head.appendChild(sc); }} catch(e){{ via(false); }}
  setTimeout(function(){{ via(false); }}, 5000);
  function apri(){{
  var L = null; try {{ L = localStorage.getItem('difendi-smerillo-lingua'); }} catch(e){{}}
  if (L !== 'it' && L !== 'en'){{ var n = (navigator.languages && navigator.languages[0]) || navigator.language || ''; L = /^it/i.test(n) ? 'it' : 'en'; }}
  var b = atob(document.getElementById('v-' + L).textContent), u = new Uint8Array(b.length);
  for (var i = 0; i < b.length; i++) u[i] = b.charCodeAt(i);
  var html = new TextDecoder('utf-8').decode(u);
  setTimeout(function(){{ document.open(); document.write(html); document.close(); }}, 0);
  }}
}})();
</script>
</body></html>'''

os.makedirs(os.path.join(QUI, 'prove'), exist_ok=True)   # copie separate per i test (non si caricano)
open(os.path.join(QUI, 'prove', 'it.html'), 'w', encoding='utf-8').write(s_it)
open(os.path.join(QUI, 'prove', 'en.html'), 'w', encoding='utf-8').write(s_en)
out = os.path.join(QUI, 'index.html')
open(out, 'w', encoding='utf-8').write(s)
print('ok', out, round(len(s.encode()) / 1e6, 2), 'MB')
