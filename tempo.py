"""Traduz o que a pessoa escreve no campo Estimativa ("15 min", "1 hora", "1h30") em horas."""
import re
def parse(txt):
    if txt is None: return None
    t = txt.strip().lower().replace(",", ".")
    if not t: return None
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(?:h|hr|hrs|hora|horas)\s*(?:e\s*)?(\d+)?\s*(?:m|min|mins|minuto|minutos)?", t)
    if m: return float(m.group(1)) + (int(m.group(2)) / 60 if m.group(2) else 0)
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(?:m|min|mins|minuto|minutos)", t)
    if m: return float(m.group(1)) / 60
    m = re.fullmatch(r"(\d+):(\d{2})", t)
    if m: return int(m.group(1)) + int(m.group(2)) / 60
    m = re.fullmatch(r"\d+(?:\.\d+)?", t)
    if m:
        v = float(t)                    # numero sozinho: ate 8 = horas; acima disso = minutos
        return v if v <= 8 else v / 60
    return None
def fmt(h):
    mins = int(round(h * 60 / 5) * 5) if h else 0
    if h and mins == 0: mins = 5
    if mins < 60: return f"{mins} min"
    hh, mm = divmod(mins, 60)
    if mm == 0: return "1 hora" if hh == 1 else f"{hh} horas"
    return f"{hh}h{mm:02d}"
if __name__ == "__main__":
    for s in ["15 min","15 minutos","1 hora","2 horas","1h30","1h 30min","1 hora e 30 minutos","0","0 min","1,5h","45","2","1:30","5min","rapidinho",""]:
        print(repr(s), parse(s), fmt(parse(s)) if parse(s) is not None else None)
