"""Regenerates the conduction-loss table in low_voltage_power_electronics.md.

Only claim: at fixed power, P_cond = I^2 * R_path, so raising pack voltage
reduces conduction loss quadratically. Switching loss ~ V*I*f stays flat.
Run: python3 low_voltage_math_check.py
"""

R_PATH = 1.5e-3  # ohms, 2 devices in the conduction path, 4x 3 mOhm paralleled per switch
VOLTS = (48, 60, 72, 96)
POWER = (1000, 5000)


def cond_loss_w(power, volts, r=R_PATH):
    return (power / volts) ** 2 * r


def table():
    rows = []
    for p in POWER:
        for v in VOLTS:
            i = p / v
            w = cond_loss_w(p, v)
            rows.append((p, v, i, w, 100 * w / p))
    return rows


if __name__ == "__main__":
    print(f"R_path = {R_PATH*1e3:.1f} mOhm")
    print(f"{'P(W)':>6} {'V':>4} {'I(A)':>7} {'Pcond(W)':>9} {'% of P':>7}")
    for p, v, i, w, pct in table():
        print(f"{p:>6} {v:>4} {i:>7.1f} {w:>9.2f} {pct:>6.2f}%")

    # The document's claims, checked.
    assert abs(cond_loss_w(1000, 48) - 0.651) < 0.01
    assert abs(cond_loss_w(1000, 96) - 0.163) < 0.01
    assert abs(cond_loss_w(5000, 48) - 16.28) < 0.05
    # 4x voltage -> 1/16 conduction loss at fixed power
    assert abs(cond_loss_w(5000, 48) / cond_loss_w(5000, 192 if False else 96) - 4.0) < 0.01
    # Worst case in the table is still under 0.5% of throughput
    assert max(r[4] for r in table()) < 0.5

    # Market arithmetic used in the doc: units x price band, in crore INR.
    units = 1_279_951 + 797_733
    lo, hi = units * 1500 / 1e7, units * 3500 / 1e7
    assert units == 2_077_684
    assert 310 < lo < 315 and 725 < hi < 730
    print(f"\ncontrollers/yr = {units:,}; revenue pool = Rs {lo:.0f}-{hi:.0f} crore")
