const SEGMENT_COLORS = {
  'Champions': '#00D4AA',
  'Loyal Customers': '#4ECDC4',
  'Potential Loyalists': '#45B7D1',
  'Recent Customers': '#96CEB4',
  'Promising': '#FFEAA7',
  'Need Attention': '#FF8C42',
  'About to Sleep': '#DDA0DD',
  'At Risk': '#FF6B6B',
  "Can't Lose Them": '#FF85A2',
  'Hibernating': '#6C5CE7',
  'Lost': '#636e72',
  'Other': '#888888'
};

// Global Chart defaults for dark theme
Chart.defaults.color = '#8888aa';
Chart.defaults.font.family = 'Inter, sans-serif';
Chart.defaults.scale.grid.color = 'rgba(255, 255, 255, 0.05)';
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(22, 33, 62, 0.9)';
Chart.defaults.plugins.tooltip.titleColor = '#e8e8f0';
Chart.defaults.plugins.tooltip.bodyColor = '#e8e8f0';
Chart.defaults.plugins.tooltip.borderColor = 'rgba(255, 255, 255, 0.1)';
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.padding = 10;
Chart.defaults.plugins.tooltip.cornerRadius = 8;

let rfmData = [];
let transactionsData = [];
let tableSortColumn = 'Monetary';
let tableSortAsc = false;

document.addEventListener('DOMContentLoaded', () => {
  loadData();
});

async function loadData() {
  try {
    const [rfmRes, transRes] = await Promise.all([
      fetch('./data/rfm_segments.csv'),
      fetch('./data/cleaned_transactions.csv')
    ]);

    if (!rfmRes.ok || !transRes.ok) {
        console.warn("Could not fetch CSV data, please ensure files exist. We will render empty state.");
    }

    const rfmText = await rfmRes.text();
    const transText = await transRes.text();

    Papa.parse(rfmText, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      complete: function(results) {
        rfmData = results.data;
        if(rfmData.length > 0) {
            initDashboard();
        }
      }
    });

    Papa.parse(transText, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      complete: function(results) {
        transactionsData = results.data;
        if(transactionsData.length > 0) {
             initTransactionsCharts();
        }
      }
    });

  } catch (error) {
    console.error("Error loading data:", error);
    document.getElementById('kpi-customers').textContent = 'Error';
  }
}

function initDashboard() {
  calculateKPIs();
  createSegmentDistributionChart();
  createSegmentDoughnutChart();
  createRfmScoreChart();
  createMonetaryBySegmentChart();
  initTable();
}

function initTransactionsCharts() {
    createRevenueTrendChart();
    createCountryRevenueChart();
}

function formatCurrency(num) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(num || 0);
}

function formatNumber(num) {
  return new Intl.NumberFormat('en-US').format(num || 0);
}

function calculateKPIs() {
  const totalCustomers = rfmData.length;
  const totalRevenue = rfmData.reduce((sum, row) => sum + (row.Monetary || 0), 0);
  const totalFrequency = rfmData.reduce((sum, row) => sum + (row.Frequency || 0), 0);
  const avgOrderValue = totalFrequency > 0 ? totalRevenue / totalFrequency : 0;
  const avgRecency = rfmData.reduce((sum, row) => sum + (row.Recency || 0), 0) / (totalCustomers || 1);

  document.getElementById('kpi-customers').textContent = formatNumber(totalCustomers);
  document.getElementById('kpi-revenue').textContent = formatCurrency(totalRevenue);
  document.getElementById('kpi-aov').textContent = formatCurrency(avgOrderValue);
  document.getElementById('kpi-recency').textContent = formatNumber(Math.round(avgRecency)) + ' days';
}

function getSegmentCounts() {
  const counts = {};
  rfmData.forEach(row => {
    const seg = row.Segment || 'Other';
    counts[seg] = (counts[seg] || 0) + 1;
  });
  return Object.entries(counts).sort((a, b) => b[1] - a[1]);
}

function createSegmentDistributionChart() {
  const sortedCounts = getSegmentCounts();
  const labels = sortedCounts.map(item => item[0]);
  const data = sortedCounts.map(item => item[1]);
  const bgColors = labels.map(label => SEGMENT_COLORS[label] || SEGMENT_COLORS['Other']);

  const ctx = document.getElementById('segmentDistributionChart').getContext('2d');
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Customers',
        data: data,
        backgroundColor: bgColors,
        borderRadius: 4
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      }
    }
  });
}

function createSegmentDoughnutChart() {
  const sortedCounts = getSegmentCounts();
  const labels = sortedCounts.map(item => item[0]);
  const data = sortedCounts.map(item => item[1]);
  const bgColors = labels.map(label => SEGMENT_COLORS[label] || SEGMENT_COLORS['Other']);

  const ctx = document.getElementById('segmentDoughnutChart').getContext('2d');
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: bgColors,
        borderWidth: 0,
        hoverOffset: 10
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '70%',
      plugins: {
        legend: { position: 'right', labels: { boxWidth: 12, usePointStyle: true } }
      }
    }
  });
}

function createRfmScoreChart() {
  const rCounts = {1:0,2:0,3:0,4:0,5:0};
  const fCounts = {1:0,2:0,3:0,4:0,5:0};
  const mCounts = {1:0,2:0,3:0,4:0,5:0};

  rfmData.forEach(row => {
    if(row.R_Score) rCounts[row.R_Score]++;
    if(row.F_Score) fCounts[row.F_Score]++;
    if(row.M_Score) mCounts[row.M_Score]++;
  });

  const labels = ['1', '2', '3', '4', '5'];
  
  const ctx = document.getElementById('rfmScoreChart').getContext('2d');
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        { label: 'Recency', data: labels.map(l => rCounts[l]), backgroundColor: '#00D4AA', borderRadius: 4 },
        { label: 'Frequency', data: labels.map(l => fCounts[l]), backgroundColor: '#45B7D1', borderRadius: 4 },
        { label: 'Monetary', data: labels.map(l => mCounts[l]), backgroundColor: '#6C5CE7', borderRadius: 4 }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false }
    }
  });
}

