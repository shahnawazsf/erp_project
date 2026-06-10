# Chart Implementation Guide - Step by Step

**Date:** June 2026  
**Version:** 1.0  
**Status:** ✅ Practical Guide  
**Example:** Container Received & Shipped Line Chart

---

## Table of Contents

1. [Overview](#overview)
2. [3-Step Implementation](#3-step-implementation)
3. [Detailed Examples](#detailed-examples)
4. [Chart Types & Customization](#chart-types--customization)
5. [Troubleshooting](#troubleshooting)

---

## Overview

To add a chart to the Operations Dashboard from a database query, you need:

```
Query Function → Format Data → Display in Template
    (views.py)    (views.py)    (dashboard.html)
```

**Example:** Container Received & Shipped Line Chart

---

## 3-Step Implementation

### **Step 1️⃣: Create Query Function** (operations/views.py)

```python
def get_container_daily_summary():
    """Get container received and shipped by day for chart"""
    from django.db import connection
    
    query = """
        SELECT ACTION_DATE, ACTION_DAY, RECVD_QTY, SHIPPED_QTY
        FROM TABLE (GET_RECVD_SHIPPED_DATE_LIST)
        ORDER BY ACTION_DATE ASC
    """
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            print(f"DEBUG: Retrieved {len(data)} records")
            return data
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return []
```

**Key Points:**
- ✅ Always use `try/except` for error handling
- ✅ Return list of dictionaries with column names as keys
- ✅ Add debug print statements
- ✅ Return empty list on error

---

### **Step 2️⃣: Format Data for Chart** (operations/views.py)

```python
def get_container_chart_data():
    """Format data for Chart.js line chart"""
    import json
    
    # Get raw data from query
    data = get_container_daily_summary()
    
    if not data:
        return json.dumps({
            'labels': [],
            'recvd_data': [],
            'shipped_data': []
        })
    
    # Extract and transform data
    labels = []
    recvd_data = []
    shipped_data = []
    
    for item in data:
        try:
            day = int(str(item['ACTION_DAY']).strip())
            labels.append(str(day))
            recvd_data.append(int(item['RECVD_QTY']) if item['RECVD_QTY'] else 0)
            shipped_data.append(int(item['SHIPPED_QTY']) if item['SHIPPED_QTY'] else 0)
        except Exception as e:
            print(f"ERROR processing item: {str(e)}")
            continue
    
    # Return as JSON
    return json.dumps({
        'labels': labels,
        'recvd_data': recvd_data,
        'shipped_data': shipped_data
    })
```

**Key Points:**
- ✅ Extract values from each row
- ✅ Transform to proper types (int, str, float)
- ✅ Handle NULL values with `if item['COLUMN'] else 0`
- ✅ Return JSON formatted data

---

### **Step 3️⃣: Add to Views Context** (operations/views.py)

```python
@login_required
def operations_dashboard(request):
    context = {
        # Card 1: Container Chart
        'container_chart_data': _safe('{}', lambda: get_container_chart_data()),
    }
    return render(request, 'operations/dashboard.html', context)
```

**Key Points:**
- ✅ Use `_safe()` to handle errors gracefully
- ✅ Default to empty JSON object `'{}'`
- ✅ Pass data to template via context

---

## Detailed Examples

### Example 1: Simple Line Chart (2 Lines)

**Query:**
```python
query = """
    SELECT DATE_COL, VALUE1, VALUE2
    FROM MY_TABLE
    ORDER BY DATE_COL ASC
"""
```

**Format Function:**
```python
def get_chart_data():
    data = get_raw_data()  # Your query function
    labels = []
    line1_data = []
    line2_data = []
    
    for item in data:
        labels.append(item['DATE_COL'].strftime('%Y-%m-%d'))
        line1_data.append(int(item['VALUE1']))
        line2_data.append(int(item['VALUE2']))
    
    return json.dumps({
        'labels': labels,
        'line1': line1_data,
        'line2': line2_data
    })
```

**Template:**
```html
<script>
const data = JSON.parse('{{ chart_data|safe }}');
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: data.labels,
        datasets: [
            {
                label: 'Series 1',
                data: data.line1,
                borderColor: '#27a745'
            },
            {
                label: 'Series 2',
                data: data.line2,
                borderColor: '#007bff'
            }
        ]
    }
});
</script>
```

---

### Example 2: Bar Chart (Single Series)

**Query:**
```python
query = """
    SELECT CATEGORY, COUNT(*) as TOTAL
    FROM TRANSACTIONS
    GROUP BY CATEGORY
    ORDER BY TOTAL DESC
"""
```

**Format Function:**
```python
def get_bar_chart_data():
    data = get_raw_data()
    categories = []
    values = []
    
    for item in data:
        categories.append(item['CATEGORY'])
        values.append(int(item['TOTAL']))
    
    return json.dumps({
        'labels': categories,
        'data': values
    })
```

**Template:**
```html
<script>
const data = JSON.parse('{{ bar_chart_data|safe }}');
const chart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: data.labels,
        datasets: [{
            label: 'Count',
            data: data.data,
            backgroundColor: '#007bff'
        }]
    }
});
</script>
```

---

### Example 3: Pie/Doughnut Chart

**Query:**
```python
query = """
    SELECT STATUS, COUNT(*) as COUNT
    FROM ORDERS
    GROUP BY STATUS
"""
```

**Format Function:**
```python
def get_pie_chart_data():
    data = get_raw_data()
    labels = []
    values = []
    colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
    
    for item in data:
        labels.append(item['STATUS'])
        values.append(int(item['COUNT']))
    
    return json.dumps({
        'labels': labels,
        'data': values,
        'colors': colors
    })
```

**Template:**
```html
<script>
const data = JSON.parse('{{ pie_chart_data|safe }}');
const chart = new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: data.labels,
        datasets: [{
            data: data.data,
            backgroundColor: data.colors
        }]
    }
});
</script>
```

---

## Chart Types & Customization

### Supported Chart Types

| Type | Use Case | Colors |
|------|----------|--------|
| `line` | Trends over time | Primary (Blue), Success (Green) |
| `bar` | Comparisons | Info (Cyan), Warning (Orange) |
| `doughnut` | Parts of whole | Multiple colors |
| `pie` | Proportions | Multiple colors |
| `area` | Cumulative data | Fill colors |

### Color Reference

```javascript
// Bootstrap Colors
Primary:   '#0d6efd'
Success:   '#27a745'
Info:      '#007bff'
Warning:   '#ffc107'
Danger:    '#dc3545'
Dark:      '#1a2035'
```

### Common Customizations

#### **1. Change Line Style**
```javascript
datasets: [{
    borderDash: [5, 5],        // Dashed line
    borderWidth: 2,            // Line thickness
    tension: 0.3,              // Curve smoothness
    fill: false                // No fill under line
}]
```

#### **2. Add Grid Lines**
```javascript
scales: {
    y: {
        grid: {
            color: 'rgba(0, 0, 0, 0.1)',
            drawBorder: true
        }
    }
}
```

#### **3. Format Tooltip**
```javascript
plugins: {
    tooltip: {
        callbacks: {
            label: function(context) {
                return context.dataset.label + ': ' + 
                       context.parsed.y + ' items';
            }
        }
    }
}
```

#### **4. Add Legend**
```javascript
plugins: {
    legend: {
        position: 'top',
        labels: {
            font: { size: 14, weight: 'bold' }
        }
    }
}
```

---

## Step-by-Step: Add New Chart

### Step 1: Write & Test Query
```sql
-- Test in SQL Developer first
SELECT YOUR_COLUMNS FROM YOUR_TABLE ORDER BY DATE_COLUMN;
```

### Step 2: Create Query Function in views.py
```python
def get_your_data():
    from django.db import connection
    query = """SELECT..."""
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return []
```

### Step 3: Create Format Function in views.py
```python
def get_your_chart_data():
    import json
    data = get_your_data()
    
    labels = []
    values = []
    
    for item in data:
        # Extract and transform
        labels.append(item['COLUMN1'])
        values.append(int(item['COLUMN2']))
    
    return json.dumps({'labels': labels, 'data': values})
```

### Step 4: Add to Context in views.py
```python
context = {
    'your_chart_data': _safe('{}', lambda: get_your_chart_data()),
}
```

### Step 5: Add HTML in Template
```html
<div class="card">
    <div class="card-header">Your Chart Title</div>
    <div class="card-body">
        <canvas id="yourChart"></canvas>
    </div>
</div>
```

### Step 6: Add JavaScript in Template
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    const data = JSON.parse('{{ your_chart_data|safe }}');
    const ctx = document.getElementById('yourChart');
    
    new Chart(ctx, {
        type: 'line',  // or bar, pie, doughnut, etc.
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Your Label',
                data: data.data,
                borderColor: '#007bff'
            }]
        }
    });
});
</script>
```

---

## Troubleshooting

### Issue: Chart is Blank

**Cause:** No data returned from query  
**Fix:**
```python
# Add debug print
print(f"Data: {data}")
print(f"Labels: {labels}")
print(f"Values: {values}")
```

### Issue: Chart Shows Error

**Cause:** Invalid JSON or missing columns  
**Fix:**
- Check exact column names from database
- Verify JSON format is valid
- Test query in SQL Developer first

### Issue: Chart Not Showing

**Cause:** Chart.js not loaded or canvas element missing  
**Fix:**
```html
<!-- Verify library is included -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<!-- Verify canvas element exists -->
<canvas id="myChart"></canvas>
```

### Issue: Data Type Errors

**Cause:** Mixing strings and numbers  
**Fix:**
```python
# Always convert to proper types
labels.append(str(item['COL']))      # String
values.append(int(item['COL']))      # Integer
decimals.append(float(item['COL']))  # Float
```

---

## Real World Example: Container Chart

**Complete Code:**

**views.py:**
```python
def get_container_daily_summary():
    from django.db import connection
    query = """
        SELECT ACTION_DATE, ACTION_DAY, RECVD_QTY, SHIPPED_QTY
        FROM TABLE (GET_RECVD_SHIPPED_DATE_LIST)
        ORDER BY ACTION_DATE ASC
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return data
    except Exception as e:
        return []

def get_container_chart_data():
    import json
    data = get_container_daily_summary()
    
    labels = []
    recvd_data = []
    shipped_data = []
    
    for item in data:
        labels.append(str(int(item['ACTION_DAY'])))
        recvd_data.append(int(item['RECVD_QTY']) if item['RECVD_QTY'] else 0)
        shipped_data.append(int(item['SHIPPED_QTY']) if item['SHIPPED_QTY'] else 0)
    
    return json.dumps({
        'labels': labels,
        'recvd_data': recvd_data,
        'shipped_data': shipped_data
    })

@login_required
def operations_dashboard(request):
    context = {
        'container_chart_data': _safe('{}', lambda: get_container_chart_data()),
    }
    return render(request, 'operations/dashboard.html', context)
```

**dashboard.html:**
```html
<div class="card">
    <div class="card-header bg-light">
        <h6 class="mb-0">📦 Containers Received & Shipped</h6>
    </div>
    <div class="card-body">
        <canvas id="containerChart" height="80"></canvas>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    const chartData = JSON.parse('{{ container_chart_data|safe }}');
    const ctx = document.getElementById('containerChart');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [
                {
                    label: 'Received',
                    data: chartData.recvd_data,
                    borderColor: '#27a745',
                    backgroundColor: 'rgba(39, 167, 69, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Shipped',
                    data: chartData.shipped_data,
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }
            ]
        }
    });
});
</script>
```

---

## Quick Checklist for Adding Charts

- [ ] Test query in SQL Developer
- [ ] Create query function in views.py
- [ ] Create format function in views.py
- [ ] Add to context dictionary
- [ ] Add HTML card in template
- [ ] Add Chart.js script tag
- [ ] Add JavaScript chart creation
- [ ] Test in browser
- [ ] Check console (F12) for errors
- [ ] Add debug print statements

---

## File Locations

| File | What | Location |
|------|------|----------|
| **Query Functions** | `get_your_data()` | `operations/views.py` |
| **Format Functions** | `get_your_chart_data()` | `operations/views.py` |
| **Context** | Pass to template | `operations_dashboard()` |
| **HTML Card** | Chart container | `operations/templates/operations/dashboard.html` |
| **JavaScript** | Chart initialization | Same template file |

---

## Related Documentation

- [OPERATIONS_QUICK_START.md](OPERATIONS_QUICK_START.md) — Quick reference
- [OPERATIONS_MODULE_GUIDE.md](OPERATIONS_MODULE_GUIDE.md) — Module details

---

**Created:** June 2026  
**Last Updated:** June 10, 2026  
**Author:** Claude Code Assistant
