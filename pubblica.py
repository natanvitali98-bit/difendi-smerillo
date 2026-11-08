# Mette un numero di versione nuovo nel gioco e in version.json (da lanciare prima di ogni commit del gioco)
import json, time, re, pathlib
v = time.strftime('%Y%m%d%H%M%S')
p = pathlib.Path(__file__).with_name('index.html'); s = p.read_text()
s, n = re.subn(r"const VERSIONE = window\.DS_VER = '\d*';", f"const VERSIONE = window.DS_VER = '{v}';", s, count=1)
assert n == 1, 'versione non trovata'
p.write_text(s); p.with_name('version.json').write_text(json.dumps({'v': v}) + '\n')
print(v)
