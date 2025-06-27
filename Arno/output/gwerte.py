import xml.etree.ElementTree as ET
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
# Wir importieren hier constants und ggf. barwerte, falls benötigt
from constants import (
    RUND_LX,
    RUND_TX,
    RUND_DX,
    RUND_CX,
    RUND_NX,
    RUND_MX,
    RUND_RX,
    MAX_ALTER
)

##############################################################################
# EIGENE VBA-RUNDUNGSFUNKTION
##############################################################################

def vba_round(value, digits=0):
    """
    Rundet wie VBA/Excel: "Round-Half-Away-From-Zero".
    """
    dec_value = Decimal(str(value))
    if digits >= 0:
        quant_str = '1.' + ('0' * digits) if digits > 0 else '1'
    else:
        quant_str = f'1E{abs(digits)}'
    quant = Decimal(quant_str)
    return float(dec_value.quantize(quant, rounding=ROUND_HALF_UP))

##############################################################################
# GLOBALE DATENSTRUKTUREN (CACHE + Tafel-Daten)
##############################################################################
cache = {}
TAFELN_DATA = {}

##############################################################################
# HILFSFUNKTIONEN
##############################################################################

def initialize_cache():
    cache.clear()

def create_cache_key(art, alter, sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht):
    return f"{art}_{alter}_{sex}_{tafel}_{zins}_{geb_jahr}_{rentenbeginnalter}_{schicht}"

def _parse_tafeln_xml(xml_file="Tafeln.xml"):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    data = {}
    for rec in root.findall('record'):
        xy_tag = rec.find('xy')
        if xy_tag is None:
            continue
        try:
            alter = int(xy_tag.text)
        except (ValueError, TypeError):
            continue

        data[alter] = {}
        for child in rec:
            if child.tag == 'xy':
                continue
            try:
                val = float(child.text.replace(',', '.'))
            except (ValueError, AttributeError):
                val = 0.0

            data[alter][child.tag] = val
    return data

def _ensure_tafeln_data_loaded():
    global TAFELN_DATA
    if not TAFELN_DATA:  # noch leer
        TAFELN_DATA = _parse_tafeln_xml("Tafeln.xml")

##############################################################################
# WERTE AUS TAFELN AUSLESEN
##############################################################################

def act_qx(alter, sex, tafel, geb_jahr=None, rentenbeginnalter=None, schicht=1):
    _ensure_tafeln_data_loaded()
    if str(sex).upper() != "M":
        sex = "F"
    else:
        sex = "M"

    tafel_up = str(tafel).upper()
    if tafel_up not in ["DAV1994_T", "DAV2008_T"]:
        # VBA: Case else => qx=1 + Error
        raise ValueError(f"Unbekannte Tafel '{tafel}'.")

    s_tafelvektor = f"{tafel_up}_{sex}"

    if alter not in TAFELN_DATA:
        # Alter zu groß / nicht vorhanden => qx=1
        return 1.0

    if s_tafelvektor not in TAFELN_DATA[alter]:
        return 1.0

    return TAFELN_DATA[alter][s_tafelvektor]

##############################################################################
# "Private" Hilfsfunktionen (v_lx, v_tx, v_dx, etc.)
##############################################################################

def _v_lx(endalter, sex, tafel, geb_jahr=None, rentenbeginnalter=None, schicht=1):
    if endalter == -1:
        grenze = MAX_ALTER
    else:
        grenze = endalter

    vek = [0.0] * (grenze + 1)
    vek[0] = 1000000.0

    for i in range(1, grenze + 1):
        qx_val = act_qx(i - 1, sex, tafel, geb_jahr, rentenbeginnalter, schicht)
        lx_val = vek[i - 1] * (1.0 - qx_val)
        # Runden VBA-like:
        vek[i] = vba_round(lx_val, RUND_LX)

    return vek

def _v_tx(endalter, sex, tafel, geb_jahr=None, rentenbeginnalter=None, schicht=1):
    if endalter == -1:
        grenze = MAX_ALTER
    else:
        grenze = endalter

    vek = [0.0] * (grenze + 1)
    v_temp_lx = _v_lx(grenze, sex, tafel, geb_jahr, rentenbeginnalter, schicht)

    for i in range(grenze):
        tx_val = v_temp_lx[i] - v_temp_lx[i + 1]
        vek[i] = vba_round(tx_val, RUND_TX)

    return vek

def _v_dx(endalter, sex, tafel, zins, geb_jahr=None, rentenbeginnalter=None, schicht=1):
    if endalter == -1:
        grenze = MAX_ALTER
    else:
        grenze = endalter

    vek = [0.0] * (grenze + 1)
    v = 1.0 / (1.0 + zins)

    v_temp_lx = _v_lx(grenze, sex, tafel, geb_jahr, rentenbeginnalter, schicht)

    for i in range(grenze + 1):
        dx_val = v_temp_lx[i] * (v ** i)
        vek[i] = vba_round(dx_val, RUND_DX)

    return vek

