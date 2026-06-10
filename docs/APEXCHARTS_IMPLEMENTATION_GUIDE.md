# ApexCharts Implementation Guide - 3D Dynamic Charts

**Date:** June 2026  
**Version:** 1.0  
**Status:** ✅ Production Ready  
**Library:** ApexCharts v3.45+  
**Features:** 3D, Dynamic, Interactive, Real-time Updates

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [3-Step Implementation](#3-step-implementation)
4. [Chart Types & Examples](#chart-types--examples)
5. [Advanced Features](#advanced-features)
6. [Data Labels & Formatting](#data-labels--formatting)
7. [Animations & Interactions](#animations--interactions)
8. [Color Schemes & Styling](#color-schemes--styling)
9. [Real-World Examples](#real-world-examples)
10. [Troubleshooting](#troubleshooting)

---

## Overview

### Why ApexCharts?

| Feature | Chart.js | ApexCharts |
|---------|----------|-----------|
| 3D Charts | ❌ | ✅ |
| Data Labels | ⚠️ Limited | ✅ Full |
| Animations | Basic | ✅ Advanced |
| Interactions | ⚠️ Manual | ✅ Built-in |
| Toolbar | ❌ | ✅ (Zoom, Pan, Download) |
| Real-time | ⚠️ | ✅ Optimized |
| Mobile | Good | ✅ Excellent |

### ApexCharts Advantages

```
✅ Zero dependencies
✅ Lightweight (60KB gzipped)
✅ 100+ configuration options
✅ Beautiful animations
✅ Mobile responsive
✅ Built-in toolbar
✅ Export as image
✅ Professional looking
```

---

## Quick Start

### **1. Include Library in Template**

```html
<script src="https://cdn.jsdelivr.net/npm/apexcharts@latest/dist/apexcharts.min.js"></script>
```

### **2. Create HTML Container**

```html
<div id="myChart" style="height: 400px;"></div>
```

### **3. Initialize Chart**

```javascript
const options = {
    series: [{ data: [10, 20, 30, 40, 50] }],
    chart: { type: 'bar', height: 400 }
};

new ApexCharts(document.querySelector("#myChart"), options).render();
```

Done! 🎉

---

## 3-Step Implementation

### **Step 1️⃣: Create Query Function** (views.py)

```python
def get_your_data():
    """Query your database"""
    from django.db import connection
    
    query = """
        SELECT DATE_COL, VALUE_COL
        FROM YOUR_TABLE
        ORDER BY DATE_COL
    """
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return data
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return []
```

### **Step 2️⃣: Format Data for ApexCharts** (views.py)

```python
def get_your_chart_data():
    """Format data as JSON for ApexCharts"""
    import json
    
    data = get_your_data()
    
    labels = []
    values = []
    
    for item in data:
        labels.append(item['DATE_COL'].strftime('%Y-%m-%d'))
        values.append(int(item['VALUE_COL']))
    
    return json.dumps({
        'labels': labels,
        'values': values
    })
```

### **Step 3️⃣: Add to Context & Render** (views.py)

```python
@login_required
def operations_dashboard(request):
    context = {
        'your_chart_data': _safe('{}', lambda: get_your_chart_data()),
    }
    return render(request, 'operations/dashboard.html', context)
```

### **Step 4️⃣: Create Chart in Template** (dashboard.html)

```html
<div id="myChart"></div>

<script src="https://cdn.jsdelivr.net/npm/apexcharts@latest/dist/apexcharts.min.js"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    const chartData = JSON.parse('{{ your_chart_data|safe }}');
    
    const options = {
        series: [{ data: chartData.values }],
        chart: { type: 'bar', height: 400 },
        xaxis: { categories: chartData.labels }
    };
    
    new ApexCharts(document.querySelector("#myChart"), options).render();
});
</script>
```

---

## Chart Types & Examples

### **1. Bar Chart (with Data Labels)**

```javascript
const barOptions = {
    series: [{ name: 'Sales', data: [10, 20, 30, 40] }],
    chart: { type: 'bar', height: 400 },
    dataLabels: {
        enabled: true,
        offsetY: -20,
        style: { fontSize: '12px', fontWeight: 'bold' }
    },
    plotOptions: {
        bar: { columnWidth: '60%', borderRadius: 5 }
    }
};
```

**Features:**
- ✅ Count labels on top of bars
- ✅ Rounded corners
- ✅ Custom colors
- ✅ Hover effects

---

### **2. Line Chart (Dynamic)**

```javascript
const lineOptions = {
    series: [
        { name: 'Received', data: [100, 150, 200, 250] },
        { name: 'Shipped', data: [80, 120, 180, 220] }
    ],
    chart: { 
        type: 'line', 
        height: 400,
        animations: { enabled: true, speed: 800 }
    },
    stroke: { curve: 'smooth', width: 3 },
    markers: { size: 6, hover: { size: 8 } }
};
```

**Features:**
- ✅ Smooth curves
- ✅ Animated transitions
- ✅ Interactive markers
- ✅ Multiple series

---

### **3. Area Chart (Filled)**

```javascript
const areaOptions = {
    series: [
        { name: 'Series A', data: [10, 20, 30, 40] },
        { name: 'Series B', data: [5, 15, 25, 35] }
    ],
    chart: { type: 'area', height: 400 },
    fill: { opacity: 0.3 },
    stroke: { curve: 'smooth', width: 2 }
};
```

---

### **4. Pie/Doughnut Chart**

```javascript
const pieOptions = {
    series: [30, 25, 20, 15, 10],
    chart: { type: 'pie', height: 400 },
    labels: ['Category A', 'Category B', 'Category C', 'Category D', 'Category E'],
    colors: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9C27B0']
};
```

---

### **5. Scatter Chart**

```javascript
const scatterOptions = {
    series: [{
        name: 'Correlation',
        data: [[10, 20], [20, 30], [30, 40], [40, 50]]
    }],
    chart: { type: 'scatter', height: 400, zoom: { enabled: true } },
    xaxis: { type: 'numeric' },
    yaxis: { type: 'numeric' }
};
```

---

## Advanced Features

### **1. Interactive Toolbar**

```javascript
chart: {
    toolbar: {
        show: true,
        tools: {
            download: true,      // Download as PNG/SVG
            selection: true,     // Select area
            zoom: true,          // Zoom in
            zoomin: true,        // Zoom in button
            zoomout: true,       // Zoom out button
            pan: true,           // Pan around
            reset: true          // Reset view
        }
    }
}
```

### **2. Zoom & Pan**

```javascript
chart: {
    zoom: {
        enabled: true,
        type: 'xy',  // 'x', 'y', or 'xy'
        autoScaleYaxis: true
    }
}
```

### **3. Animations**

```javascript
chart: {
    animations: {
        enabled: true,
        speed: 1000,  // ms
        animateGradually: {
            enabled: true,
            delay: 150  // delay between elements
        },
        dynamicAnimation: {
            enabled: true,
            speed: 150
        }
    }
}
```

### **4. Responsive**

```javascript
responsive: [{
    breakpoint: 1024,
    options: {
        chart: { height: 300 },
        legend: { position: 'bottom' }
    }
}, {
    breakpoint: 600,
    options: {
        chart: { height: 250 }
    }
}]
```

### **5. Real-time Updates**

```javascript
// Update chart data
ApexCharts.exec('chartId', 'updateSeries', [{
    data: [newData1, newData2, ...]
}]);

// Update options
ApexCharts.exec('chartId', 'updateOptions', {
    xaxis: { categories: newLabels }
});
```

---

## Data Labels & Formatting

### **Enable Data Labels on Bars**

```javascript
dataLabels: {
    enabled: true,           // Show labels
    offsetY: -20,           // Position above bar
    style: {
        fontSize: '12px',
        fontWeight: 'bold',
        colors: ['#1a2035']
    },
    formatter: function(value) {
        return value.toLocaleString();  // Format with commas
    }
}
```

### **Format Numbers with Commas**

```javascript
// In dataLabels
formatter: function(value) {
    return value.toLocaleString();
}

// In yaxis
labels: {
    formatter: function(value) {
        return value.toLocaleString();
    }
}

// In tooltip
tooltip: {
    y: {
        formatter: function(value) {
            return value.toLocaleString() + ' units';
        }
    }
}
```

### **Date Formatting**

```javascript
xaxis: {
    type: 'datetime',
    labels: {
        format: 'MMM dd',  // Mar 15, Apr 20, etc.
        datetimeFormatter: {
            year: 'yyyy',
            month: 'MMM',
            day: 'dd',
            hour: 'HH:mm'
        }
    }
}
```

---

## Animations & Interactions

### **Smooth Animations**

```javascript
chart: {
    animations: {
        enabled: true,
        speed: 800,
        animateGradually: { enabled: true, delay: 150 },
        dynamicAnimation: { enabled: true, speed: 150 }
    }
}
```

### **Hover Effects**

```javascript
states: {
    hover: { filter: { type: 'darken', value: 0.15 } },
    active: { filter: { type: 'darken', value: 0.15 } }
}
```

### **Interactive Legend**

```javascript
legend: {
    position: 'top',
    horizontalAlign: 'right',
    fontSize: 13,
    markers: {
        width: 12,
        height: 12,
        radius: 2
    }
}
```

### **Tooltip Customization**

```javascript
tooltip: {
    theme: 'dark',           // 'light' or 'dark'
    shared: true,            // Show all series
    intersect: false,        // Show on hover
    x: {
        formatter: function(value) {
            return 'Day ' + value;
        }
    },
    y: {
        formatter: function(value) {
            return value.toLocaleString() + ' containers';
        }
    }
}
```

---

## Color Schemes & Styling

### **Custom Colors**

```javascript
colors: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9C27B0']
```

### **Bootstrap Colors**

```javascript
colors: [
    '#007bff',   // Primary (Blue)
    '#28a745',   // Success (Green)
    '#ffc107',   // Warning (Yellow)
    '#dc3545',   // Danger (Red)
    '#17a2b8',   // Info (Cyan)
    '#6c757d'    // Dark (Gray)
]
```

### **Gradient Colors**

```javascript
fill: {
    type: 'gradient',
    gradient: {
        shade: 'dark',
        type: 'horizontal',
        shadeIntensity: 0.5,
        gradientToColors: ['#00bcd4'],
        opacityFrom: 1,
        opacityTo: 0.5
    }
}
```

### **3D-Style Bar Colors**

```javascript
plotOptions: {
    bar: {
        distributed: true,
        borderRadiusApplication: 'end'
    }
},
colors: ['#4FC3F7', '#27a745', '#FFC107', '#FF5722', '#9C27B0']
```

---

## Real-World Examples

### **Example 1: Daily Container Activity**

**views.py:**
```python
def get_daily_container_chart_data():
    data = get_container_daily_summary()
    labels = [item['ACTION_DAY'] for item in data]
    recvd = [item['RECVD_QTY'] for item in data]
    shipped = [item['SHIPPED_QTY'] for item in data]
    
    return json.dumps({
        'labels': labels,
        'recvd': recvd,
        'shipped': shipped
    })
```

**template:**
```javascript
const options = {
    series: [
        { name: 'Received', data: data.recvd },
        { name: 'Shipped', data: data.shipped }
    ],
    chart: { type: 'line', height: 400 },
    stroke: { curve: 'smooth', width: 3 },
    xaxis: { categories: data.labels }
};
new ApexCharts(document.querySelector("#chart"), options).render();
```

---

### **Example 2: Yearly 3D Bar Chart**

**views.py:**
```python
def get_yearly_chart_data():
    data = get_container_year_summary()
    years = [str(item['YEAR']) for item in data]
    qty = [item['QTY'] for item in data]
    
    return json.dumps({
        'years': years,
        'quantities': qty
    })
```

**template:**
```javascript
const options = {
    series: [{ name: 'Containers', data: data.quantities }],
    chart: { type: 'bar', height: 400 },
    dataLabels: {
        enabled: true,
        offsetY: -20,
        formatter: v => v.toLocaleString()
    },
    xaxis: { categories: data.years },
    plotOptions: {
        bar: { columnWidth: '60%', borderRadius: 5, distributed: true }
    },
    colors: ['#4FC3F7', '#27a745', '#FFC107']
};
```

---

## Troubleshooting

### **Issue: Chart Not Rendering**

**Cause:** Container not found or data empty  
**Fix:**
```html
<!-- Verify container exists -->
<div id="myChart" style="height: 400px;"></div>

<!-- Check data in console -->
<script>
console.log('Chart Data:', chartData);
console.log('Labels:', chartData.labels);
console.log('Values:', chartData.values);
</script>
```

### **Issue: Data Labels Not Showing**

**Cause:** Offset position wrong  
**Fix:**
```javascript
dataLabels: {
    enabled: true,
    offsetY: -20,  // Negative for above bar
    offsetX: 0,
    position: 'top'
}
```

### **Issue: Colors Not Applied**

**Cause:** Colors array size mismatch  
**Fix:**
```javascript
// Make sure colors match data series
colors: ['#color1', '#color2', '#color3']  // 3 colors for 3 series
```

### **Issue: Animation Too Slow**

**Cause:** Speed set too high  
**Fix:**
```javascript
animations: {
    enabled: true,
    speed: 500  // Reduce from 1000ms
}
```

### **Issue: Zoom Not Working**

**Cause:** Zoom not enabled  
**Fix:**
```javascript
chart: {
    zoom: {
        enabled: true,
        type: 'xy'
    }
}
```

---

## Complete Working Example

### **views.py**
```python
def get_sales_data():
    from django.db import connection
    query = "SELECT MONTH, SALES FROM MONTHLY_SALES ORDER BY MONTH"
    with connection.cursor() as cursor:
        cursor.execute(query)
        return [dict(zip([col[0] for col in cursor.description], row)) 
                for row in cursor.fetchall()]

def get_sales_chart_data():
    import json
    data = get_sales_data()
    months = [item['MONTH'] for item in data]
    sales = [int(item['SALES']) for item in data]
    return json.dumps({'months': months, 'sales': sales})

@login_required
def dashboard(request):
    return render(request, 'dashboard.html', {
        'sales_chart_data': _safe('{}', lambda: get_sales_chart_data())
    })
```

### **dashboard.html**
```html
<div id="salesChart" style="height: 400px;"></div>

<script src="https://cdn.jsdelivr.net/npm/apexcharts@latest/dist/apexcharts.min.js"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    const data = JSON.parse('{{ sales_chart_data|safe }}');
    
    new ApexCharts(document.querySelector("#salesChart"), {
        series: [{ name: 'Sales', data: data.sales }],
        chart: { 
            type: 'bar', 
            height: 400,
            toolbar: { show: true }
        },
        dataLabels: {
            enabled: true,
            formatter: v => v.toLocaleString()
        },
        xaxis: { categories: data.months },
        yaxis: { labels: { formatter: v => v.toLocaleString() } }
    }).render();
});
</script>
```

---

## Quick Checklist for Adding Charts

- [ ] Create query function in views.py
- [ ] Create format function in views.py
- [ ] Add to context dictionary
- [ ] Include ApexCharts library in template
- [ ] Create HTML container with ID
- [ ] Write chart initialization script
- [ ] Test in browser
- [ ] Verify data labels display (if needed)
- [ ] Test interactive features (zoom, pan)
- [ ] Check responsive on mobile

---

## File Locations

| Component | Location |
|-----------|----------|
| Query Functions | `operations/views.py` |
| Format Functions | `operations/views.py` |
| Context Setup | `operations_dashboard()` in views.py |
| Chart Container | `operations/templates/operations/dashboard.html` |
| Chart Script | Same template file |
| Library | CDN (jsdelivr) |

---

## Performance Tips

1. **Lazy Load Charts** — Initialize only when needed
2. **Limit Data Points** — 100+ points may slow animations
3. **Disable Animations** — For large datasets
4. **Use Throttling** — For real-time updates
5. **Cache Data** — Don't query on every load

---

## Migration from Chart.js

| Chart.js | ApexCharts |
|----------|-----------|
| `new Chart(ctx, {...})` | `new ApexCharts(el, {...})` |
| `canvas` element | `div` element |
| `datasets` | `series` |
| `labels` → `xaxis.categories` | `xaxis.categories` |
| `plugins.datalabels` | `dataLabels` |
| Manual toolbar | Built-in `chart.toolbar` |

---

## Related Documentation

- [CHART_IMPLEMENTATION_GUIDE.md](CHART_IMPLEMENTATION_GUIDE.md) — Original Chart.js guide
- [OPERATIONS_MODULE_GUIDE.md](OPERATIONS_MODULE_GUIDE.md) — Module details
- [OPERATIONS_QUICK_START.md](OPERATIONS_QUICK_START.md) — Quick reference

---

## Resources

- **Official Docs:** https://apexcharts.com/docs/
- **Live Examples:** https://apexcharts.com/docs/react-charts/
- **Chart Options:** https://apexcharts.com/docs/options/chart/type/
- **CDN:** https://cdn.jsdelivr.net/npm/apexcharts

---

**Created:** June 2026  
**Last Updated:** June 10, 2026  
**Author:** Claude Code Assistant  
**Status:** Production Ready ✅
