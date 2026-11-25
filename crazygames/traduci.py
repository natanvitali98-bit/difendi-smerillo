# Traduce in inglese i testi visibili del gioco (solo per la versione CrazyGames).
# Usa en.json (italiano -> inglese). Le stringhe JS vengono trovate con acorn (estrai.js),
# cosi' si toccano solo i testi e mai il codice.
import json, re, os, subprocess, sys
QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
from segmenti import segmenti, segmenti2

def traduci_valore(v, D):
    out = v
    for a, b in sorted(segmenti(v) + segmenti2(v), reverse=True):
        t = D.get(v[a:b])
        if t is not None: out = out[:a] + t + out[b:]
    return out

def esc_str(v, q):
    v = v.replace('\\', '\\\\').replace(q, '\\' + q).replace('\n', '\\n').replace('\r', '\\r').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    return q + v + q

def esc_tpl(v):
    return v.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

# parole singole usate come valori (non si possono tradurre in automatico senza rischiare le chiavi)
FISSI = [
    ("'Ondate respinte: ' + n + ' di ' + ONDATE", "'Waves held: ' + n + ' of ' + ONDATE"),
    ("Queste due strade sono corte: tieni qualcuno vicino alla <b>chiesetta</b>.'", "These two roads are short: keep someone near the <b>little church</b>.'"),
    ("'🟡 <b>Costruisci</b> (legno ' + S.legname + ')' : T.ferma ? '🎯 <b>Ferma</b>' : '🎯 <b>Colpisci</b> il rosso'", "'🟡 <b>Build</b> (wood ' + S.legname + ')' : T.ferma ? '🎯 <b>Block</b>' : '🎯 <b>Hit</b> the red one'"),
    ("' Passo' + (m ? ' · <b>Scatto</b>: ancora 1' : '') : m ? '🟢 <b>Vai</b> sul verde' : '–'} · ${u.agito ? ico('ok') + ' Azione'", "' Step' + (m ? ' · <b>Dash</b>: 1 more' : '') : m ? '🟢 <b>Go</b> to green' : '–'} · ${u.agito ? ico('ok') + ' Action'"),
    ("'Legno finito' : 'Nessuno vicino'}", "'No wood left' : 'Nobody near'}"),
    ("<small>Benvenuto a</small>Smerillo</div>'", "<small>Welcome to</small>Smerillo</div>'"),
    ("${f ? 'Il tuo regalo' : 'Per chi giochi?'}", "${f ? 'Your gift' : 'Who do you play for?'}"),
    ("NOMEG = {legno:'legno', argento:'argento', oro:'oro'}", "NOMEG = {legno:'wood', argento:'silver', oro:'gold'}"),
    ("`Sconfiggi ${n} ${n === 1 ? 'volta' : 'volte'} il Cavaliere Nero`", "`Defeat the Black Knight ${n} ${n === 1 ? 'time' : 'times'}`"),
    ("'liv. ' + d.liv", "'lv. ' + d.liv"),
    ("g.s === 1 ? 'giorno' : 'giorni'", "g.s === 1 ? 'day' : 'days'"),
    ("const sol = n => n === 1 ? '1 soldato' : n + ' soldati';", "const sol = n => n === 1 ? '1 soldier' : n + ' soldiers';"),
    ("(m === 1 ? 'moneta' : 'monete') : '', c ? c + ' cibo' : '', l ? l + ' legna' : ''].filter(Boolean).join(', ') + ' a stagione'", "(m === 1 ? 'coin' : 'coins') : '', c ? c + ' food' : '', l ? l + ' wood' : ''].filter(Boolean).join(', ') + ' per season'"),
    ("testo:`${FZ[f].corto} costruisce: ${ED[k].nome} livello ${F.ed[k]}`", "testo:`${FZ[f].corto} builds: ${ED[k].nome} level ${F.ed[k]}`"),
    ("testo:`${FZ[f].corto} costruisce: ${STR[k].nome}${lv ? ' livello ' + (lv + 1) : ''} a ${TERRE[t].nome}`", "testo:`${FZ[f].corto} builds: ${STR[k].nome}${lv ? ' level ' + (lv + 1) : ''} in ${TERRE[t].nome}`"),
    (" Guida l’attacco ${capNome(r.cap)}.` : ''", " Led by ${capNome(r.cap)}.` : ''", 2),
    ("match(/Guida l’attacco (.+)\\./)", "match(/Led by (.+)\\./)"),
    ("`Respinto ${resp === 1 ? '1 volta' : resp + ' volte'}`", "`Pushed back ${resp === 1 ? 'once' : resp + ' times'}`"),
    ("replace(/La tua casata/g, 'La casata ' + nm).replace(/la tua casata/g, 'la casata ' + nm)", "replace(/Your house/g, 'The house ' + nm).replace(/your house/g, 'the house ' + nm)"),
    ("replace(/^(Simbolo|Colore|Forma) /, '')", "replace(/ (symbol|colour|shape)$/, '')", 2),
    ("replace(/^(Stemma|Scudo) «(.*)»$/, '$2')", "replace(/^(Crest|Shield) «(.*)»$/, '$2')"),
    ("'DIFENDI'", "'DEFEND'", 3),
    ("t = '<b>▶ VIA!</b>'", "t = '<b>▶ GO!</b>'"),
    ('<div class="ld-logo"><span>Difendi</span>', '<div class="ld-logo"><span>Difendi\u200b</span>'),   # il titolo del gioco resta "Difendi Smerillo"
    ("strDet(st.str, 'danneggiato', 'danneggiata')", "strDet(st.str, 'damaged', 'damaged')"),
    ("strDet(dn.k, 'distrutto', 'distrutta')", "strDet(dn.k, 'destroyed', 'destroyed')"),
    ("strDet(dn.k, 'danneggiato', 'danneggiata')", "strDet(dn.k, 'damaged', 'damaged')"),
    ("strDet(d.k, 'distrutto', 'distrutta')", "strDet(d.k, 'destroyed', 'destroyed')"),
    ("strDet(d.k, 'danneggiato', 'danneggiata')", "strDet(d.k, 'damaged', 'damaged')"),
]
# singolare/plurale scelti con  n === 1 ? 'x' : 'y'  (solo queste coppie: sono testi, non chiavi)
PLURALI = {('stagione','stagioni'):('season','seasons'), ('soldato','soldati'):('soldier','soldiers'), ('mossa','mosse'):('move','moves'),
    ('diserta','disertano'):('deserts','desert'), ('volta','volte'):('time','times'), ('turno','turni'):('turn','turns'), ('tappa','tappe'):('stage','stages'),
    ('piano','piani'):('floor','floors'), ('persa','perse'):('lost','lost'), ('pensa','pensano'):('thinks','think'), ('moneta','monete'):('coin','coins'),
    ('difesa','difese'):('held','held'), ('brigante','briganti'):('bandit','bandits'), ('nemico','nemici'):('enemy','enemies')}