def _v_cx(endalter, sex, tafel, zins, geb_jahr=None, rentenbeginnalter=None, schicht=1):
    if endalter == -1:
        grenze = MAX_ALTER
    else:
        grenze = endalter

    vek = [0.0] * (grenze + 1)
    v = 1.0 / (1.0 + zins)
    v_temp_tx = _v_tx(grenze, sex, tafel, geb_jahr, rentenbeginnalter, schicht)

    for i in range(grenze):
        cx_val = v_temp_tx[i] * (v ** (i + 1))
        vek[i] = vba_round(cx_val, RUND_CX)

    return vek

def _v_nx(sex, tafel, zins, geb_jahr=None, rentenbeginnalter=None, schicht=1):
    vek = [0.0] * (MAX_ALTER + 1)
    v_temp_dx = _v_dx(-1, sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht)

    vek[MAX_ALTER] = v_temp_dx[MAX_ALTER]
    for i in range(MAX_ALTER - 1, -1, -1):
        nx_val = vek[i + 1] + v_temp_dx[i]
        vek[i] = vba_round(nx_val, RUND_NX)

    return vek

def _v_mx(sex, tafel, zins, geb_jahr=None, rentenbeginnalter=None, schicht=1):
    vek = [0.0] * (MAX_ALTER + 1)
    v_temp_cx = _v_cx(-1, sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht)

    vek[MAX_ALTER] = v_temp_cx[MAX_ALTER]
    for i in range(MAX_ALTER - 1, -1, -1):
        mx_val = vek[i + 1] + v_temp_cx[i]
        vek[i] = vba_round(mx_val, RUND_MX)

    return vek

def _v_rx(sex, tafel, zins, geb_jahr=None, rentenbeginnalter=None, schicht=1):
    vek = [0.0] * (MAX_ALTER + 1)
    v_temp_mx = _v_mx(sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht)

    vek[MAX_ALTER] = v_temp_mx[MAX_ALTER]
    for i in range(MAX_ALTER - 1, -1, -1):
        rx_val = vek[i + 1] + v_temp_mx[i]
        vek[i] = vba_round(rx_val, RUND_RX)

    return vek

##############################################################################
# ÖFFENTLICHE FUNKTIONEN (analog VBA Public)
##############################################################################

def act_lx(alter, sex, tafel, geb_jahr=None, rentenbeginnalter=None, schicht=1):
    vek = _v_lx(alter, sex, tafel, geb_jahr, rentenbeginnalter, schicht)
    return vek[alter]

def act_tx(alter, sex, tafel, geb_jahr=None, rentenbeginnalter=None, schicht=1):
    vek = _v_tx(alter, sex, tafel, geb_jahr, rentenbeginnalter, schicht)
    return vek[alter]

def act_dx(alter, sex, tafel, zins, geb_jahr=None, rentenbeginnalter=None, schicht=1):
    s_key = create_cache_key("Dx", alter, sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht)
    if s_key in cache:
        return cache[s_key]
    else:
        vek = _v_dx(alter, sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht)
        result = vek[alter]
        cache[s_key] = result
        return result

def act_cx(alter, sex, tafel, zins, geb_jahr=None, rentenbeginnalter=None, schicht=1):
    s_key = create_cache_key("Cx", alter, sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht)
    if s_key in cache:
        return cache[s_key]
    else:
        vek = _v_cx(alter, sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht)
        result = vek[alter]
        cache[s_key] = result
        return result

def act_nx(alter, sex, tafel, zins, geb_jahr=None, rentenbeginnalter=None, schicht=1):
    s_key = create_cache_key("Nx", alter, sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht)
    if s_key in cache:
        return cache[s_key]
    else:
        vek = _v_nx(sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht)
        result = vek[alter]
        cache[s_key] = result
        return result

def act_mx(alter, sex, tafel, zins, geb_jahr=None, rentenbeginnalter=None, schicht=1):
    s_key = create_cache_key("Mx", alter, sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht)
    if s_key in cache:
        return cache[s_key]
    else:
        vek = _v_mx(sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht)
        result = vek[alter]
        cache[s_key] = result
        return result

def act_rx(alter, sex, tafel, zins, geb_jahr=None, rentenbeginnalter=None, schicht=1):
    s_key = create_cache_key("Rx", alter, sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht)
    if s_key in cache:
        return cache[s_key]
    else:
        vek = _v_rx(sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht)
        result = vek[alter]
        cache[s_key] = result
        return result

def act_altersberechnung(geb_dat, ber_dat, methode):
    if methode != "K":
        methode = "H"

    j_gd = geb_dat.year
    j_bd = ber_dat.year
    m_gd = geb_dat.month
    m_bd = ber_dat.month

    if methode == "K":
        return j_bd - j_gd
    else:
        return int((j_bd - j_gd) + (1.0 / 12.0) * (m_bd - m_gd + 5))
