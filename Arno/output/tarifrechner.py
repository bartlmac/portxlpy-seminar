import openpyxl

from barwerte import act_ngr_ax, act_axn_k
from gwerte import act_dx

from verlaufswerte import (
    calc_Axn,
    calc_axn,
    calc_axt,
    calc_kVx_bpfl,
    calc_kDRx_bpfl,
    calc_kVx_bfr,
    calc_kVx_MRV,
    calc_flex_phase,
    calc_StoAb,
    calc_RKW,
    calc_VS_bfr
)

def calc_Bxt(x, n, t, sex, tafel, zins, alpha, beta1, gamma1, gamma2):
    numerator = (
        act_ngr_ax(x, n, sex, tafel, zins)
        + act_dx(x + n, sex, tafel, zins) / act_dx(x, sex, tafel, zins)
        + gamma1 * act_axn_k(x, t, sex, tafel, zins, 1)
        + gamma2 * (
            act_axn_k(x, n, sex, tafel, zins, 1)
            - act_axn_k(x, t, sex, tafel, zins, 1)
        )
    )
    denominator = (
        (1 - beta1) * act_axn_k(x, t, sex, tafel, zins, 1)
        - alpha * t
    )
    return numerator / denominator

def calc_BJB(VS, Bxt_value):
    return VS * Bxt_value

def calc_BZB(ratzu, zw, BJB_value, k_val):
    return (1 + ratzu) / zw * (BJB_value + k_val)

def calc_Pxt(x, n, t, sex, tafel, zins, alpha, Bxt_value):
    numerator = (
        act_ngr_ax(x, n, sex, tafel, zins)
        + act_dx(x + n, sex, tafel, zins) / act_dx(x, sex, tafel, zins)
        + t * alpha * Bxt_value
    )
    denominator = act_axn_k(x, t, sex, tafel, zins, 1)
    return numerator / denominator

def main():
    wb = openpyxl.load_workbook("Tarifrechner_KLV_Eingabe.xlsx", data_only=True)
    sheet = wb["Kalkulation"]

    # Eingabedaten (Zeilen 4..9 in Spalte B usw.)
    x            = sheet["B4"].value
    sex          = sheet["B5"].value
    n            = sheet["B6"].value
    t            = sheet["B7"].value
    VS           = sheet["B8"].value
    zw           = sheet["B9"].value

    # Tarifdaten (Spalte E, Zeilen 4..12)
    zins         = sheet["E4"].value
    tafel        = sheet["E5"].value
    alpha        = sheet["E6"].value
    beta1        = sheet["E7"].value
    gamma1       = sheet["E8"].value
    gamma2       = sheet["E9"].value
    gamma3       = sheet["E10"].value
    k_val        = sheet["E11"].value
    ratzu        = sheet["E12"].value

    # Grenzen in Spalte H (z.B. Zeilen 4 und 5)
    MinAlterFlex = sheet["H4"].value  # z.B. 60
    MinRLZFlex   = sheet["H5"].value  # z.B. 5

    wb.close()

    # --- Beitragsberechnung ---
    Bxt_value = calc_Bxt(x, n, t, sex, tafel, zins, alpha, beta1, gamma1, gamma2)
    BJB_value = calc_BJB(VS, Bxt_value)
    BZB_value = calc_BZB(ratzu, zw, BJB_value, k_val)
    Pxt_value = calc_Pxt(x, n, t, sex, tafel, zins, alpha, Bxt_value)

    print("=== Beitragsberechnung ===")
    print(f"Bxt = {Bxt_value:12.8f}")
    print(f"BJB = {BJB_value:12.2f}")
    print(f"BZB = {BZB_value:12.2f}")
    print(f"Pxt = {Pxt_value:12.8f}")
    print()

    # --- Verlaufswerte ---
    print("=== Verlaufswerte (k = 0..n) ===")
    print("k\tAxn\t\taxn\t\taxt\t\tkVx_bpfl\tkDRx_bpfl\tkVx_bfr\t\tkVx_MRV\t\tflexPh\tStoAb\t\tRKW\t\tVS_bfr")

    for k in range(n + 1):
        Axn_val       = calc_Axn(k, x, n, sex, tafel, zins)
        axn_val       = calc_axn(k, x, n, sex, tafel, zins)
        axt_val       = calc_axt(k, x, t, sex, tafel, zins)
        kVx_bpfl_val  = calc_kVx_bpfl(k, x, n, t, sex, tafel, zins, Pxt_value, gamma2)
        kDRx_bpfl_val = calc_kDRx_bpfl(k, x, n, t, sex, tafel, zins, Pxt_value, gamma2, VS)
        kVx_bfr_val   = calc_kVx_bfr(k, x, n, t, sex, tafel, zins, gamma3)
        kVx_MRV_val   = calc_kVx_MRV(k, x, n, t, sex, tafel, zins, alpha, BJB_value,
                                     Pxt_value, gamma2, VS)
        flex_val      = calc_flex_phase(k, x, n, MinAlterFlex, MinRLZFlex)
        StoAb_val     = calc_StoAb(k, x, n, t, sex, tafel, zins,
                                   Pxt_value, gamma2, VS,
                                   alpha, BJB_value,
                                   MinAlterFlex, MinRLZFlex)
        RKW_val       = calc_RKW(k, x, n, t, sex, tafel, zins,
                                 Pxt_value, gamma2, VS,
                                 alpha, BJB_value,
                                 MinAlterFlex, MinRLZFlex)
        VS_bfr_val    = calc_VS_bfr(k, x, n, t, sex, tafel, zins,
                                    Pxt_value, gamma2, gamma3, VS,
                                    alpha, BJB_value,
                                    MinAlterFlex, MinRLZFlex)

        print(f"{k}\t"
              f"{Axn_val:10.6f}\t"
              f"{axn_val:10.6f}\t"
              f"{axt_val:10.6f}\t"
              f"{kVx_bpfl_val:10.6f}\t"
              f"{kDRx_bpfl_val:10.2f}\t"
              f"{kVx_bfr_val:10.6f}\t"
              f"{kVx_MRV_val:10.2f}\t"
              f"{flex_val}\t"
              f"{StoAb_val:10.2f}\t"
              f"{RKW_val:10.2f}\t"
              f"{VS_bfr_val:10.2f}"
        )

if __name__ == "__main__":
    main()
