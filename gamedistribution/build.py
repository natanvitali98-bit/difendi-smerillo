# Crea gamedistribution/index.html (e il .zip da caricare) partendo dalla beta.
# Stessa base della versione CrazyGames (niente account, niente link esterni, inglese + italiano),
# ma con l'SDK di GameDistribution: pubblicità prima di entrare e tra una partita e l'altra, sempre dopo un tocco.
# Uso: python3 gamedistribution/build.py [GAME_ID]   (il GAME_ID si trova nel pannello sviluppatori di GameDistribution)
import re, os, sys, zipfile
QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'crazygames'))
GDID = sys.argv[1] if len(sys.argv) > 1 else (open(os.path.join(QUI, 'gameid.txt')).read().strip() if os.path.exists(os.path.join(QUI, 'gameid.txt')) else 'GAME_ID_DA_INSERIRE')
s = open(os.path.join(QUI, '..', 'beta', 'index.html'), encoding='utf-8').read()

def sost(vecchio, nuovo, n=1):
    global s
    c = s.count(vecchio)
    if c != n: sys.exit(f'ERRORE: trovato {c} volte (attese {n}): {vecchio[:90]}')
    s = s.replace(vecchio, nuovo)

TESTA = r'''<script>
/* ===== versione GameDistribution ===== */
window.CG_BUILD = true; window.GD_BUILD = true;
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
/* parti che non servono su GameDistribution */
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
sost("const DA = (() => { const m = /[?&]da=", "const DA = (() => { if (window.CG_BUILD) return 'gamedistribution'; const m = /[?&]da=")
sost("vero = /github\\.io$/.test(location.hostname) && !/\\/beta\\//.test(location.pathname);", "vero = !!window.CG_BUILD || (/github\\.io$/.test(location.hostname) && !/\\/beta\\//.test(location.pathname));")

# 5) pulsante lingua nel pannello "Altro"
sost('''<button class="big alt" data-p="home">Indietro</button></div>`;
  } else if (pannello === 'profilo')''', '''<button class="big alt" onclick="cgPrivacy()">Privacy</button>
      ${window.CG_LINGUA === 'it' ? '<button class="big alt" onclick="cambiaLingua()">🌐 English</button>' : '<button class="big alt" onclick="cambiaLingua()">🌐 Italiano</button>'}
      <button class="big alt" data-p="home">Indietro</button></div>`;
  } else if (pannello === 'profilo')''')
sost('window.CG_BUILD = true;', '''window.CG_BUILD = true; window.CG_LINGUA = '@@LINGUA@@';
/* SDK di GameDistribution: pubblicità solo fuori dal gioco e dopo un tocco; durante la pubblicità il gioco tace */
(() => {
  let prima = null;
  const zitto = on => { try { const A = window.SUONI_CG; if (!A) return; if (on){ if (prima === null) prima = A.muto; window.CG_MUTO = true; A.muto = true; } else { window.CG_MUTO = false; if (prima !== null){ A.muto = prima; prima = null; } } } catch(e){} };
  window.GD_OPTIONS = { gameId: '@@GDID@@', onEvent: ev => {
    if (ev.name === 'SDK_GAME_PAUSE'){ zitto(true); document.body && document.body.classList.add('gd-pub'); }
    else if (ev.name === 'SDK_GAME_START'){ zitto(false); document.body && document.body.classList.remove('gd-pub'); } } };
  try { const sc = document.createElement('script'); sc.id = 'gamedistribution-jssdk'; sc.src = 'https://html5.api.gamedistribution.com/main.min.js'; document.head.appendChild(sc); } catch(e){}
  window.GD_PUB = () => { try { if (typeof gdsdk !== 'undefined' && typeof gdsdk.showAd !== 'undefined') gdsdk.showAd(); } catch(e){} };
  let giocato = false;
  window.CG_GP = on => { if (on) giocato = true; };
  let tocco = 0; for (const t of ['pointerup','keyup','touchend','click']) addEventListener(t, () => { tocco = Date.now(); }, true);
  window.GD_FRA = () => { if (giocato && Date.now() - tocco < 1500){ giocato = false; window.GD_PUB(); } };   // tra una partita e l'altra, solo subito dopo un tocco
  window.CG_CARICATO = () => {};
})();

