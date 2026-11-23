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
window.cambiaLingua = () => { try { localStorage.setItem('difendi-smerillo-lingua', window.CG_LINGUA === 'it' ? 'en' : 'it'); } catch(e){} location.reload(); };''')

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
  var L = null; try {{ L = localStorage.getItem('difendi-smerillo-lingua'); }} catch(e){{}}
  if (L !== 'it' && L !== 'en'){{ var n = (navigator.languages && navigator.languages[0]) || navigator.language || ''; L = /^it/i.test(n) ? 'it' : 'en'; }}
  var b = atob(document.getElementById('v-' + L).textContent), u = new Uint8Array(b.length);
  for (var i = 0; i < b.length; i++) u[i] = b.charCodeAt(i);
  var html = new TextDecoder('utf-8').decode(u);
  setTimeout(function(){{ document.open(); document.write(html); document.close(); }}, 0);
}})();
</script>
</body></html>'''

os.makedirs(os.path.join(QUI, 'prove'), exist_ok=True)   # copie separate per i test (non si caricano)
open(os.path.join(QUI, 'prove', 'it.html'), 'w', encoding='utf-8').write(s_it)
open(os.path.join(QUI, 'prove', 'en.html'), 'w', encoding='utf-8').write(s_en)
out = os.path.join(QUI, 'index.html')
open(out, 'w', encoding='utf-8').write(s)
print('ok', out, round(len(s.encode()) / 1e6, 2), 'MB')
