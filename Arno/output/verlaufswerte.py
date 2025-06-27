########################################
# Beispiel: versicherungsmathematische 
# Excel-Formeln als Python-Funktionen
########################################

# Beispiel-Importe, passen Sie diese bitte
# an Ihre Projektstruktur und Modulnamen an.
from barwerte import act_ngr_ax, act_axn_k
from gwerte import act_dx

#
# 1. Hilfsfunktionen: Axn, axn, axt
#    (gemäß der Excel-Formeln in der Spalte „Beitragsberechnung“)
#

def calc_Axn(k, x, n, sex, tafel, zins):
    """
    Entspricht der Excel-Formel:
      Axn = WENN(k <= n;
                 act_nGrAx(x + k; max(0; n - k); sex; tafel; zins)
                 + Act_Dx(x + n; sex; tafel; zins) / Act_Dx(x + k; sex; tafel; zins);
                 0)
    (Angepasst auf: act_ngr_ax(...) und act_dx(...))
    """
    if k <= n:
        return (act_ngr_ax(x + k, max(0, n - k), sex, tafel, zins)
                + act_dx(x + n, sex, tafel, zins) 
                  / act_dx(x + k, sex, tafel, zins))
    else:
        return 0.0


def calc_axn(k, x, n, sex, tafel, zins):
    """
    Entspricht:
      axn = Act_axn_k(x + k; max(0; n - k); sex; tafel; zins; 1)
    (Angepasst auf: act_axn_k(...))
    """
    return act_axn_k(x + k, max(0, n - k), sex, tafel, zins, 1)


def calc_axt(k, x, t, sex, tafel, zins):
    """
    Entspricht:
      axt = Act_axn_k(x + k; max(0; t - k); sex; tafel; zins; 1)
    (Angepasst auf: act_axn_k(...))
    """
    return act_axn_k(x + k, max(0, t - k), sex, tafel, zins, 1)


#
# 2. kVx_bpfl
#    (Formel: B16 - P_xt*D16 + gamma2*(C16 - [Act_axn_k(x; n)/Act_axn_k(x; t)]*D16))
#

def calc_kVx_bpfl(k, x, n, t, sex, tafel, zins, P_xt, gamma2):
    """
    Entspricht der Excel-Formel (sinngemäß):
      kVx_bpfl = Axn - P_xt*axt
                 + gamma2 * (axn
                             - [Act_axn_k(x; n; ...)/Act_axn_k(x; t; ...)] * axt)
    wobei:
      Axn(k)  => calc_Axn
      axn(k)  => calc_axn
      axt(k)  => calc_axt
    """
    Axn_value = calc_Axn(k, x, n, sex, tafel, zins)
    axn_value = calc_axn(k, x, n, sex, tafel, zins)
    axt_value = calc_axt(k, x, t, sex, tafel, zins)

    ratio = (act_axn_k(x, n, sex, tafel, zins, 1)
             / act_axn_k(x, t, sex, tafel, zins, 1))

    return (Axn_value
            - P_xt * axt_value
            + gamma2 * (axn_value - ratio * axt_value))


#
# 3. kDRx_bpfl
#    (Formel: VS * E16; E16 = kVx_bpfl)
#

def calc_kDRx_bpfl(k, x, n, t, sex, tafel, zins, P_xt, gamma2, VS):
    """
    Entspricht:
      kDRx_bpfl = VS * kVx_bpfl
    """
    kVx_bpfl_value = calc_kVx_bpfl(k, x, n, t, sex, tafel, zins, P_xt, gamma2)
    return VS * kVx_bpfl_value


#
# 4. kVx_bfr
#    (Formel: B16 + gamma3*C16 => Axn + gamma3*axn)
#

def calc_kVx_bfr(k, x, n, t, sex, tafel, zins, gamma3):
    """
    Entspricht:
      kVx_bfr = Axn + gamma3*axn
    """
    Axn_value = calc_Axn(k, x, n, sex, tafel, zins)
    axn_value = calc_axn(k, x, n, sex, tafel, zins)
    return Axn_value + gamma3 * axn_value


#
# 5. kVx_MRV
#    (Formel: kDRx_bpfl + alpha*t*BJB*(Act_axn_k(x+k, max(5-k,0))/Act_axn_k(x,5)))
#

