# BSE Sensex Platform: Phase-Wise Rollback Strategy & Registry

This document establishes the mandatory **Rollback Strategy, Commit Hash Registry, and Deployment Safety Protocol** for the **BSE Sensex Sentry Engine**.

---

## 📋 Phase-Wise Rollback Hash Registry (Sensex)

| Phase Tag | Release Date | Git Commit Hash | Scope / Key Changes | Rollback Target Hash |
| :--- | :---: | :---: | :--- | :--- |
| **`Phase 3.0 (Sensex)`** | 2026-08-02 | **`3.0 Release`** | Micro-Trailing Engine (Level 1 Breakeven Lock at +15-20 pts, Level 2 Dynamic 20-pt Trail at +40 pts), 3-min Cooldown, Opposing Wick Filter, 30-min Circuit Breaker, Ghost SL Lock Clearing. | **`023216c`** (Phase 1.1) |
| **`Phase 1.1 (Sensex)`** | 2026-08-02 | **`023216c`** | Realized Net PnL Win-Rate Scorecard Alignment + True OHLCV Body Delta (|Close - Open| / |High - Low|). | **`35d6849`** (Phase 1.0) |
| **`Phase 1.0 (Sensex)`** | 2026-08-02 | **`35d6849`** | Configured Dhan API Key (072d3f26) & Secret authentication + Public Yahoo Finance BSE Sensex (`^BSESN`) Fallback Feed. | Initial Commit |

---

## ⏪ Rollback Execution Procedure

To rollback from `Phase 3.0 (Sensex)` to `Phase 1.1 (Sensex)` or `Phase 1.0 (Sensex)`:

1. **Git Checkout**:
   ```bash
   git checkout 023216c # Rollback to Phase 1.1 (Sensex)
   # OR
   git checkout 35d6849 # Rollback to Phase 1.0 (Sensex)
   ```

2. **Render Dashboard Rollback**:
   * Open your Render Web Service for `bse-sensex-sentry` $\rightarrow$ Events $\rightarrow$ Click **Rollback to this deploy**.