function createMonetaryBySegmentChart() {
  const sums = {};
  const counts = {};
  rfmData.forEach(row => {
    const seg = row.Segment || 'Other';
    sums[seg] = (sums[seg] || 0) + (row.Monetary || 0);
    counts[seg] = (counts[seg] || 0) + 1;
  });

  const entries = Object.keys(sums).map(seg => ({
    seg, avg: sums[seg] / counts[seg]
  })).sort((a, b) => b.avg - a.avg);

  const labels = entries.map(e => e.seg);
  const data = entries.map(e => e.avg);
  const bgColors = labels.map(label => SEGMENT_COLORS[label] || SEGMENT_COLORS['Other']);

  const ctx = document.getElementById('monetaryBySegmentChart').getContext('2d');
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Avg Monetary ($)',
        data: data,
        backgroundColor: bgColors,
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } }
    }
  });
}

function createRevenueTrendChart() {
  // Aggregate by InvoiceDate (assuming YYYY-MM format for simplicity or extracting it)
  const monthlyRev = {};
  transactionsData.forEach(row => {
    if(row.InvoiceDate && row.TotalAmount) {
      // rough string check, adjust based on actual CSV format
      let dateStr = String(row.InvoiceDate).substring(0, 7); 
      monthlyRev[dateStr] = (monthlyRev[dateStr] || 0) + row.TotalAmount;
    }
  });
  
  const sortedMonths = Object.keys(monthlyRev).sort();
  const data = sortedMonths.map(m => monthlyRev[m]);

  const ctx = document.getElementById('revenueTrendChart').getContext('2d');
  const gradient = ctx.createLinearGradient(0, 0, 0, 400);
  gradient.addColorStop(0, 'rgba(0, 212, 170, 0.5)');
  gradient.addColorStop(1, 'rgba(0, 212, 170, 0.0)');

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: sortedMonths,
      datasets: [{
        label: 'Revenue',
        data: data,
        borderColor: '#00D4AA',
        backgroundColor: gradient,
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#12122a',
        pointBorderColor: '#00D4AA',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      interaction: { mode: 'index', intersect: false }
    }
  });
}

function createCountryRevenueChart() {
  const countryRev = {};
  transactionsData.forEach(row => {
    if(row.Country && row.TotalAmount) {
      countryRev[row.Country] = (countryRev[row.Country] || 0) + row.TotalAmount;
    }
  });

  const sortedCountries = Object.entries(countryRev).sort((a, b) => b[1] - a[1]).slice(0, 10);
  const labels = sortedCountries.map(c => c[0]);
  const data = sortedCountries.map(c => c[1]);

  const ctx = document.getElementById('countryRevenueChart').getContext('2d');
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Revenue',
        data: data,
        backgroundColor: '#45B7D1',
        borderRadius: 4
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } }
    }
  });
}

function initTable() {
  // Populate segments dropdown
  const filter = document.getElementById('segmentFilter');
  const uniqueSegments = [...new Set(rfmData.map(d => d.Segment || 'Other'))].sort();
  uniqueSegments.forEach(seg => {
    const opt = document.createElement('option');
    opt.value = seg;
    opt.textContent = seg;
    filter.appendChild(opt);
  });

  document.getElementById('searchInput').addEventListener('input', renderTable);
  filter.addEventListener('change', renderTable);

  document.querySelectorAll('th[data-sort]').forEach(th => {
    th.addEventListener('click', () => {
      const col = th.getAttribute('data-sort');
      if (tableSortColumn === col) {
        tableSortAsc = !tableSortAsc;
      } else {
        tableSortColumn = col;
        tableSortAsc = false;
      }
      renderTable();
    });
  });

  renderTable();
}

function renderTable() {
  const searchStr = document.getElementById('searchInput').value.toLowerCase();
  const segmentFilter = document.getElementById('segmentFilter').value;
  const tbody = document.getElementById('customerTableBody');

  let filtered = rfmData.filter(row => {
    const matchSearch = String(row.CustomerID || '').toLowerCase().includes(searchStr);
    const matchSegment = segmentFilter === 'All' || row.Segment === segmentFilter;
    return matchSearch && matchSegment;
  });

  filtered.sort((a, b) => {
    let valA = a[tableSortColumn];
    let valB = b[tableSortColumn];
    if (typeof valA === 'string') valA = valA.toLowerCase();
    if (typeof valB === 'string') valB = valB.toLowerCase();
    
    if (valA < valB) return tableSortAsc ? -1 : 1;
    if (valA > valB) return tableSortAsc ? 1 : -1;
    return 0;
  });

  const top100 = filtered.slice(0, 100);
  tbody.innerHTML = '';

  top100.forEach(row => {
    const tr = document.createElement('tr');
    
    const segColor = SEGMENT_COLORS[row.Segment || 'Other'] || '#888';
    
    tr.innerHTML = `
      <td>${row.CustomerID}</td>
      <td>${row.Recency}</td>
      <td>${row.Frequency}</td>
      <td>${formatCurrency(row.Monetary)}</td>
      <td>${row.R_Score || '-'}</td>
      <td>${row.F_Score || '-'}</td>
      <td>${row.M_Score || '-'}</td>
      <td><span class="badge" style="background-color: ${segColor}">${row.Segment || 'Other'}</span></td>
    `;
    tbody.appendChild(tr);
  });
}
