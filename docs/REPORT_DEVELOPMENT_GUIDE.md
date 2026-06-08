# ERP Report Development Guide

Complete reference for building Oracle-backed reports **and CRUD forms** in this
Django ERP project — covering URL registration, view logic, Oracle cursor pattern,
filter forms, HTML table design, CSS, pagination, JavaScript totals, Excel/PDF
export, session timeout, and full list/add/edit CRUD workflows.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Step 1 — Register the URL](#2-step-1--register-the-url)
3. [Step 2 — Write the View](#3-step-2--write-the-view)
4. [Step 3 — Oracle Raw Cursor Pattern](#4-step-3--oracle-raw-cursor-pattern)
5. [Step 4 — Filter Form Design](#5-step-4--filter-form-design)
6. [Step 5 — HTML Table Structure](#6-step-5--html-table-structure)
7. [Step 6 — CSS](#7-step-6--css)
8. [Step 7 — Pagination (JavaScript)](#8-step-7--pagination-javascript)
9. [Step 8 — Column Totals (JavaScript)](#9-step-8--column-totals-javascript)
10. [Step 9 — Excel & PDF Export](#10-step-9--excel--pdf-export)
11. [Step 10 — Session Timeout](#11-step-10--session-timeout)
12. [Quick Reference — Full File Checklist](#12-quick-reference--full-file-checklist)
13. [CRUD Form — List + Add + Edit](#13-crud-form--list--add--edit)
    - [Step A — Model (managed = False)](#step-a--model-managed--false)
    - [Step B — ModelForm](#step-b--modelform)
    - [Step C — URL patterns](#step-c--url-patterns)
    - [Step D — Views](#step-d--views)
    - [Step E — List template](#step-e--list-template)
    - [Step F — Form template](#step-f--form-template)
    - [Step G — Sidebar menu entry](#step-g--sidebar-menu-entry)
    - [Step H — Migrations](#step-h--migrations)

---

## 1. Architecture Overview

```
Browser  →  URL router (finance/urls.py)
         →  View function (finance/views.py)
         →  Oracle DB via raw cursor (oracledb thick mode)
         →  Template (templates/finance/report_*.html)
         →  Bootstrap 5 table + vanilla JS pagination
```

- **Stack:** Django 6 · Python 3.14 · Oracle 12.2 · Bootstrap 5
- **Auth guard:** every view uses `@login_required`
- **Session:** `oracle_user` dict stored in Django session; expires after
  10 minutes of inactivity (see §11)
- **Oracle cursor:** must unwrap two layers to reach `oracledb` cursor
  (see §4)

---

## 2. Step 1 — Register the URL

File: `finance/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    # ... existing paths ...
    path('reports/',                   views.reports_hub,             name='finance_reports'),
    path('reports/vat/',               views.report_vat,              name='report_vat'),
    path('reports/customer-invoice/',  views.report_customer_invoice, name='report_customer_invoice'),
]
```

The project root `erp_project/urls.py` already includes finance with the
`/finance/` prefix, so the full paths become `/finance/reports/vat/` etc.

Add a sidebar link in `templates/base.html`:

```html
<a href="{% url 'report_vat' %}"
   class="nav-link {% if request.resolver_match.url_name == 'report_vat' %}active{% endif %}">
    <i class="bi bi-percent"></i> VAT Report
</a>
```

---

## 3. Step 2 — Write the View

File: `finance/views.py`

### Skeleton

```python
import calendar
import logging
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import connection
from django.shortcuts import render

logger = logging.getLogger(__name__)

@login_required
def report_vat(request):
    current_year  = date.today().year
    current_month = date.today().month
    rows     = []
    filters  = {}
    generated = False
    filter_mode = 'month'

    if request.method == 'POST':
        filter_mode = request.POST.get('filter_mode', 'month')

        # ── Monthly mode ──────────────────────────────────────────────
        if filter_mode == 'month':
            selected = request.POST.get('month', '')   # e.g. "2026-04"
            if selected:
                year, month = int(selected.split('-')[0]), int(selected.split('-')[1])
                last_day = calendar.monthrange(year, month)[1]
                filters = {
                    'month':       selected,
                    'month_label': date(year, month, 1).strftime('%B %Y'),
                    'date_from':   f"{year}-{month:02d}-01",
                    'date_to':     f"{year}-{month:02d}-{last_day}",
                }
                generated = True

        # ── Date-range mode ──────────────────────────────────────────
        else:
            date_from = request.POST.get('date_from', '')
            date_to   = request.POST.get('date_to',   '')
            if date_from and date_to:
                filters = {
                    'date_from': date_from,
                    'date_to':   date_to,
                    'month':     '',
                    'month_label': '',
                }
                generated = True

        # ── Execute Oracle query once filters are resolved ────────────
        if generated:
            try:
                with connection.cursor() as django_cur:
                    cur = django_cur.cursor.cursor   # raw oracledb cursor
                    cur.execute("""
                        SELECT ...
                        FROM   ...
                        WHERE  TRUNC(POSTING_DATE)
                               BETWEEN TO_DATE(:d1, 'YYYY-MM-DD')
                                   AND TO_DATE(:d2, 'YYYY-MM-DD')
                    """, {'d1': filters['date_from'], 'd2': filters['date_to']})
                    cols = [d[0].lower() for d in cur.description]
                    rows = [dict(zip(cols, row)) for row in cur.fetchall()]
            except Exception:
                logger.exception('VAT report query failed')
                messages.error(request, 'Query failed — check server logs.')

    # ── Build month calendar data ─────────────────────────────────────
    month_names = ['Jan','Feb','Mar','Apr','May','Jun',
                   'Jul','Aug','Sep','Oct','Nov','Dec']
    months = [
        {
            'num':         m + 1,
            'short':       month_names[m],
            'value':       f"{current_year}-{m+1:02d}",
            'is_future':   (m + 1) > current_month,
            'is_current':  (m + 1) == current_month,
            'is_selected': filters.get('month') == f"{current_year}-{m+1:02d}",
        }
        for m in range(12)
    ]

    return render(request, 'finance/report_vat.html', {
        'rows':          rows,
        'filters':       filters,
        'generated':     generated,
        'filter_mode':   filter_mode,
        'current_year':  current_year,
        'current_month': current_month,
        'months':        months,
    })
```

### Key design rules

| Rule | Reason |
|------|--------|
| `rows = []` default | Template always receives the variable |
| `generated = False` default | Template shows "enter filters" state until POST |
| Single query block after both filter branches | Avoids duplicated query code |
| `try/except` wrapping the cursor | Oracle errors produce a user message, not a 500 |
| `cols = [d[0].lower() ...]` | Column names lowercased so template uses `row.inv_no` etc. |

---

## 4. Step 3 — Oracle Raw Cursor Pattern

Django wraps the oracledb cursor in a `CursorWrapper`. To call `cur.var()` or
access driver-level features you must unwrap:

```python
with connection.cursor() as django_cur:
    cur = django_cur.cursor.cursor   # ← two levels: CursorWrapper → DatabaseCursor → oracledb cursor

    # Named bind variables  (preferred — prevents SQL injection)
    cur.execute("SELECT ... WHERE col = :val", {'val': some_value})

    # Positional bind variables
    cur.execute("SELECT ... WHERE col = :1", [some_value])

    cols = [d[0].lower() for d in cur.description]
    rows = [dict(zip(cols, row)) for row in cur.fetchall()]
```

### Date binding

HTML `<input type="date">` returns `YYYY-MM-DD`. Pass it directly with
a matching format mask:

```sql
WHERE TRUNC(posting_date) BETWEEN TO_DATE(:d1, 'YYYY-MM-DD')
                               AND TO_DATE(:d2, 'YYYY-MM-DD')
```

### CTE queries

Oracle supports `WITH` CTEs normally:

```sql
WITH Q1 AS (
    SELECT im.inv_no, SUM(idt.charge_amount) AS charge_amount
    FROM   invoice_master im
    JOIN   invoice_detail idt ON im.inv_no = idt.inv_no
    WHERE  im.agent_code = :G
    GROUP BY im.inv_no
),
Q2 AS (
    SELECT b.inv_no, MAX(a.bolnumber) AS bl1
    FROM   operationdetails a
    JOIN   invoice_detail b ON b.id = a.toid
    WHERE  a.bolnumber IS NOT NULL
    GROUP BY b.inv_no
)
SELECT q1.*, q2.bl1
FROM   q1
LEFT JOIN q2 ON q1.inv_no = q2.inv_no
ORDER BY q1.inv_no DESC
```

### Database-link queries

Append `@link_name` to the table or view name:

```sql
SELECT ... FROM VIEW_VAT_STATEMENT@SDRS104 WHERE ...
```

---

## 5. Step 4 — Filter Form Design

The reports use two filter modes served from the same page:

### Monthly calendar picker

```html
<form method="post" id="monthForm">
    {% csrf_token %}
    <input type="hidden" name="filter_mode" value="month">
    <input type="hidden" name="month" id="selectedMonth" value="{{ filters.month }}">

    <div class="month-grid">
        {% for m in months %}
        <div class="month-btn
            {% if m.is_current %}current-month{% endif %}
            {% if m.is_future %}disabled{% endif %}
            {% if m.is_selected %}selected{% endif %}"
            data-month="{{ m.value }}"
            onclick="selectMonth(this)">
            <span class="month-short">{{ m.short }}</span>
            <span class="month-num">{{ current_year }}</span>
        </div>
        {% endfor %}
    </div>
</form>
```

```js
function selectMonth(el) {
    if (el.classList.contains('disabled')) return;
    document.querySelectorAll('.month-btn').forEach(b => b.classList.remove('selected'));
    el.classList.add('selected');
    document.getElementById('selectedMonth').value = el.dataset.month;
    document.getElementById('monthForm').submit();
}
```

### Date-range picker

```html
<form method="post" id="rangeForm">
    {% csrf_token %}
    <input type="hidden" name="filter_mode" value="range">
    <input type="date" name="date_from" value="{{ filters.date_from }}" required>
    <input type="date" name="date_to"   value="{{ filters.date_to }}"   required>
    <button type="submit">Generate</button>
</form>
```

### Switching between modes

```js
function switchMode(mode) {
    const panelMonth = document.getElementById('panel-month');
    const panelRange = document.getElementById('panel-range');
    if (mode === 'range') {
        panelMonth.style.display = 'none';
        panelRange.style.display = '';
    } else {
        panelRange.style.display = 'none';
        panelMonth.style.display = '';
    }
}
```

### Agent dropdown (Customer Invoice report)

Uses [Tom Select](https://tom-select.github.io/) for searchable select:

```html
<select name="agent_code" id="agentSelect" class="form-select form-select-sm" required>
    <option value="">Search agent…</option>
    {% for agent in agents %}
    <option value="{{ agent.code }}"
        {% if filters.agent_code == agent.code %}selected{% endif %}>
        {{ agent.code }} — {{ agent.name }}
    </option>
    {% endfor %}
</select>
```

```js
new TomSelect('#agentSelect', {
    placeholder: 'Search agent code or name…',
    allowEmptyOption: true,
    maxOptions: null,
    searchField: ['text'],
});
```

---

## 6. Step 5 — HTML Table Structure

```html
<div class="table-responsive">
    <table class="table table-hover mb-0 report-table" id="reportTable">

        <thead>
            <tr>
                <th>#</th>
                <th>Doc No</th>
                <th>...</th>
                <th class="amount-col">Tax Base Amt</th>
                <th class="amount-col">Output/Input Tax</th>
                <th class="amount-col">Gross Incl. VAT</th>
            </tr>
        </thead>

        <tbody>
            {% for row in rows %}
            <tr>
                <td class="text-muted small">{{ forloop.counter }}</td>
                <td class="fw-semibold">{{ row.doc_no|default:"—" }}</td>
                <td class="amount-col">{{ row.tax_base_amount|default:"0.00" }}</td>
            </tr>
            {% endfor %}
        </tbody>

        <tfoot>
            <tr>
                <td colspan="11" class="text-end pe-3">Totals</td>
                <td class="amount-col" id="totalTaxBase">—</td>
                <td class="amount-col text-warning" id="totalOutputInput">—</td>
                <td class="amount-col" id="totalGross">—</td>
                <td></td>   <!-- non-numeric columns get empty cells -->
            </tr>
        </tfoot>

    </table>
</div>

<!-- Pagination bar — placed immediately after table-responsive div -->
<div class="pagination-bar no-print" id="paginationBar">
    <div class="pagination-info" id="pageInfo"></div>
    <div class="page-nums"       id="pageNums"></div>
</div>
```

### colspan rule for tfoot

`colspan` = number of text/non-numeric columns before the first amount
column. Keep the count equal to the number of `<th>` elements to the left
of the first `amount-col` header (including the `#` counter column).

---

## 7. Step 6 — CSS

Add inside `{% block extra_css %}` in the report template.

```css
/* ── Report table ── */
.report-table th {
    font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.5px; color: #495057; background: #f8f9fa;
    white-space: nowrap;
}
.report-table td   { font-size: 0.875rem; vertical-align: middle; }
.report-table tfoot td {
    font-weight: 700; font-size: 0.875rem;
    background: #f0f4ff; border-top: 2px solid #dee2e6;
}
.amount-col {
    text-align: right;
    font-variant-numeric: tabular-nums;  /* aligns decimal points */
}

/* ── Pagination ── */
.pagination-bar {
    padding: 0.75rem 1rem; border-top: 1px solid #e9ecef; background: #fafafa;
    border-radius: 0 0 14px 14px;
    display: flex; align-items: center;
    justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;
}
.pagination-info { font-size: 0.8rem; color: #6c757d; }
.page-nums       { display: flex; gap: 4px; flex-wrap: wrap; }
.page-btn {
    border: 1px solid #dee2e6; background: #fff; color: #495057;
    border-radius: 6px; padding: 0.3rem 0.65rem;
    font-size: 0.8rem; cursor: pointer;
    transition: all 0.15s; line-height: 1.4;
}
.page-btn:hover:not(.active):not(:disabled) {
    background: #f0f4ff; border-color: #4361ee; color: #4361ee;
}
.page-btn.active   { background: #1a2e52; border-color: #1a2e52; color: #fff; font-weight: 600; }
.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }

/* ── Month calendar grid ── */
.month-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin-top: 1rem; }
.month-btn {
    border: 2px solid #e9ecef; border-radius: 10px;
    padding: 0.75rem 0.5rem; text-align: center;
    cursor: pointer; background: #fafafa;
    font-size: 0.85rem; font-weight: 600; color: #495057;
    transition: all 0.18s; user-select: none;
}
.month-btn:hover:not(.disabled):not(.selected) {
    border-color: #4fc3f7; background: #f0faff; color: #0288d1;
}
.month-btn.selected {
    border-color: #1a2e52;
    background: linear-gradient(135deg, #1a2e52, #1e3a6e);
    color: #fff; box-shadow: 0 4px 14px rgba(26,46,82,.35);
}
.month-btn.disabled { opacity: 0.35; cursor: not-allowed; background: #f0f0f0; }

/* ── Empty state ── */
.empty-state { padding: 4rem 2rem; text-align: center; color: #adb5bd; }
.empty-state i { font-size: 3.5rem; display: block; margin-bottom: 0.75rem; }

/* ── Print overrides ── */
@media print {
    .no-print        { display: none !important; }
    .sidebar,
    .topbar          { display: none !important; }
    .main-content    { margin-left: 0 !important; }
    .content-area    { padding: 0 !important; }
    .print-header    { display: block !important; }
    .pagination-bar  { display: none !important; }
    body             { background: #fff !important; }
    .card            { box-shadow: none !important; border: 1px solid #dee2e6 !important; }
}
.print-header { display: none; margin-bottom: 1.5rem; }
```

---

## 8. Step 7 — Pagination (JavaScript)

Place inside `{% block extra_js %}`. Must run after the table is rendered.

```js
const PAGE_SIZE = 25;
let currentPage = 1;
let allRows = [];

document.addEventListener('DOMContentLoaded', function () {
    const tbody = document.querySelector('#reportTable tbody');
    if (!tbody) return;

    // Cache all <tr> elements once
    allRows = Array.from(tbody.querySelectorAll('tr'));

    renderPage(1);
});

function renderPage(page) {
    currentPage  = page;
    const total      = allRows.length;
    const totalPages = Math.ceil(total / PAGE_SIZE);
    const start      = (page - 1) * PAGE_SIZE;
    const end        = Math.min(start + PAGE_SIZE, total);

    // Show/hide rows for current page
    allRows.forEach(function (r, i) {
        r.style.display = (i >= start && i < end) ? '' : 'none';
    });

    // Info label
    document.getElementById('pageInfo').textContent =
        'Showing ' + (start + 1) + '–' + end + ' of ' + total + ' records';

    // Rebuild page buttons
    const container = document.getElementById('pageNums');
    container.innerHTML = '';

    const prev = makeBtn('‹ Prev', page <= 1);
    prev.onclick = () => renderPage(page - 1);
    container.appendChild(prev);

    // Smart page window: always show page 1, last page, and ±2 around current
    const pages = new Set([1, totalPages]);
    for (let p = Math.max(1, page - 2); p <= Math.min(totalPages, page + 2); p++) pages.add(p);

    let prev_p = 0;
    Array.from(pages).sort((a, b) => a - b).forEach(function (p) {
        if (p - prev_p > 1) {                    // gap → insert ellipsis
            const gap = document.createElement('span');
            gap.textContent = '…';
            gap.style.cssText = 'padding:0.3rem 0.4rem;font-size:0.8rem;color:#adb5bd;';
            container.appendChild(gap);
        }
        const btn = makeBtn(p, false);
        if (p === page) btn.classList.add('active');
        btn.onclick = () => renderPage(p);
        container.appendChild(btn);
        prev_p = p;
    });

    const next = makeBtn('Next ›', page >= totalPages);
    next.onclick = () => renderPage(page + 1);
    container.appendChild(next);
}

function makeBtn(label, disabled) {
    const btn = document.createElement('button');
    btn.className = 'page-btn';
    btn.textContent = label;
    btn.disabled = disabled;
    return btn;
}
```

---

## 9. Step 8 — Column Totals (JavaScript)

Compute totals from **all rows** (not just the visible page) so footer
numbers are always correct regardless of which page is shown.

```js
document.addEventListener('DOMContentLoaded', function () {
    const tbody = document.querySelector('#reportTable tbody');
    if (!tbody) return;

    allRows = Array.from(tbody.querySelectorAll('tr'));

    // ── Compute grand totals ──────────────────────────────────────────
    // p(i) reads column i (0-indexed including the # counter)
    let taxBase = 0, outputInput = 0, gross = 0, foreign = 0;
    allRows.forEach(function (r) {
        const c = r.querySelectorAll('td');
        const p = i => parseFloat((c[i]?.textContent || '0').replace(/,/g, '')) || 0;
        taxBase     += p(11);   // column index 11 = TAX_BASE_AMOUNT
        outputInput += p(12);   // column index 12 = OUTPUT_INPUT_TAX
        gross       += p(13);   // column index 13 = GRSOS_AMT_INCL_VAT
        foreign     += p(15);   // column index 15 = FOREIGN_CURRENCY_AMT
    });

    const fmt = n => n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    const el  = id => document.getElementById(id);
    if (el('totalTaxBase'))     el('totalTaxBase').textContent     = fmt(taxBase);
    if (el('totalOutputInput')) el('totalOutputInput').textContent = fmt(outputInput);
    if (el('totalGross'))       el('totalGross').textContent       = fmt(gross);
    if (el('totalForeign'))     el('totalForeign').textContent     = fmt(foreign);

    renderPage(1);   // ← call pagination after totals are computed
});
```

### Column index reference (VAT report, 0-based)

| Index | Column |
|-------|--------|
| 0 | # (counter) |
| 1 | Doc No |
| 2 | Doc Type |
| 3 | Inv No |
| 4 | Doc Date |
| 5 | Posting Date |
| 6 | Vendor/Cust No |
| 7 | Name |
| 8 | VAT No |
| 9 | Type of Goods/Services |
| 10 | Tax Code |
| **11** | **Tax Base Amt** ← summed |
| **12** | **Output/Input Tax** ← summed |
| **13** | **Gross Incl. VAT** ← summed |
| 14 | Currency |
| **15** | **Foreign Amt** ← summed |
| 16 | Foreign Currency |
| 17 | Posting Month |

---

## 10. Step 9 — Excel & PDF Export

### Excel (SheetJS)

Include the CDN script once per report template:

```html
<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
```

```js
function exportExcel() {
    // Temporarily show ALL rows so SheetJS captures every record
    allRows.forEach(r => r.style.display = '');

    const wb = XLSX.utils.book_new();
    const ws = XLSX.utils.table_to_sheet(document.getElementById('reportTable'));
    XLSX.utils.book_append_sheet(wb, ws, 'VAT Report');

    const label = '{{ filters.month_label|default:"" }}'
                || '{{ filters.date_from }}_{{ filters.date_to }}';
    XLSX.writeFile(wb, 'VAT_Report_' + label.replace(/ /g, '_') + '.xlsx');

    // Restore current page
    renderPage(currentPage);
}
```

Trigger button:

```html
<button class="btn btn-success btn-sm" onclick="exportExcel()">
    <i class="bi bi-file-earmark-excel me-1"></i> Download Excel
</button>
```

### PDF / Print

```html
<button class="btn btn-danger btn-sm" onclick="window.print()">
    <i class="bi bi-file-earmark-pdf me-1"></i> Download PDF
</button>
```

The print CSS hides sidebar, topbar, filter card, and pagination bar
automatically (`.no-print { display: none !important; }` in `@media print`).

Add a print-only header that is hidden on screen:

```html
<div class="print-header">
    <h5>VAT Report — {{ filters.month_label }}</h5>
    <small>Period: {{ filters.date_from }} to {{ filters.date_to }}</small>
    <hr>
</div>
```

```css
.print-header { display: none; }
@media print  { .print-header { display: block !important; } }
```

---

## 11. Step 10 — Session Timeout

### Server-side (settings.py)

```python
SESSION_COOKIE_AGE      = 600   # seconds (10 minutes)
SESSION_SAVE_EVERY_REQUEST = True  # reset expiry timer on every request
```

`SESSION_SAVE_EVERY_REQUEST = True` means: each HTTP request refreshes the
10-minute clock, so the session expires after 10 minutes of **inactivity**
(not 10 minutes after login).

### Client-side inactivity timer (base.html)

Place this block **before** the Bootstrap JS `<script>` tag so the modal
HTML is in the DOM when Bootstrap initialises.

```html
{% if user.is_authenticated %}
<!-- Warning modal -->
<div class="modal fade" id="sessionModal" tabindex="-1"
     data-bs-backdrop="static" data-bs-keyboard="false">
    <div class="modal-dialog modal-dialog-centered modal-sm">
        <div class="modal-content border-0 shadow-lg" style="border-radius:16px;">
            <div class="modal-body text-center p-4">
                <div style="font-size:2.5rem; margin-bottom:0.75rem;">&#9201;</div>
                <h6 class="fw-bold mb-1">Session Expiring</h6>
                <p class="text-muted small mb-3">
                    You will be logged out in
                    <strong id="sessionCountdown">60</strong> seconds.
                </p>
                <button class="btn btn-primary btn-sm w-100"
                        id="sessionStayBtn">Stay Logged In</button>
            </div>
        </div>
    </div>
</div>

<script>
(function () {
    var TIMEOUT  = 600;   // 10 min total inactivity before logout
    var WARN_AT  = 540;   // show warning after 9 min idle

    var lastActive = Date.now();
    var modal, bsModal;

    // Reset timer on any user activity
    ['mousemove','keydown','click','scroll','touchstart'].forEach(function (ev) {
        document.addEventListener(ev, function () { lastActive = Date.now(); }, { passive: true });
    });

    document.addEventListener('DOMContentLoaded', function () {
        modal   = document.getElementById('sessionModal');
        bsModal = modal ? new bootstrap.Modal(modal) : null;

        document.getElementById('sessionStayBtn').addEventListener('click', function () {
            lastActive = Date.now();
            bsModal.hide();
            // Ping the server so Django resets the server-side session cookie
            fetch(window.location.href, { method: 'HEAD', credentials: 'same-origin' });
        });
    });

    // Check every second
    setInterval(function () {
        var idle = Math.floor((Date.now() - lastActive) / 1000);

        if (idle >= TIMEOUT) {
            window.location.href = '{% url "logout" %}';
            return;
        }

        if (idle >= WARN_AT && bsModal) {
            var cd = document.getElementById('sessionCountdown');
            if (cd) cd.textContent = TIMEOUT - idle;          // live countdown
            if (modal && !modal.classList.contains('show')) bsModal.show();
        } else if (modal && modal.classList.contains('show')) {
            bsModal.hide();                                    // user became active
        }
    }, 1000);
})();
</script>
{% endif %}
```

### How it works end-to-end

```
User inactive for 9 min  →  JS shows warning modal with live countdown
User clicks "Stay Logged In"  →  JS resets lastActive + fetches current page (HEAD)
                                  →  Django sees request → saves session → resets 10-min cookie
User ignores warning for 60 s  →  JS redirects to /accounts/logout/
                                  →  Django deletes session row from DJANGO_SESSION table
User tries to navigate back    →  @login_required redirects to /accounts/login/
```

---

## 12. Quick Reference — Full File Checklist

When creating a new report, touch these files in order:

| # | File | What to add |
|---|------|-------------|
| 1 | `finance/urls.py` | `path('reports/my-report/', views.report_my, name='report_my')` |
| 2 | `finance/views.py` | View function with filter parsing + Oracle query + `render()` |
| 3 | `templates/finance/report_my.html` | Filter form, results table, pagination bar |
| 4 | `templates/base.html` | Sidebar `<a>` link (already has session timeout) |
| 5 | `erp_project/settings.py` | No change needed (session timeout already configured) |

### Template block structure

```
{% extends 'base.html' %}
{% block title %}...{% endblock %}
{% block extra_css %}  ← report-table, pagination, month-grid CSS  {% endblock %}
{% block content %}
    breadcrumb
    page header  (+ Download Excel / PDF buttons when generated)
    filter card  (month calendar OR date range form)
    applied-filter badges
    print header (hidden on screen, visible on print)
    results card
        card-header (record count + inline export buttons)
        table-responsive > table#reportTable
        pagination-bar
        empty-state (when rows is empty)
    empty-state (when not yet generated)
{% endblock %}
{% block extra_js %}  ← xlsx CDN, pagination JS, totals JS, exportExcel()  {% endblock %}
```

---

## 13. CRUD Form — List + Add + Edit

Use this pattern whenever you need a **list page with a search bar and Add
button**, plus an **Edit button** on each row. Example used throughout:
*Container Notification* in the Finance module.

---

### Step A — Model (`managed = False`)

File: `finance/models.py`

```python
from django.db import models

class ContainerNotification(models.Model):
    container_no  = models.CharField(max_length=50)
    vessel_name   = models.CharField(max_length=100)
    port          = models.CharField(max_length=100, blank=True)
    eta           = models.DateField(null=True, blank=True)
    status        = models.CharField(max_length=30, blank=True)
    remarks       = models.TextField(blank=True)

    class Meta:
        db_table = 'YOUR_ORACLE_TABLE_NAME'   # ← exact Oracle table name
        managed  = False                       # Django will NOT create/alter this table
```

**`managed = False` rules:**
- Django reads and writes rows normally via the ORM
- `makemigrations` creates a migration file but `migrate` does nothing to Oracle
- You must ensure the `db_table` name matches the Oracle table exactly
- Column names in the model must match Oracle column names (case-insensitive)

**Field type mapping (Django → Oracle):**

| Django field | Oracle column type |
|---|---|
| `CharField` | `VARCHAR2` |
| `IntegerField` | `NUMBER` |
| `DecimalField` | `NUMBER(p,s)` |
| `DateField` | `DATE` (date part only) |
| `DateTimeField` | `DATE` or `TIMESTAMP` |
| `TextField` | `CLOB` or long `VARCHAR2` |
| `BooleanField` | `NUMBER(1)` (0/1) |

---

### Step B — ModelForm

Create file: `finance/forms.py`

```python
from django import forms
from .models import ContainerNotification

class ContainerNotificationForm(forms.ModelForm):
    class Meta:
        model  = ContainerNotification
        fields = '__all__'          # or list specific fields: ['container_no', 'vessel_name', ...]
        widgets = {
            'eta':     forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }
```

Then import it at the top of `finance/views.py`:

```python
from .forms import ContainerNotificationForm
```

**Excluding fields from the form:**

```python
fields  = ['container_no', 'vessel_name', 'eta', 'status']   # whitelist
# OR
exclude = ['created_at', 'created_by']                        # blacklist
```

---

### Step C — URL patterns

File: `finance/urls.py`

```python
# Container Notification
path('container-notification/',              views.cn_list,   name='cn_list'),
path('container-notification/add/',          views.cn_create, name='cn_create'),
path('container-notification/<int:pk>/edit/', views.cn_edit,  name='cn_edit'),
```

Full URLs (with the `/finance/` project prefix):

| Name | Full URL | Purpose |
|------|----------|---------|
| `cn_list` | `/finance/container-notification/` | List + search |
| `cn_create` | `/finance/container-notification/add/` | Add new record |
| `cn_edit` | `/finance/container-notification/5/edit/` | Edit record with pk=5 |

---

### Step D — Views

File: `finance/views.py`

```python
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ContainerNotification
from .forms import ContainerNotificationForm


# ── List ─────────────────────────────────────────────────────────────
@login_required
def cn_list(request):
    q  = request.GET.get('q', '').strip()
    qs = ContainerNotification.objects.all().order_by('-id')
    if q:
        qs = qs.filter(container_no__icontains=q)   # adjust field to match your search column
    return render(request, 'finance/cn_list.html', {'rows': qs, 'q': q})


# ── Create ───────────────────────────────────────────────────────────
@login_required
def cn_create(request):
    if request.method == 'POST':
        form = ContainerNotificationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Record added successfully.')
            return redirect('cn_list')
    else:
        form = ContainerNotificationForm()
    return render(request, 'finance/cn_form.html', {'form': form, 'action': 'Add'})


# ── Edit ─────────────────────────────────────────────────────────────
@login_required
def cn_edit(request, pk):
    obj = get_object_or_404(ContainerNotification, pk=pk)
    if request.method == 'POST':
        form = ContainerNotificationForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Record updated successfully.')
            return redirect('cn_list')
    else:
        form = ContainerNotificationForm(instance=obj)
    return render(request, 'finance/cn_form.html', {'form': form, 'action': 'Edit'})
```

**How the views work:**

```
GET  /container-notification/        → cn_list   → renders table of all rows
GET  /container-notification/add/    → cn_create → renders blank form
POST /container-notification/add/    → cn_create → validates + saves → redirects to list
GET  /container-notification/5/edit/ → cn_edit   → renders form pre-filled with row pk=5
POST /container-notification/5/edit/ → cn_edit   → validates + updates → redirects to list
```

---

### Step E — List Template

File: `templates/finance/cn_list.html`

```html
{% extends 'base.html' %}
{% block title %}Container Notification{% endblock %}

{% block content %}

<!-- Breadcrumb -->
<nav aria-label="breadcrumb" class="mb-3">
    <ol class="breadcrumb small">
        <li class="breadcrumb-item">
            <a href="{% url 'finance_dashboard' %}" class="text-decoration-none">Finance</a>
        </li>
        <li class="breadcrumb-item active">Container Notification</li>
    </ol>
</nav>

<!-- Page header -->
<div class="page-header d-flex align-items-center justify-content-between">
    <div>
        <h4 class="mb-0">
            <i class="bi bi-box-seam me-2" style="color:#0288d1;"></i>Container Notification
        </h4>
        <small class="text-muted">Manage container notification records</small>
    </div>
    <a href="{% url 'cn_create' %}" class="btn btn-primary btn-sm">
        <i class="bi bi-plus-lg me-1"></i> Add Record
    </a>
</div>

<!-- Search bar -->
<form method="get" class="mb-3">
    <div class="input-group input-group-sm" style="max-width:360px;">
        <span class="input-group-text bg-white">
            <i class="bi bi-search text-muted"></i>
        </span>
        <input type="text" name="q" class="form-control border-start-0"
               placeholder="Search container no…" value="{{ q }}">
        {% if q %}
        <a href="{% url 'cn_list' %}" class="btn btn-outline-secondary">
            <i class="bi bi-x"></i>
        </a>
        {% endif %}
    </div>
</form>

<!-- Results -->
<div class="card" style="border-radius:14px; border:none; box-shadow:0 1px 4px rgba(0,0,0,0.08);">
    <div class="card-header bg-white border-0 pt-3 pb-0 d-flex align-items-center justify-content-between">
        <h6 class="fw-bold mb-0">
            Records
            {% if rows %}
            <span class="badge bg-primary ms-2">{{ rows|length }}</span>
            {% endif %}
        </h6>
    </div>

    <div class="table-responsive">
        <table class="table table-hover mb-0" style="font-size:0.875rem;">
            <thead>
                <tr style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.5px;
                            color:#495057; background:#f8f9fa;">
                    <th>#</th>
                    <th>Container No</th>
                    <th>Vessel Name</th>
                    <th>Port</th>
                    <th>ETA</th>
                    <th>Status</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                {% for row in rows %}
                <tr>
                    <td class="text-muted small">{{ forloop.counter }}</td>
                    <td class="fw-semibold">{{ row.container_no|default:"—" }}</td>
                    <td>{{ row.vessel_name|default:"—" }}</td>
                    <td>{{ row.port|default:"—" }}</td>
                    <td>{{ row.eta|date:"d/m/Y"|default:"—" }}</td>
                    <td>
                        <span class="badge rounded-pill
                            {% if row.status == 'Arrived' %}bg-success
                            {% elif row.status == 'In Transit' %}bg-warning text-dark
                            {% else %}bg-secondary{% endif %}">
                            {{ row.status|default:"—" }}
                        </span>
                    </td>
                    <td>
                        <a href="{% url 'cn_edit' row.pk %}"
                           class="btn btn-outline-primary btn-sm">
                            <i class="bi bi-pencil me-1"></i>Edit
                        </a>
                    </td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="7" class="text-center text-muted py-5">
                        <i class="bi bi-inbox" style="font-size:2rem; display:block; margin-bottom:0.5rem;"></i>
                        {% if q %}No records match "<strong>{{ q }}</strong>".
                        {% else %}No records found. <a href="{% url 'cn_create' %}">Add one</a>.{% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

{% endblock %}
```

**Key template tags:**

| Tag | Purpose |
|-----|---------|
| `{% for row in rows %}` | Loop over queryset |
| `{{ row.field\|default:"—" }}` | Show `—` when value is empty |
| `{{ row.eta\|date:"d/m/Y" }}` | Format a DateField |
| `{% url 'cn_edit' row.pk %}` | Build edit URL with the row's primary key |
| `{% empty %}` | Shown when queryset is empty |

---

### Step F — Form Template

File: `templates/finance/cn_form.html`

```html
{% extends 'base.html' %}
{% load widget_tweaks %}
{% block title %}{{ action }} Container Notification{% endblock %}

{% block content %}

<!-- Breadcrumb -->
<nav aria-label="breadcrumb" class="mb-3">
    <ol class="breadcrumb small">
        <li class="breadcrumb-item">
            <a href="{% url 'cn_list' %}" class="text-decoration-none">Container Notification</a>
        </li>
        <li class="breadcrumb-item active">{{ action }}</li>
    </ol>
</nav>

<!-- Page header -->
<div class="page-header">
    <h4 class="mb-0">
        <i class="bi bi-box-seam me-2" style="color:#0288d1;"></i>
        {{ action }} Container Notification
    </h4>
</div>

<!-- Form card -->
<div class="card p-4" style="max-width:760px; border-radius:14px;
     border:none; box-shadow:0 1px 4px rgba(0,0,0,0.08);">
    <form method="post" autocomplete="off">
        {% csrf_token %}

        <div class="row g-3">
            {% for field in form %}
            <div class="col-md-6">
                <label class="form-label fw-semibold small text-uppercase text-muted mb-1">
                    {{ field.label }}
                    {% if field.field.required %}
                    <span class="text-danger">*</span>
                    {% endif %}
                </label>
                {{ field|add_class:"form-control form-control-sm" }}
                {% if field.errors %}
                <div class="text-danger small mt-1">{{ field.errors.0 }}</div>
                {% endif %}
            </div>
            {% endfor %}
        </div>

        <!-- Buttons -->
        <div class="d-flex gap-2 mt-4 pt-3 border-top">
            <button type="submit" class="btn btn-primary btn-sm px-4">
                <i class="bi bi-check-lg me-1"></i> Save
            </button>
            <a href="{% url 'cn_list' %}" class="btn btn-outline-secondary btn-sm px-4">
                <i class="bi bi-x-lg me-1"></i> Cancel
            </a>
        </div>
    </form>
</div>

{% endblock %}
```

`{% load widget_tweaks %}` and `{{ field|add_class:"form-control form-control-sm" }}`
applies Bootstrap classes to every field automatically — no need to style
each field individually.

---

### Step G — Sidebar Menu Entry

File: `templates/base.html`

Find the Finance section in the sidebar and add the link:

```html
<div class="nav-section">Finance</div>

<a href="{% url 'cn_list' %}"
   class="nav-link {% if request.resolver_match.url_name == 'cn_list' %}active{% endif %}">
    <i class="bi bi-box-seam"></i> Container Notification
</a>
```

The `active` class highlights the link when you are on the list page.
To also highlight it when on the add/edit pages:

```html
class="nav-link {% if request.resolver_match.url_name in 'cn_list cn_create cn_edit' %}active{% endif %}"
```

---

### Step H — Migrations

Because `managed = False`, Django will not create or alter the Oracle table.
But Django still needs a migration record so it knows the model exists:

```bash
python manage.py makemigrations finance
python manage.py migrate
```

`migrate` will print `No migrations to apply` for the unmanaged model,
which is correct — Oracle already has the table.

**Verify the model can read from Oracle:**

```bash
python manage.py shell
>>> from finance.models import ContainerNotification
>>> ContainerNotification.objects.count()
```

If this returns a number (not an error), the model is wired up correctly.

---

### CRUD Quick Reference

| # | File | What to add |
|---|------|-------------|
| A | `finance/models.py` | Model class with `managed = False` and `db_table` |
| B | `finance/forms.py` | `ModelForm` with field list and widget overrides |
| C | `finance/urls.py` | 3 paths: list, add, `<str:pk>/edit/` (use `<str:pk>` if PK is VARCHAR) |
| D | `finance/views.py` | `cn_list`, `cn_create`, `cn_edit` + import form + model |
| E | `templates/finance/cn_list.html` | List table + search bar + Add button + Edit button + **pagination** |
| F | `templates/finance/cn_form.html` | Bootstrap form card with `widget_tweaks` |
| G | `templates/base.html` | Sidebar `<a>` with active-state check |
| H | Terminal | `makemigrations finance` then `migrate` |

---

### Pagination in List Templates (mandatory)

**Every list template must include pagination.** Use the same JS pattern as
reports. Copy the block below into every `*_list.html`.

#### 1. CSS (in `{% block extra_css %}`)

```css
.pagination-bar {
    padding: 0.75rem 1rem; border-top: 1px solid #e9ecef; background: #fafafa;
    border-radius: 0 0 14px 14px;
    display: flex; align-items: center; justify-content: space-between;
    flex-wrap: wrap; gap: 0.5rem;
}
.pagination-info { font-size: 0.8rem; color: #6c757d; }
.page-nums { display: flex; gap: 4px; flex-wrap: wrap; }
.page-btn {
    border: 1px solid #dee2e6; background: #fff; color: #495057;
    border-radius: 6px; padding: 0.3rem 0.65rem;
    font-size: 0.8rem; cursor: pointer; transition: all 0.15s; line-height: 1.4;
}
.page-btn:hover:not(.active):not(:disabled) { background:#f0f4ff; border-color:#4361ee; color:#4361ee; }
.page-btn.active   { background:#1a2e52; border-color:#1a2e52; color:#fff; font-weight:600; }
.page-btn:disabled { opacity:0.4; cursor:not-allowed; }
```

#### 2. HTML — pagination bar (immediately after `</div>` of `table-responsive`)

```html
<div class="pagination-bar" id="paginationBar" style="display:none;">
    <div class="pagination-info" id="pageInfo"></div>
    <div class="page-nums"      id="pageNums"></div>
</div>
```

Give the empty-row a unique id so JS can exclude it:

```html
{% empty %}
<tr id="emptyRow"><td colspan="N">...</td></tr>
```

#### 3. JavaScript (in `{% block extra_js %}`)

```js
const PAGE_SIZE = 25;
let currentPage = 1;
let allRows = [];

document.addEventListener('DOMContentLoaded', function () {
    const tbody = document.querySelector('#listTable tbody');
    if (!tbody) return;

    allRows = Array.from(tbody.querySelectorAll('tr:not(#emptyRow)'));
    if (allRows.length === 0) return;   // nothing to paginate — hide bar

    document.getElementById('paginationBar').style.display = 'flex';
    renderPage(1);
});

function renderPage(page) {
    currentPage  = page;
    const total      = allRows.length;
    const totalPages = Math.ceil(total / PAGE_SIZE);
    const start      = (page - 1) * PAGE_SIZE;
    const end        = Math.min(start + PAGE_SIZE, total);

    allRows.forEach((r, i) => r.style.display = (i >= start && i < end) ? '' : 'none');

    document.getElementById('pageInfo').textContent =
        'Showing ' + (start + 1) + '–' + end + ' of ' + total + ' records';

    const container = document.getElementById('pageNums');
    container.innerHTML = '';

    const prev = makeBtn('‹ Prev', page <= 1);
    prev.onclick = () => renderPage(page - 1);
    container.appendChild(prev);

    const pages = new Set([1, totalPages]);
    for (let p = Math.max(1, page-2); p <= Math.min(totalPages, page+2); p++) pages.add(p);
    let prev_p = 0;
    Array.from(pages).sort((a,b) => a-b).forEach(p => {
        if (p - prev_p > 1) {
            const gap = document.createElement('span');
            gap.textContent = '…'; gap.style.cssText = 'padding:0.3rem 0.4rem;font-size:0.8rem;color:#adb5bd;';
            container.appendChild(gap);
        }
        const btn = makeBtn(p, false);
        if (p === page) btn.classList.add('active');
        btn.onclick = () => renderPage(p);
        container.appendChild(btn);
        prev_p = p;
    });

    const next = makeBtn('Next ›', page >= totalPages);
    next.onclick = () => renderPage(page + 1);
    container.appendChild(next);
}

function makeBtn(label, disabled) {
    const btn = document.createElement('button');
    btn.className = 'page-btn'; btn.textContent = label; btn.disabled = disabled;
    return btn;
}
```

#### Key rules

| Rule | Detail |
|------|--------|
| `PAGE_SIZE = 25` | 25 rows per page — change if needed |
| `style="display:none;"` on bar | Bar auto-shows only when rows exist (JS sets to `flex`) |
| `tr:not(#emptyRow)` selector | Excludes the Django `{% empty %}` row from the row list |
| Table must have `id="listTable"` | JS targets this id |