def calc_kVx_MRV(k, x, n, t, sex, tafel, zins, alpha, BJB, P_xt, gamma2, VS):
    """
    Entspricht:
      kVx_MRV = kDRx_bpfl + alpha*t*BJB
                * (act_axn_k(x+k, max(5-k, 0)) / act_axn_k(x, 5))
    """
    kDRx_bpfl_value = calc_kDRx_bpfl(k, x, n, t, sex, tafel, zins, P_xt, gamma2, VS)

    oben = act_axn_k(x + k, max(0, 5 - k), sex, tafel, zins, 1)
    unten = act_axn_k(x, 5, sex, tafel, zins, 1)

    return kDRx_bpfl_value + alpha * t * BJB * (oben / unten)


#
# 6. flex. Phase
#    (Formel: WENN(UND(x+k>=MinAlterFlex; k>=n-MinRLZFlex); 1; 0))
#

def calc_flex_phase(k, x, n, MinAlterFlex, MinRLZFlex):
    """
    Entspricht:
      flex_phase = 1, wenn (x+k >= MinAlterFlex) und (k>= n - MinRLZFlex), sonst 0
    """
    if (x + k >= MinAlterFlex) and (k >= n - MinRLZFlex):
        return 1
    else:
        return 0


#
# 7. StoAb
#    (Formel: WENN(ODER(k>n; flex_phase==1); 0; MIN(150; MAX(50; 1%*(VS - kDRx_bpfl))))
#

def calc_StoAb(k, x, n, t, sex, tafel, zins,
               P_xt, gamma2, VS,
               alpha, BJB, MinAlterFlex, MinRLZFlex):
    """
    Entspricht:
      StoAb = 0, wenn (k>n) oder (flex_phase == 1)
              sonst min(150, max(50, 1%*(VS - kDRx_bpfl)))
    """
    flex_phase_value = calc_flex_phase(k, x, n, MinAlterFlex, MinRLZFlex)
    kDRx_bpfl_value  = calc_kDRx_bpfl(k, x, n, t, sex, tafel, zins, P_xt, gamma2, VS)

    if (k > n) or (flex_phase_value == 1):
        return 0.0
    else:
        stoab_calc = 0.01 * (VS - kDRx_bpfl_value)  # = 1%*(VS - kDRx_bpfl)
        return min(150, max(50, stoab_calc))


#
# 8. RKW
#    (Formel: RKW = MAX(0; kVx_MRV - StoAb))
#

def calc_RKW(k, x, n, t, sex, tafel, zins,
             P_xt, gamma2, VS,
             alpha, BJB, MinAlterFlex, MinRLZFlex):
    """
    Entspricht:
      RKW = max(0, kVx_MRV - StoAb)
    """
    kVx_MRV_value = calc_kVx_MRV(k, x, n, t, sex, tafel, zins, alpha, BJB,
                                 P_xt, gamma2, VS)
    StoAb_value   = calc_StoAb(k, x, n, t, sex, tafel, zins,
                               P_xt, gamma2, VS,
                               alpha, BJB,
                               MinAlterFlex, MinRLZFlex)
    return max(0, kVx_MRV_value - StoAb_value)


#
# 9. VS_bfr
#    (Formel: WENNFEHLER(WENN(k>n; 0; WENN(k<t; kVx_MRV/kVx_bfr; VS)); 0))
#

def calc_VS_bfr(k, x, n, t, sex, tafel, zins,
                P_xt, gamma2, gamma3, VS,
                alpha, BJB, MinAlterFlex, MinRLZFlex):
    """
    Entspricht:
      VS_bfr = wenn(k>n, 0,
                    wenn(k<t, kVx_MRV/kVx_bfr, VS))
      (Fehlerfrei: bei Division durch 0 => 0)
    """
    kVx_MRV_value = calc_kVx_MRV(k, x, n, t, sex, tafel, zins,
                                 alpha, BJB, P_xt, gamma2, VS)
    kVx_bfr_value = calc_kVx_bfr(k, x, n, t, sex, tafel, zins, gamma3)

    if k > n:
        return 0.0
    else:
        if k < t:
            return (kVx_MRV_value / kVx_bfr_value) if (kVx_bfr_value != 0) else 0.0
        else:
            return VS
