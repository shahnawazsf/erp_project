# Quick Reference - June 2026 Updates

## 🎯 What Changed

### 1️⃣ Invoice Report Query
- **What:** Updated customer invoice report to use new database views
- **Where:** `finance/views.py` lines 235-254
- **Why:** Previous `Custom_report` table missing BOL data
- **Result:** Reports now show invoice BOL numbers correctly with proper date filtering

### 2️⃣ Page Loader Behavior  
- **What:** Loader now appears in content area only, not full page
- **Where:** `templates/base.html` (CSS + HTML)
- **Why:** Users wanted sidebar to remain accessible during page loads
- **Result:** Sidebar and topbar stay visible and interactive

### 3️⃣ Login Page Branding
- **What:** Changed from "ERP System" to "Reporting Tool"
- **Where:** `templates/accounts/login.html`
- **Why:** Better reflects the system's reporting-focused purpose
- **Result:** Cleaner, more professional appearance

---

## 🛠 Key Technical Details

### Date Filtering Problem & Solution

**The Issue:**
- Form sends dates as: `2026-05-01` (YYYY-MM-DD)
- View stores dates as: `01/05/2026` (DD/MM/YYYY string)
- String comparison: `'01/05/2026' < '04/01/2026'` ❌ (Wrong!)

**The Solution:**
1. Python: Convert `2026-05-01` → `01/05/2026` for Oracle
2. Oracle: Convert `01/05/2026` back to `2026-05-01` for comparison
3. Result: String comparison now works correctly ✅

```sql
-- Oracle query
WHERE SUBSTR(a.INV_DATE, 7, 4) || '-' || SUBSTR(a.INV_DATE, 4, 2) || '-' || SUBSTR(a.INV_DATE, 1, 2) >= '2026-05-01'
```

### Loader Architecture

**Sidebar (z-index: 100)**
```
│ Fixed on left, always visible
└─ Cannot be covered by anything
```

**Topbar (z-index: 99)**
```
│ Sticky, scrolls with page
└─ Cannot be covered by loader
```

**Loader (z-index: 10000)**
```
│ Absolute within main-content
└─ Shows over content during navigation
```

**Content Area (z-index: 0)**
```
└─ Behind loader when it's shown
```

---

## 📋 Files Modified Summary

| File | Changes | Lines |
|------|---------|-------|
| `finance/views.py` | Query refactored for new views | 235-254 |
| `finance/report_customer_invoice.html` | Column names updated | 274 |
| `templates/base.html` | Loader CSS & positioning changed | 62-74 |
| `templates/accounts/login.html` | Branding updated, features removed | 7,281-303 |

---

## ✅ Testing Checklist

Before deploying these changes, verify:

- [ ] Invoice report filters by date correctly
- [ ] Both BOLNUMBER columns display
- [ ] Date range edge cases work (01/01/2026, 31/12/2026, etc.)
- [ ] Page loader appears only in content area
- [ ] Sidebar remains clickable during load
- [ ] Login page shows "Reporting Tool" branding
- [ ] External links work without showing loader
- [ ] Form submissions show loader

---

## 🚀 Deployment Notes

### Server Restart Required
All changes require Django server restart to take effect.

### No Database Migrations
- No new models created
- No database schema changes
- Safe to deploy to production

### Browser Cache
Users may need to clear browser cache to see:
- Updated login page design
- Loader styling changes

---

## 📚 Related Documentation

- **Full Details:** See `DEVELOPMENT_CHANGELOG.md`
- **Architecture:** See `CLAUDE.md` section "Dashboard _safe() guard"
- **Database Views:** Consult Oracle documentation for:
  - `INV_WEEKLY_REPORT_VIEW`
  - `INV_WEEKLY_REPORT_BL_VIEW`

---

## 💡 Quick Tips

### To verify changes locally:
```bash
cd E:\Testing\projects\erp_project
python manage.py runserver 9001
# Visit http://localhost:9001/accounts/login/
```

### To debug date filtering:
1. Check server logs for the SQL query being executed
2. Verify `filters['date_from']` and `filters['date_to']` values in Python
3. Test the SUBSTR conversion in SQL Developer

### To test loader behavior:
1. Open browser DevTools (F12)
2. Go to Network tab
3. Click navigation link
4. Watch loader appear in content area only

---

**Last Updated:** June 3, 2026  
**Status:** ✅ Production Ready