/* privacy dentro il gioco (CrazyGames non permette link esterni) */
window.cgPrivacy = () => {
  const it = window.CG_LINGUA === 'it';
  const T = it ? {
    t: 'Privacy', agg: 'Ultimo aggiornamento: 23 novembre 2026',
    p: [['Chi è il responsabile', 'Natan Vitali, che ha creato il gioco. Per domande o richieste: Instagram <b>@smerillo_portal</b>.'],
        ['Progressi', 'I progressi e le impostazioni si salvano solo sul tuo dispositivo.'],
        ['Statistiche anonime', 'Contiamo le visite in modo anonimo: un codice casuale creato dal dispositivo, quando apri il gioco, le partite giocate, i passi della guida, la larghezza dello schermo e che arrivi da GameDistribution. Niente nome. Le teniamo sul nostro server (Supabase, Francoforte, UE) al massimo 24 mesi, per capire cosa migliorare.'],
        ['Partite con gli amici', 'Solo quando giochi online con il codice stanza, le mosse passano dal nostro server, legate solo al codice della stanza. Si cancellano da sole dopo alcune ore.'],
        ['Cosa non facciamo', 'Non chiediamo email, telefono, età o posizione. Non vendiamo né regaliamo dati a nessuno. La pubblicità la mostra GameDistribution: per i loro cookie e le loro scelte sulla privacy vale la privacy di GameDistribution.'],
        ['I tuoi diritti', 'Puoi chiederci di vedere, correggere o cancellare i dati, o di non usare le statistiche: scrivici su Instagram <b>@smerillo_portal</b>. Puoi anche fare reclamo al Garante per la protezione dei dati personali.']],
    ok: 'Chiudi' } : {
    t: 'Privacy', agg: 'Last updated: 23 November 2026',
    p: [['Who is responsible', 'Natan Vitali, who made the game. For questions or requests: Instagram <b>@smerillo_portal</b>.'],
        ['Progress', 'Your progress and settings are saved only on your device.'],
        ['Anonymous statistics', 'We count visits anonymously: a random code created by your device, when you open the game, matches played, guide steps, screen width and that you came from GameDistribution. No name. We keep them on our server (Supabase, Frankfurt, EU) for at most 24 months, to understand what to improve.'],
        ['Playing with friends', 'Only when you play online with a room code, the moves pass through our server, linked only to the room code. They are deleted automatically after a few hours.'],
        ['What we don\\'t do', 'We don\\'t ask for email, phone, age or location. We don\\'t sell or give data to anyone. Ads are shown by GameDistribution: their cookies and privacy choices follow the GameDistribution privacy policy.'],
        ['Your rights', 'You can ask us to see, correct or delete data, or to stop using statistics: message us on Instagram <b>@smerillo_portal</b>. You can also complain to your data protection authority.']],
    ok: 'Close' };
  const o = document.createElement('div');
  o.setAttribute('style', 'position:fixed;inset:0;z-index:2147483647;background:rgba(8,10,30,.82);display:flex;align-items:center;justify-content:center;padding:16px;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif');
  o.innerHTML = `<div style="background:#1b1f4b;color:#fff;border:3px solid #141433;border-radius:18px;max-width:560px;width:100%;max-height:88vh;overflow:auto;padding:20px 20px 16px;box-shadow:0 8px 0 #141433;line-height:1.45;font-size:15px">
    <h2 style="margin:0 0 2px;font-size:24px">${T.t}</h2><div style="opacity:.65;font-size:12px;margin-bottom:10px">Difendi Smerillo · ${T.agg}</div>
    ${T.p.map(([h, x]) => `<h3 style="margin:12px 0 3px;font-size:15px;color:#ffd03a">${h}</h3><p style="margin:0">${x}</p>`).join('')}
    <button type="button" style="margin-top:16px;width:100%;font:700 17px system-ui,sans-serif;color:#141433;background:#ffd03a;border:3px solid #141433;border-radius:14px;padding:10px;cursor:pointer">${T.ok}</button></div>`;
  o.querySelector('button').onclick = () => o.remove(); o.onclick = e => { if (e.target === o) o.remove(); };
  document.body.appendChild(o);
};
window.cambiaLingua = () => { try { localStorage.setItem('difendi-smerillo-lingua', window.CG_LINGUA === 'it' ? 'en' : 'it'); } catch(e){} location.reload(); };''')

sost("localStorage.setItem('difendi-smerillo-audio', v ? 'no' : 'si'); } catch(e){} } };\n})();", "localStorage.setItem('difendi-smerillo-audio', v ? 'no' : 'si'); } catch(e){} } };\n})();\nwindow.SUONI_CG = SUONI;")

# 5c) avvisi a CrazyGames: fine caricamento, inizio e fine partita; il loro "muto" vince sul nostro
sost("else { if (via){ via.hidden = false; via.onclick = esci; } else esci(); }", "else { if (via){ via.hidden = false; via.onclick = () => { try { window.GD_PUB && GD_PUB(); } catch(e){} esci(); }; } else esci(); }")
sost("function mostraMenu(", "function mostraMenu(){ try { window.GD_FRA && GD_FRA(); } catch(e){} return mostraMenu0.apply(this, arguments); }\nfunction mostraMenu0(")
sost("function nuovaPartita(", "function nuovaPartita(){ try { window.CG_GP && CG_GP(true); } catch(e){} return nuovaPartita0.apply(this, arguments); }\nfunction nuovaPartita0(")
sost("function apri(modo){ provenienza = 'menu';", "function apri(modo){ try { window.CG_GP && CG_GP(true); } catch(e){} provenienza = 'menu';")
sost("function apri(dopo){ APRI_DOPO = dopo || null;", "function apri(dopo){ try { window.CG_GP && CG_GP(true); } catch(e){} APRI_DOPO = dopo || null;")

sost("set muto(v){ muto = v;", "set muto(v){ if (!v && window.CG_MUTO) return; muto = v;")

# 6) testi in inglese (CrazyGames chiede l'inglese come lingua principale)
from traduci import traduci_html
s_en, n = traduci_html(s)
print('testi tradotti:', n)
s_it = s.replace('@@LINGUA@@', 'it').replace('@@GDID@@', GDID); s_en = s_en.replace('@@LINGUA@@', 'en').replace('@@GDID@@', GDID)

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
  apri();
  function apri(){{
  var L = null; try {{ L = localStorage.getItem('difendi-smerillo-lingua'); }} catch(e){{}}
  // lingua: quella che il giocatore ha scelto, se no quella del browser (italiano se è in italiano, se no inglese)
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
with zipfile.ZipFile(os.path.join(QUI, 'difendi-smerillo-gd.zip'), 'w', zipfile.ZIP_DEFLATED) as z: z.write(out, 'index.html')
print('game id:', GDID)
print('ok', out, round(len(s.encode()) / 1e6, 2), 'MB')
