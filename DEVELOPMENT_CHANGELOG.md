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

---

## June 4, 2026

### 1. Phase 1 Header & Footer Features Implementation

#### Features Added

**Global Search Bar**
- Location: Topbar left section
- Functionality:
  - 320px search input with debounced search (300ms)
  - Mock search results showing reports, dashboard, report center
  - Autocomplete-style results dropdown
  - Click result to navigate directly
  - Auto-closes when clicking outside
- Implementation: JavaScript-based with mock data
- Future: Can connect to real search backend API

**Settings Dropdown**
- Location: Topbar right section (gear icon)
- Menu items:
  - Date Format selector (DD/MM/YYYY)
  - Theme selector (Light Mode)
  - Timezone selector (UTC)
  - Help & Documentation link
- Functionality: Toggle open/close on click, auto-close on click outside
- Future: Add actual settings storage and preferences

**Footer with Copyright**
- Location: Bottom of authenticated pages
- Content: Copyright notice only ("© 2026 SDES Reporting Tool. All rights reserved.")
- Styling: Minimal, centered, using WhiteNoiseMiddleware for static serving
- Note: Quick Links section removed per user request

#### Files Modified
- `templates/base.html`:
  - Added CSS for search bar (lines 84-117)
  - Added CSS for settings dropdown (lines 119-156)
  - Added CSS for footer (lines 158-194)
  - Added HTML for global search (lines 359-365)
  - Added HTML for settings dropdown (lines 368-385)
  - Added HTML for footer (lines 429-434)
  - Added JavaScript for search functionality (lines 497-538)
  - Added JavaScript for settings dropdown (lines 540-565)
  - Updated flex layout for footer positioning

#### Technical Details
- **Search Debouncing**: 300ms delay prevents excessive function calls
- **Dropdown Toggle**: Uses `classList.add('show')` / `classList.remove('show')` for visibility
- **CSS Positioning**: Footer uses flex layout to push content up, footer to bottom
- **Mock Results**: Currently hardcoded; ready to connect to actual search API
- **Responsive**: All features work on mobile via Bootstrap media queries

#### Testing Checklist
- [x] Global search input appears in topbar
- [x] Search dropdown shows on typing
- [x] Results are clickable and navigate correctly
- [x] Search auto-closes when clicking outside
- [x] Settings gear icon visible in topbar
- [x] Settings menu toggles on click
- [x] Settings menu closes on outside click
- [x] Footer appears at bottom of all pages
- [x] Copyright text is centered and readable
- [x] All features work on network access (172.16.2.3:9001)

---

### 2. Production Deployment with Waitress

#### Changes Made

**Server Migration**
- Moved from Django development server → **Waitress** (production WSGI)
- Static files collected to `staticfiles/` directory
- WhiteNoiseMiddleware already configured for efficient static serving
- Application now accessible on all network interfaces (0.0.0.0:9001)

#### Deployment Configuration
- **WSGI Server**: Waitress 3.0.2 (pure Python, Windows-compatible)
- **Port**: 9001 (both localhost and network)
- **Host Binding**: 0.0.0.0 (all interfaces)
- **Static Files**: Collected and cached
- **DEBUG**: True (local development, can change to False for production)

#### Startup Commands

**Using Waitress:**
```bash
python -m waitress --port=9001 --host=0.0.0.0 erp_project.wsgi:application
```

**Collect Static Files:**
```bash
python manage.py collectstatic --noinput
```

#### Network Access
- **Local**: http://localhost:9001
- **Network**: http://172.16.2.3:9001
- Works from any device on the same network

#### Performance Notes
- WhiteNoiseMiddleware serves static files efficiently
- Waitress is production-ready and thread-safe
- No need for separate web server (nginx/Apache) for local deployment

---

## Future Improvements

- Connect global search to real backend API (search invoices, reports by name/number)
- Implement persistent user settings storage (date format, timezone, theme preference)
- Add Phase 2 features: Notifications bell, Recent reports dropdown
- Implement feedback widget for user feedback collection
- Add real-time system status indicator
- Consider caching agent list from AGENT_MASTER for faster dropdown loading
- Implement export functionality for invoice reports (Excel/PDF already in template)
- Add date range presets (Today, This Week, This Month, Last 30 Days)
- Performance optimization for large date ranges
- Set up proper production environment with DEBUG=False and specific ALLOWED_HOSTS

