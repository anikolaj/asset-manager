// @ts-nocheck
import React, { useState, useMemo, useEffect } from 'react';
import './App.css';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Container,
  Card,
  CardContent,
  Grid,
  Chip,
  IconButton,
  Avatar,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AttachMoney,
  Inventory,
  Notifications,
  Settings,
  Savings,
} from '@mui/icons-material';
import { AgGridReact } from 'ag-grid-react';
import { AllCommunityModule, ModuleRegistry, themeQuartz } from 'ag-grid-community';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Legend,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

// Register AG Grid modules
ModuleRegistry.registerModules([AllCommunityModule]);

// Custom AG Grid theme
const gridTheme = themeQuartz.withParams({
  borderRadius: 8,
  headerBackgroundColor: 'FAFAFA_1',
  oddRowBackgroundColor: 'FFFFFF_1',
  rowHoverColor: 'F5F5F5_1',
  selectedRowBackgroundColor: 'E3F2FD_1',
  fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  fontSize: 14,
  cellHorizontalPadding: 16,
});

// Sample data for charts
const revenueData = [
    { month: 'Jan', revenue: 4000, orders: 240 },
    { month: 'Feb', revenue: 3000, orders: 198 },
    { month: 'Mar', revenue: 5000, orders: 300 },
    { month: 'Apr', revenue: 4500, orders: 278 },
    { month: 'May', revenue: 6000, orders: 389 },
    { month: 'Jun', revenue: 5500, orders: 349 },
    { month: 'Jul', revenue: 7000, orders: 430 },
    { month: 'Aug', revenue: 6500, orders: 401 },
    { month: 'Sep', revenue: 8000, orders: 502 },
    { month: 'Oct', revenue: 7500, orders: 475 },
    { month: 'Nov', revenue: 9000, orders: 560 },
    { month: 'Dec', revenue: 8500, orders: 520 },
  ];

// Stat Card Component
const StatCard = ({ title, value, change, changeType, icon: Icon, color }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography color="text.secondary" variant="body2" sx={{ mb: 1 }}>
            {title}
          </Typography>
          <Typography variant="h4" sx={{ mb: 1 }}>
            {value}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            {changeType === 'up' ? (
              <TrendingUp sx={{ fontSize: 18, color: 'success.main' }} />
            ) : (
              <TrendingDown sx={{ fontSize: 18, color: 'error.main' }} />
            )}
            <Typography
              variant="body2"
              sx={{ color: changeType === 'up' ? 'success.main' : 'error.main' }}
            >
              {change}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              vs last month
            </Typography>
          </Box>
        </Box>
        <Avatar sx={{ bgcolor: `${color}.light`, width: 48, height: 48 }}>
          <Icon sx={{ color: `${color}.main` }} />
        </Avatar>
      </Box>
    </CardContent>
  </Card>
);

// Status cell renderer for AG Grid
const StatusCellRenderer = (params: any) => {
  const statusColors = {
    Delivered: { bg: '#E8F5E9', color: '#2E7D32' },
    Shipped: { bg: '#E3F2FD', color: '#1565C0' },
    Processing: { bg: '#FFF3E0', color: '#EF6C00' },
    Pending: { bg: '#FCE4EC', color: '#C62828' },
  };
  const style = statusColors[params.value] || { bg: '#F5F5F5', color: '#757575' };

  return (
    <Chip
      label={params.value}
      size="small"
      sx={{
        backgroundColor: style.bg,
        color: style.color,
        fontWeight: 500,
        fontSize: '0.75rem',
      }}
    />
  );
};

