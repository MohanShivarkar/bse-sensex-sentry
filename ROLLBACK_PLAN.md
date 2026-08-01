# BSE Sensex Scalper Platform: Phase-Wise Rollback Strategy & Registry

This document maintains the official **Rollback Strategy, Commit Hash Registry, and Deployment Safety Protocol** for the **BSE Sensex Scalper Platform** (`bse-sensex-sentry`).

---

## 📋 Phase-Wise Rollback Hash Registry

| Phase Tag | Release Date | Git Commit Hash | Scope / Key Changes | Rollback Target Hash |
| :--- | :---: | :---: | :--- | :--- |
| **`Phase 1.0`** | 2026-07-26 | **`55d80d6`** | Initial Standalone BSE Sensex Engine (Dhan API, 9:15 AM-3:30 PM IST Schedule, 3:15 PM Auto-Squareoff, Telegram & WhatsApp Alerts, Web Console). | Baseline Initial Commit |

---

## ⏪ Phase Rollback Execution Procedure

### Method A: Git Rollback Command
```bash
git checkout 55d80d6
git push origin HEAD:main --force
```

### Method B: Render One-Click Rollback
1. Open Render Web Service Dashboard for `bse-sensex-sentry`.
2. Go to **Events** tab.
3. Click **Rollback to this deploy** on the desired commit hash.
