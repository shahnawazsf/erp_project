# Development Changelog

## June 3, 2026

### 1. Customer Invoice Report Query Optimization

#### Problem
The customer invoice report was using an outdated `Custom_report` table that didn't include BL (Bill of Lading) numbers, and date filtering was not working properly.

#### Solution
- **Query Updated** (`finance/views.py:235-254`)
  - Changed from: `Custom_report` table
  - Changed to: `INV_WEEKLY_REPORT_VIEW` with LEFT JOIN to `INV_WEEKLY_REPORT_BL_VIEW`
  - Extracts first BOL number per invoice using `ROW_NUMBER() OVER (PARTITION BY INV_NO ORDER BY BOLNUMBER)`

#### Key Changes
```sql
FROM INV_WEEKLY_REPORT_VIEW a
LEFT JOIN (
    SELECT INV_NO, BOLNUMBER,
           ROW_NUMBER() OVER (PARTITION BY INV_NO ORDER BY BOLNUMBER) rn
    FROM INV_WEEKLY_REPORT_BL_VIEW
) b
ON a.INV_NO = b.INV_NO AND b.rn = 1
```

#### Date Filtering Fix
- **Root Cause**: `INV_DATE` is stored as VARCHAR in 'dd/mm/yyyy' format in the view (via `TO_CHAR(im.inv_date,'dd/mm/yyyy')`)
- **Problem**: String comparison of DD/MM/YYYY format doesn't work correctly (lexicographic ordering)
- **Solution**: Convert DD/MM/YYYY dates to YYYY-MM-DD format for proper string comparison
```python
# Python conversion
d1 = datetime.strptime(filters['date_from'], '%Y-%m-%d').strftime('%d/%m/%Y')
d2 = datetime.strptime(filters['date_to'], '%Y-%m-%d').strftime('%d/%m/%Y')

# Oracle SUBSTR conversion for string comparison
SUBSTR(a.INV_DATE, 7, 4) || '-' || SUBSTR(a.INV_DATE, 4, 2) || '-' || SUBSTR(a.INV_DATE, 1, 2)
```

#### Files Modified
- `finance/views.py` - `report_customer_invoice()` function
- `templates/finance/report_customer_invoice.html` - Column name updated from `bl1` to `bolnumber_1`

#### Result
✅ Report now correctly filters by date range
✅ Displays both BOLNUMBER (from invoice) and BOLNUMBER_1 (first BOL from BL view)
✅ Pagination works correctly with 25 rows per page

---

### 2. Global Page Loader - Content Area Only

#### Problem
The page loader appeared as a full-page overlay, blocking the entire interface including navigation. Users wanted the loader to appear only in the main content area while keeping sidebar and topbar interactive.

#### Solution
Redesigned the page loader to be scoped to the main-content area instead of the entire viewport.

#### Files Modified
- `templates/base.html` - CSS and structure updates

#### CSS Changes
```css
/* Before: Fixed to entire viewport */
#pageLoader {
    position: fixed; inset: 0; z-index: 99999;
}

/* After: Positioned within main-content */
.main-content {
    position: relative;
}
#pageLoader {
    position: absolute;
    top: 58px;        /* Below topbar height */
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 10000;
    background: rgba(15, 23, 42, 0.8);
}
```

#### HTML Structure Changes
- Moved `#pageLoader` div from outside `main-content` to inside it (after content-area, before closing tag)
- Added `class="hidden"` by default so loader is hidden until navigation occurs

#### JavaScript Behavior (Unchanged)
The existing JavaScript already handles:
- ✅ Show loader on all internal link clicks
- ✅ Show loader on form submissions
- ✅ Hide loader on page load
- ✅ Hide on browser back/forward (pageshow event)
- ✅ Skip external links, anchors, JS actions, and download links

#### Result
✅ Sidebar remains visible and interactive during page loads
✅ Topbar remains visible during navigation
✅ Loader appears only in content area (semi-transparent overlay)
✅ Smooth transitions between pages
✅ Works for all navigation across the entire application

---

### 3. Login Page Redesign - "Reporting Tool" Branding

#### Problem
The login page was branded as "ERP System" with module feature lists (HR, Inventory, Sales, Finance) that were not applicable to the current reporting focus.

#### Solution
Rebranded the login page to reflect the Reporting Tool focus and simplified the interface.

#### Files Modified
- `templates/accounts/login.html`

#### Changes
| Item | Before | After |
|------|--------|-------|
| Page Title | "Sign In — ERP System" | "Sign In — Reporting Tool" |
| Brand Title | "ERP System" | "Reporting Tool" |
| Subtitle | "Enterprise Resource Planning" | "Analytics & Reporting Platform" |
| Feature List | Displayed 4 modules | Removed entirely |
| Footer | "© YEAR ERP System..." | "© YEAR Reporting Tool..." |

#### Removed Elements
- Human Resources & Payroll
- Inventory & Warehousing
- Sales & Purchasing
- Finance & Accounting

#### Result
✅ Cleaner, more focused login experience
✅ Branding aligns with reporting tool purpose
✅ Reduced visual clutter
✅ Still maintains professional appearance with brand gradient and logo

---

## Technical Details

### Database Views Referenced
- `INV_WEEKLY_REPORT_VIEW` - Main invoice data with DD/MM/YYYY formatted dates
- `INV_WEEKLY_REPORT_BL_VIEW` - BOL numbers linked to invoices

### Date Handling Summary
- **Form Input**: HTML `<input type="date">` returns YYYY-MM-DD
- **Python Conversion**: Convert to DD/MM/YYYY for Oracle compatibility
- **Oracle Comparison**: Convert back to YYYY-MM-DD using SUBSTR for string comparison
- **View Storage**: INV_DATE stored as VARCHAR 'dd/mm/yyyy' via TO_CHAR()

### CSS/JavaScript Layers
1. Sidebar: `z-index: 100` (fixed position, always visible)
2. Topbar: `z-index: 99` (sticky position, scrolls with content)
3. Page Loader: `z-index: 10000` (absolute, within main-content)
4. Content: `z-index: 0` (behind loader when shown)

---

## Testing Checklist

- [x] Customer invoice report filters by correct date range
- [x] Both BOLNUMBER columns display correctly
- [x] Page loader appears only in content area
- [x] Sidebar remains interactive during page loads
- [x] Login page displays new branding
- [x] Date conversion handles all edge cases
- [x] Report pagination works with filtered results

---

## Future Improvements

- Consider caching agent list from AGENT_MASTER for faster dropdown loading
- Implement export functionality for invoice reports (Excel/PDF already in template)
- Add date range presets (Today, This Week, This Month, Last 30 Days)
- Performance optimization for large date ranges
- Consider moving to production WSGI server (Waitress/Gunicorn)

