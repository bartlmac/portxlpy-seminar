# barwerte.py

from gwerte import act_nx, act_dx, act_mx


def act_abzugsglied(k: int, zins: float) -> float:
    """
    Entspricht der VBA-Funktion Act_Abzugsglied(k, Zins).
    
    In VBA:
        For l = 0 To k - 1
            Act_Abzugsglied = Act_Abzugsglied + l / k / (1 + l / k * Zins)
        Next l
        Act_Abzugsglied = Act_Abzugsglied * (1 + Zins) / k
    """
    result = 0.0
    if k > 0:
        for l in range(k):
            result += (l / k) / (1 + (l / k) * zins)
        result = result * (1 + zins) / k
    return result


def act_ax_k(
    alter: int,
    sex: str,
    tafel: str,
    zins: float,
    k: int,
    geb_jahr: int = None,
    rentenbeginnalter: int = None,
    schicht: int = 1
) -> float:
    """
    Entspricht VBA-Funktion Act_ax_k:
       If k > 0 Then
          Act_ax_k = Act_Nx(...) / Act_Dx(...) - Act_Abzugsglied(k, Zins)
       Else
          Act_ax_k = 0
       End If
    """
    if k > 0:
        return (
            act_nx(alter, sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht)
            / act_dx(alter, sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht)
            - act_abzugsglied(k, zins)
        )
    else:
        return 0.0


def act_axn_k(
    alter: int,
    n: int,
    sex: str,
    tafel: str,
    zins: float,
    k: int,
    geb_jahr: int = None,
    rentenbeginnalter: int = None,
    schicht: int = 1
) -> float:
    """
    Entspricht VBA-Funktion Act_axn_k:
       If k > 0 Then
          Act_axn_k = (Act_Nx(alter) - Act_Nx(alter+n)) / Act_Dx(alter)
                      - Act_Abzugsglied(k, Zins) * (1 - Act_Dx(alter+n)/Act_Dx(alter))
       Else
          Act_axn_k = 0
       End If
    """
    if k > 0:
        nx_alter = act_nx(alter, sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht)
        nx_alter_n = act_nx(
            alter + n, sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht
        )
        dx_alter = act_dx(alter, sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht)
        dx_alter_n = act_dx(
            alter + n, sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht
        )
        
        return (
            (nx_alter - nx_alter_n) / dx_alter
            - act_abzugsglied(k, zins) * (1 - dx_alter_n / dx_alter)
        )
    else:
        return 0.0


def act_nax_k(
    alter: int,
    n: int,
    sex: str,
    tafel: str,
    zins: float,
    k: int,
    geb_jahr: int = None,
    rentenbeginnalter: int = None,
    schicht: int = 1
) -> float:
    """
    Entspricht VBA-Funktion Act_nax_k:
       If k > 0 Then
          Act_nax_k = Act_Dx(alter+n)/Act_Dx(alter) * Act_ax_k(alter+n, ...)
       Else
          Act_nax_k = 0
       End If
    """
    if k > 0:
        dx_alter = act_dx(alter, sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht)
        dx_alter_n = act_dx(
            alter + n, sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht
        )
        return (
            dx_alter_n / dx_alter
            * act_ax_k(
                alter + n, sex, tafel, zins, k, geb_jahr, rentenbeginnalter, schicht
            )
        )
    else:
        return 0.0


def act_ngr_ax(
    alter: int,
    n: int,
    sex: str,
    tafel: str,
    zins: float,
    geb_jahr: int = None,
    rentenbeginnalter: int = None,
    schicht: int = 1
) -> float:
    """
    Entspricht VBA-Funktion Act_nGrAx:
       (Act_Mx(alter) - Act_Mx(alter + n)) / Act_Dx(alter)
    """
    mx_alter = act_mx(alter, sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht)
    mx_alter_n = act_mx(
        alter + n, sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht
    )
    dx_alter = act_dx(alter, sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht)
    return (mx_alter - mx_alter_n) / dx_alter


def act_ngr_ex(
    alter: int,
    n: int,
    sex: str,
    tafel: str,
    zins: float,
    geb_jahr: int = None,
    rentenbeginnalter: int = None,
    schicht: int = 1
) -> float:
    """
    Entspricht VBA-Funktion Act_nGrEx:
       Act_Dx(alter + n)/Act_Dx(alter)
    """
    dx_alter = act_dx(alter, sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht)
    dx_alter_n = act_dx(
        alter + n, sex, tafel, zins, geb_jahr, rentenbeginnalter, schicht
    )
    return dx_alter_n / dx_alter


def act_ag_k(g: int, zins: float, k: int) -> float:
    """
    Entspricht VBA-Funktion Act_ag_k:
       v = 1/(1+Zins)
       If k > 0 Then
          If Zins > 0 Then
             act_ag_k = (1 - v^g) / (1 - v) - Act_Abzugsglied(k, Zins) * (1 - v^g)
          Else
             act_ag_k = g
          End If
       Else
          act_ag_k = 0
       End If
    """
    if k <= 0:
        return 0.0

    if zins == 0.0:
        # Falls zins = 0, direkt g zurückgeben (analog VBA-Logik)
        return float(g)

    v = 1.0 / (1.0 + zins)
    return ((1 - v**g) / (1 - v)) - act_abzugsglied(k, zins) * (1 - v**g)