function App() {
  const [portfolio, setPortfolio] = useState<object | null>(null);

  const portfolioName = 'test'; // TODO: replace with your portfolio name

  useEffect(() => {
    const fetchPortfolio = async () => {
      try {
        const response = await fetch(`http://localhost:5000/portfolio?name=${portfolioName}`);

        if (!response.ok) {
          throw new Error(`Portfolio fetch failed with status ${response.status}`);
        }

        const data = await response.json();
        console.log(data);

        if (data) {
          const equities = data.equities.map(equity => ({
            ...equity,
            notional: equity.shares * equity.price,
          }));

          const cashPosition = {
            ticker: 'USD $',
            price: 1,
            shares: data.cash,
            notional: data.cash,
            weight: data.value ? data.cash / data.value : 0,
            ytd: 0,
          };

          setPortfolio({
            ...data,
            equities,
            positions: [...equities, cashPosition],
          });
        }
      } catch (error) {
        console.error('Error fetching portfolio value:', error);
      }
    };

    fetchPortfolio();
  }, [portfolioName]);

  const formatCurrency = (value: number | null) =>
    value === null
      ? '$75,500'
      : new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD',
          maximumFractionDigits: 0,
        }).format(value);

  const formatPercentage = (value: number | null) =>
    value === null
      ? '0%'
      : new Intl.NumberFormat('en-US', {
          style: 'percent',
          maximumFractionDigits: 2,
        }).format(value);

  const assetSummaryColumnDefs = useMemo(() => [
    { field: 'ticker', headerName: 'Ticker', width: 120, filter: true },
    { field: 'price', headerName: 'Price', flex: 1, type: 'numericColumn', valueFormatter: params => `$${params.value.toLocaleString()}` },
    { field: 'shares', headerName: 'Shares', flex: 1, type: 'numericColumn', valueFormatter: params => params.value.toLocaleString() },
    { field: 'notional', headerName: 'Notional', flex: 1, type: 'numericColumn', sort: 'desc', valueFormatter: params => `$${params.value.toLocaleString()}` },
    { field: 'weight', headerName: 'Weight', flex: 1, type: 'numericColumn', valueFormatter: params => `${(params.value * 100).toFixed(2)}%` },
    { field: 'ytd', headerName: 'YTD', flex: 1, type: 'numericColumn', valueFormatter: params => `${params.value.toLocaleString()}%` },
  ], [portfolio]);

  const portfolioPieChartData = useMemo(() => {
    if (!portfolio?.positions || portfolio.positions.length === 0) {
      return [];
    }

    // Sort positions by weight (descending)
    const sortedPositions = [...portfolio.positions].sort((a, b) => b.weight - a.weight);
    
    // Take top 5 holdings
    const topHoldings = sortedPositions.slice(0, 5);
    
    // Calculate remaining weight for "Other"
    const remainingWeight = sortedPositions.slice(5).reduce((sum, position) => sum + position.weight, 0);
    
    // Build pie chart data
    const data = topHoldings.map(position => ({
      name: position.ticker,
      value: position.weight,
    }));
    
    // Add "Other" entry if there are more than 5 holdings
    if (sortedPositions.length > 5 && remainingWeight > 0) {
      data.push({
        name: 'Other',
        value: remainingWeight,
      });
    }
    
    return data;
  }, [portfolio]);

  const defaultColDef = useMemo(() => ({
    sortable: true,
    resizable: true,
  }), []);

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      {/* App Bar */}
      <AppBar position="static" elevation={0} sx={{ bgcolor: 'white', borderBottom: '1px solid E0E0E0_1' }}>
        <Toolbar>
          <Typography variant="h6" sx={{ color: 'primary.main', flexGrow: 1 }}>
            📊 AM Dashboard
          </Typography>
          <IconButton>
            <Notifications />
          </IconButton>
          <IconButton>
            <Settings />
          </IconButton>
          <Avatar sx={{ ml: 2, bgcolor: 'primary.main' }}>A</Avatar>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Stats Row */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              title="Total Value"
              value={formatCurrency(portfolio?.valuation?.currentValue)}
              change={formatPercentage(0)}
              changeType={0 > 0 ? 'up' : 'down'}
              icon={Savings}
              color="success"
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              title="Year to Date"
              value={formatPercentage(portfolio?.valuation?.ytd)}
              change={formatPercentage(portfolio?.valuation?.ytd)}
              changeType={portfolio?.valuation?.ytd > 0 ? 'up' : 'down'}
              icon={TrendingUp}
              color="secondary"
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              title="PnL (1D)"
              value={formatCurrency(portfolio?.valuation?.pnl)}
              change={formatCurrency(portfolio?.valuation?.pnl)}
              changeType={portfolio?.valuation?.pnl > 0 ? 'up' : 'down'}
              icon={AttachMoney}
              color="info"
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              title="Cash"
              value={formatCurrency(portfolio?.cash)}
              change={formatPercentage(0)}
              changeType={0 > 0 ? 'up' : 'down'}
              icon={Inventory}
              color="warning"
            />
          </Grid>
        </Grid>

        {/* Charts Row */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid size={{ xs: 12, lg: 8 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 3 }}>
                  Portfolio Overview
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={revenueData}>
                    <defs>
                      <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#1976D2" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#1976D2" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E0E0E0" />
                    <XAxis dataKey="month" stroke="#9E9E9E" fontSize={12} />
                    <YAxis stroke="#9E9E9E" fontSize={12} tickFormatter={(value) => `$${value / 1000}k`} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#fff',
                        border: '1px solid #E0E0E0',
                        borderRadius: 8,
                        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                      }}
                      formatter={(value) => [`$${value.toLocaleString()}`, 'Revenue']}
                    />
                    <Area
                      type="monotone"
                      dataKey="revenue"
                      stroke="#1976D2"
                      strokeWidth={2}
                      fillOpacity={1}
                      fill="url(#colorRevenue)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, lg: 4 }}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 3 }}>
                  Portfolio Breakdown
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={portfolioPieChartData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {portfolioPieChartData.map((entry, index) => {
                        const colors = ['#9C27B0', '#1976d2', '#2e7d32', '#ed6c02', '#d32f2f', '#7b1fa2', '#0288d1', '#388e3c', '#f57c00', '#c2185b'];
                        return <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />;
                      })}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#fff',
                        border: '1px solid #E0E0E0',
                        borderRadius: 8,
                        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                      }}
                      formatter={(value) => [`${(value * 100).toFixed(2)}%`, 'Weight']}
                    />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* AG Grid Table */}
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 3 }}>
              Positions
            </Typography>
            <Box sx={{ height: 400, width: '100%' }}>
              <AgGridReact
                rowData={portfolio?.positions}
                columnDefs={assetSummaryColumnDefs}
                defaultColDef={defaultColDef}
                pagination={true}
                paginationPageSize={5}
                paginationPageSizeSelector={[5, 10, 20]}
                animateRows={true}
                rowSelection="multiple"
                theme={gridTheme}
              />
            </Box>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
}

export default App;