def traduci_html(s):
    for x in FISSI:
        a, b, n = (x + (1,))[:3]
        if s.count(a) != n: sys.exit(f'ERRORE traduzione fissa ({s.count(a)} invece di {n}): ' + a[:60])
        s = s.replace(a, b)
    s = re.sub(r"\? *'([a-zà-ù]+)' *: *'([a-zà-ù]+)'", lambda m: "? '%s' : '%s'" % PLURALI[(m[1], m[2])] if (m[1], m[2]) in PLURALI else m[0], s)
    s = re.sub(r'(?<=[>\s])liv\. (?=\$\{)', 'lv. ', s)
    D = json.load(open(os.path.join(QUI, 'en.json'), encoding='utf-8'))
    tmp = os.path.join(QUI, '.tmp.html'); open(tmp, 'w', encoding='utf-8').write(s)
    L = json.loads(subprocess.run(['node', os.path.join(QUI, 'estrai.js'), tmp], capture_output=True, text=True, check=True).stdout)
    os.remove(tmp)
    # le posizioni di acorn sono in unità UTF-16: converto in indici Python
    u16 = []; 
    for i, ch in enumerate(s):
        u16.append(i)
        if ord(ch) > 0xFFFF: u16.append(i)
    u16.append(len(s))
    rep = []
    for x in L:
        v = x['v']
        if v is None or v.startswith('data:') or len(v) > 20000: continue
        n = traduci_valore(v, D)
        if n == v: continue
        a, b = u16[x['a']], u16[x['b']]
        if x['k'] == 's': rep.append((a, b, esc_str(n, s[a])))
        else: rep.append((a, b, esc_tpl(n)))
    # testo HTML fuori da script e style
    for m in re.finditer(r'(?s)(?:^|</script>|</style>)(.*?)(?=<script|<style|$)', s):
        a, b = m.span(1)
        if b > a:
            n = traduci_valore(s[a:b], D)
            if n != s[a:b]: rep.append((a, b, n))
    rep.sort(reverse=True)
    for a, b, n in rep: s = s[:a] + n + s[b:]
    s = s.replace('<html lang="it"', '<html lang="en"')
    return s, len(rep)
