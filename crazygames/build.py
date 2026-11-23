# Crea crazygames/index.html partendo dalla beta.
# Versione per CrazyGames (Basic Launch): niente account, niente server, niente link esterni,
# niente multiplayer online, niente richiesta "aggiungi alla Home". Salvataggio solo sul dispositivo.
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
  // nessuna chiamata a server esterni: classifiche, account, diario e aggiornamenti restano spenti
  const blocca = u => /supabase\.co|version\.json|unpkg\.com|jsdelivr\.net|github\.io/.test(String(u));
  const f0 = window.fetch.bind(window);
  window.fetch = (u, o) => blocca(u && u.url || u) ? Promise.resolve(new Response('null', {status: 503, headers: {'Content-Type': 'application/json'}})) : f0(u, o);
  window.open = () => null;
  try { localStorage.setItem('difendi-smerillo-home', '1'); localStorage.setItem('difendi-smerillo-voto', 'cg'); } catch(e){}
})();
</script>
<style id="cgNascondi">
/* parti che non servono su CrazyGames */
#tAmi, .cr-tab[data-tab="amici"], .cr-tab[data-tab="classifica"], #pfAcc, .fd-inv, .st-cond, .cl-card, #hmProf .pf-acc, [onclick*="privacy"], .acc-priv, #amInv { display: none !important; }
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
sost("['amici', 'amici', 'Amici', false], ['classifica', 'coppa', 'Classifica', false]];", "['amici', 'amici', 'Amici', false], ['classifica', 'coppa', 'Classifica', false]].filter(x => !window.CG_BUILD || (x[0] !== 'amici' && x[0] !== 'classifica'));")

sost("pgs = [...c.querySelectorAll('.cr-pg')];", "pgs = [...c.querySelectorAll('.cr-pg')].filter(p => !window.CG_BUILD || (p.dataset.tab !== 'amici' && p.dataset.tab !== 'classifica') || (p.remove(), false));")

out = os.path.join(QUI, 'index.html')
open(out, 'w', encoding='utf-8').write(s)
print('ok', out, round(len(s.encode()) / 1e6, 2), 'MB')
