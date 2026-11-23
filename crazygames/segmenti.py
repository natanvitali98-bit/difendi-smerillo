# Trova i pezzi di testo visibile dentro una stringa (fuori dai tag HTML).
import json,re
WORD=re.compile(r"[A-Za-zÀ-ÿ’']{2,}")
def testo(t):
    u=t.strip()
    if not WORD.search(u): return False
    if re.search(r'\d+px|^[a-z0-9\-]+( [a-z0-9\-]+)*$' ,u) and not re.search(r'[àèéìòù]',u) and (('-' in u) or len(u.split())<=1): return False
    if re.search(r'[{};=]|=>|\(\)|^\.|^#|https?:|\.(png|jpg|mp3|js|css)\b',u): return False
    if re.fullmatch(r"[A-ZÀ-Ý][a-zà-ÿ’']+[!?.…:,]*",u): return True
    if re.fullmatch(r"[a-z0-9_\-]+",u): return False
    if ' ' in u and re.search(r"[a-zà-ÿ]{2,}",u): return True
    if re.search(r'[àèéìòù]',u): return True
    return False
TAG=re.compile(r'<[^<>]*>')
ATTR=re.compile(r'\b(alt|title|placeholder|aria-label|data-tip|value)="([^"]*)"')
def segmenti(v):
    """ritorna lista di (inizio,fine) nel valore v da tradurre"""
    out=[]
    # parti tag: attributi visibili
    pos=0; spans=[]
    m0=re.match(r'^[^<>]*>',v)
    if m0 and (('="' in m0.group()) or m0.group().lstrip().startswith('"') or re.match(r'^\s*[a-z\-]+=',m0.group())): spans.append((0,m0.end()))
    for m in TAG.finditer(v): spans.append(m.span())
    m1=re.search(r'<[^<>]*$',v)
    if m1: spans.append(m1.span())
    # also a fragment that ends inside attribute like ' class="x" data-y="'  (no < >)
    if not spans and re.search(r'^\s*[a-z\-]+="|="\s*$|^"\s*[a-z\-]+=',v): return []
    spans.sort()
    for a,b in spans:
        for m in ATTR.finditer(v[a:b]):
            if testo(m.group(2)): out.append((a+m.start(2),a+m.end(2)))
    # testo fuori dai tag
    last=0
    for a,b in spans+[(len(v),len(v))]:
        if a>last:
            t=v[last:a]
            if testo(t):
                lead=len(t)-len(t.lstrip(' \n\t>')); trail=len(t.rstrip(' \n\t<'))
                out.append((last+lead,last+trail))
        last=max(last,b)
    return out

# ---- secondo passaggio: pezzi rimasti fuori (frasi dopo un punto, MAIUSCOLE, parole singole tra i tag)
import json as _json, os as _os
_VOC = None
def _voc():
    global _VOC
    if _VOC is None:
        try: D = _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'en.json'), encoding='utf-8'))
        except Exception: D = {}
        en = set(w.lower() for v in D.values() for w in re.findall(r"[A-Za-z]+", v))
        _VOC = set(w.lower() for k in D for w in re.findall(r"[a-zà-ÿ]{4,}", k.lower())) - en
    return _VOC
IT = re.compile(r"\b(di|il|la|le|lo|gli|che|non|per|con|una|uno|dei|delle|della|dalla|dal|nel|nella|sono|hai|ha|tocca|ancora|anche|più|già|ogni|tuo|tua|tuoi|questa|questo|si|se|ti|ci|ne|ma|poi|qui|ora)\b|[àèéìòù]", re.I)
def italiano(u):
    if IT.search(u): return True
    return any(w.lower() in _voc() for w in re.findall(r"[A-Za-zà-ÿ]{4,}", u))
def testo2(u, intero):
    if not re.search(r"[A-Za-zÀ-ÿ]{2,}", u): return False
    if re.search(r'[{};=<>]|=>|https?:|\.(png|jpg|mp3|js|css)\b|\d+px', u): return False
    if re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)+', u): return False
    if intero and re.fullmatch(r"[a-zà-ÿ’']+[.:!)]?", u): return False   # una parola sola minuscola: può essere una chiave
    return italiano(u)
def segmenti2(v):
    gia = segmenti(v)
    out = []
    spans = [m.span() for m in TAG.finditer(v)]
    m0 = re.match(r'^[^<>]*>', v)
    if m0: spans.insert(0, (0, m0.end()))
    m1 = re.search(r'<[^<>]*$', v)
    if m1: spans.append(m1.span())
    if not spans and re.search(r'^\s*[a-z\-]+="|="\s*$|^"\s*[a-z\-]+=', v): return []
    last = 0
    for a, b in sorted(spans) + [(len(v), len(v))]:
        if a > last:
            t = v[last:a]
            lead = len(t) - len(t.lstrip(' \n\t>.,;:!?)·'))
            trail = len(t.rstrip(' \n\t<(·'))
            A, B = last + lead, last + trail
            if B > A and not any(x <= A < y or x < B <= y for x, y in gia):
                u = v[A:B]
                intero = A == 0 and B == len(v) and len(v.strip()) == len(v)
                if re.fullmatch(r"[A-Za-zà-ÿ’']+[.:!)]?", u) and not re.search(r'[<>]|^\s|\s$', v): intero = True
                if re.search(r'[_:#\[\]|]|\d[a-z]|[a-z]\d|--', u): continue
                if testo2(u, intero): out.append((A, B))
        last = max(last, b)
    return out
