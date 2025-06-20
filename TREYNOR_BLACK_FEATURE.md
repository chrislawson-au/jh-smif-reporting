# Treynor-Black Model Feature

## Overview

The SMIF Performance Dashboard now includes a **Treynor-Black Model Target Allocation** analysis feature. This enhancement provides optimal portfolio weights based on the Treynor-Black portfolio optimization framework.

## Key Features

### 1. **Monthly Data Analysis**

- Uses 5 years of monthly return data for more stable estimates
- Downloads data from Yahoo Finance for all portfolio holdings
- Compares each stock's performance against VTI (Vanguard Total Stock Market ETF)

### 2. **Statistical Calculations**

For each stock in the portfolio, the model calculates:

- **Alpha (α)**: Annualized excess return over the market (VTI)
- **Beta (β)**: Systematic risk relative to the market
- **MSE**: Mean Squared Error from regression (measure of idiosyncratic risk)
- **Alpha/MSE**: Information ratio used for determining optimal weights

### 3. **Target Weight Optimization**

- Weights are proportional to Alpha/MSE ratio
- Higher alpha with lower residual risk = higher allocation
- Weights are normalized to sum to 100%
- Only considers positive alpha stocks for long positions

### 4. **Visual Analytics**

#### Target Weights Table

Displays comprehensive analysis including:

- Annualized alpha for each stock
- Beta coefficients
- MSE values
- Alpha/MSE ratios
- Target weights vs current weights
- Weight differences to show rebalancing needs

#### Comparison Chart

Bar chart visualization showing:

- Current portfolio allocation
- Treynor-Black target allocation
- Side-by-side comparison for easy analysis

#### Covariance Matrix

- Annualized covariance matrix of returns
- Heatmap visualization
- Helps understand portfolio risk relationships

## How to Use

1. **Upload Data**: Upload your transaction and income Excel files as usual
2. **Navigate to Allocation Tab**: Click on the "🥧 Allocation" tab
3. **View Treynor-Black Analysis**: Scroll down to find the "🎯 Treynor-Black Model Target Allocation" section
4. **Interpret Results**:
   - Compare target weights with current weights
   - Identify stocks that should be over/underweighted
   - Use the analysis to inform rebalancing decisions

## Model Insights

The Treynor-Black model is particularly useful for:

- Identifying stocks with consistent outperformance (positive alpha)
- Optimizing the active portion of a portfolio
- Balancing expected returns with idiosyncratic risk
- Making data-driven allocation decisions

## Technical Details

- **Data Period**: 5 years of monthly returns
- **Benchmark**: VTI (Vanguard Total Stock Market ETF)
- **Minimum Data**: Requires at least 12 months of data per stock
- **Risk-Free Rate**: Implicitly included in alpha calculation

## Limitations

1. Historical data may not predict future performance
2. Model assumes returns are normally distributed
3. Transaction costs are not considered
4. Requires sufficient data history for all holdings

## Future Enhancements

Potential improvements could include:

- Adjustable lookback periods
- Alternative benchmarks
- Transaction cost optimization
- Constraints on position sizes
- Integration with risk management tools
