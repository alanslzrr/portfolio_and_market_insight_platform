# Streamlit Frontend Implementation Plan

## Overview

This document outlines the complete implementation plan for a Streamlit-based frontend that integrates with the existing FastAPI backend. The implementation follows a minimalist, robust approach covering all backend features.

---

## Architecture Principles

### Design Philosophy
- **Minimalist UI**: Clean, distraction-free interface focused on data and actions
- **Robust Integration**: Comprehensive error handling and API communication
- **Session Management**: Persistent authentication state across pages
- **Responsive Layout**: Streamlit columns and containers for organized display
- **Real-time Updates**: Automatic refresh mechanisms for dynamic data

### Technical Stack
- Streamlit (UI framework)
- Requests (HTTP client for API calls)
- Plotly (interactive charts)
- Pandas (data manipulation)
- Python-dotenv (configuration)

---

## Project Structure

```
frontend/
├── app.py                          # Main entry point
├── requirements.txt                # Dependencies
├── .env                           # Configuration (API base URL)
├── config/
│   └── settings.py                # Centralized configuration
├── services/
│   ├── api_client.py              # Base API client with auth handling
│   ├── auth_service.py            # Authentication endpoints
│   ├── user_service.py            # User management endpoints
│   ├── portfolio_service.py       # Portfolio endpoints
│   ├── operation_service.py       # Operations endpoints
│   ├── market_service.py          # Market data endpoints
│   └── analysis_service.py        # AI analysis endpoints
├── pages/
│   ├── 1_📊_Portfolios.py         # Portfolio management
│   ├── 2_💰_Operations.py         # Buy/Sell operations
│   ├── 3_📈_Market.py             # Market data and search
│   ├── 4_🤖_AI_Analysis.py        # AI-powered analysis
│   └── 5_👤_Profile.py            # User profile
├── components/
│   ├── auth.py                    # Login/Register components
│   ├── portfolio_card.py          # Portfolio display card
│   ├── operation_form.py          # Operation input forms
│   ├── charts.py                  # Reusable chart components
│   └── metrics.py                 # Metric display components
└── utils/
    ├── formatters.py              # Data formatting utilities
    ├── validators.py              # Input validation
    └── session.py                 # Session state management
```

---

## Phase 1: Foundation Setup

### 1.1 Project Initialization

**Create base structure:**
- Initialize directory structure as outlined above
- Create requirements.txt with dependencies
- Set up .env file for configuration
- Create .gitignore for sensitive files

**Dependencies (requirements.txt):**
```
streamlit>=1.29.0
requests>=2.31.0
plotly>=5.18.0
pandas>=2.1.0
python-dotenv>=1.0.0
```

### 1.2 Configuration Management

**File: config/settings.py**

Implement centralized configuration:
- API base URL from environment variables
- Default timeout values
- Page configuration constants
- Chart theme settings

**Environment variables:**
- `API_BASE_URL` (e.g., http://localhost:8000)
- `API_TIMEOUT` (default: 30 seconds)

### 1.3 Base API Client

**File: services/api_client.py**

Create APIClient class with:

**Core Methods:**
- `__init__(base_url, timeout)`: Initialize client
- `_get_headers()`: Build request headers with auth token
- `get(endpoint, params)`: Generic GET request
- `post(endpoint, data)`: Generic POST request
- `put(endpoint, data)`: Generic PUT request
- `delete(endpoint)`: Generic DELETE request

**Authentication Handling:**
- Retrieve token from session state
- Attach Bearer token to all requests
- Handle 401 Unauthorized responses
- Automatic token refresh on expiration

**Error Handling:**
- Network errors (connection timeout, DNS failures)
- HTTP errors (4xx, 5xx status codes)
- JSON parsing errors
- Custom exception classes for specific error types

---

## Phase 2: Authentication System

### 2.1 Authentication Service

**File: services/auth_service.py**

Implement AuthService class with methods:

**Registration:**
- `register(email, full_name, password)`: POST /api/v1/auth/register
  - Validate input fields
  - Send registration request
  - Return user data or error

**Login:**
- `login(email, password)`: POST /api/v1/auth/login
  - Authenticate user
  - Store access_token and refresh_token in session
  - Return success status

**Token Management:**
- `refresh_token(refresh_token)`: POST /api/v1/auth/refresh
  - Request new access token
  - Update session with new tokens
  - Handle refresh token expiration

**Logout:**
- `logout(refresh_token)`: POST /api/v1/auth/logout
  - Invalidate refresh token
  - Clear session state
- `logout_all()`: POST /api/v1/auth/logout-all
  - Invalidate all user sessions

### 2.2 Authentication Components

**File: components/auth.py**

**Login Component:**
- Email input field (with validation)
- Password input field (masked)
- "Remember me" checkbox (optional)
- Login button with loading state
- Link to registration
- Error message display

**Register Component:**
- Email input with validation
- Full name input
- Password input with strength indicator
- Confirm password input
- Terms acceptance checkbox
- Register button with loading state
- Link to login
- Success/error message display

**Session Management:**
- Check if user is authenticated
- Redirect to login if not authenticated
- Display user info in sidebar
- Logout button in sidebar

### 2.3 Main App Entry Point

**File: app.py**

**Initialization:**
- Set page config (title, icon, layout)
- Initialize session state variables
- Load configuration

**Authentication Flow:**
- Check if user is logged in
- Display login/register if not authenticated
- Display main navigation if authenticated

**Sidebar Navigation:**
- User profile summary (name, email)
- Navigation links to pages
- Logout button

---

## Phase 3: User Management

### 3.1 User Service

**File: services/user_service.py**

Implement UserService class with methods:

**Profile Management:**
- `get_profile()`: GET /api/v1/users/me
  - Retrieve current user profile
  - Return user data with preferences

- `update_profile(full_name, currency, timezone, language, preferences)`: PUT /api/v1/users/me
  - Update user profile fields
  - Return updated profile

**Password Management:**
- `change_password(current_password, new_password)`: PUT /api/v1/users/me/password
  - Validate current password
  - Update to new password
  - Handle session invalidation

### 3.2 Profile Page

**File: pages/5_👤_Profile.py**

**Profile Display Section:**
- Display user ID (read-only)
- Display email (read-only)
- Display account creation date
- Display account status (active, verified)

**Profile Edit Section:**
- Full name input field
- Currency selector (USD, EUR, etc.)
- Timezone selector
- Language selector
- Preferences JSON editor (optional)
- Save button with confirmation

**Password Change Section:**
- Current password input
- New password input with validation
- Confirm new password input
- Change password button
- Security notice about session invalidation

**UI Elements:**
- Tab-based layout for sections
- Success/error notifications
- Loading states during API calls

---

## Phase 4: Portfolio Management

### 4.1 Portfolio Service

**File: services/portfolio_service.py**

Implement PortfolioService class with methods:

**Portfolio CRUD:**
- `list_portfolios()`: GET /api/v1/portfolios
  - Retrieve all user portfolios
  - Return list with basic metrics

- `get_portfolio(portfolio_id)`: GET /api/v1/portfolios/{portfolio_id}
  - Retrieve detailed portfolio with positions
  - Return portfolio data with asset breakdown

- `create_portfolio(name, description, base_currency)`: POST /api/v1/portfolios
  - Create new portfolio
  - Return created portfolio data

- `update_portfolio(portfolio_id, name, description)`: PUT /api/v1/portfolios/{portfolio_id}
  - Update portfolio information
  - Return updated portfolio

- `delete_portfolio(portfolio_id)`: DELETE /api/v1/portfolios/{portfolio_id}
  - Delete portfolio and all associated data
  - Handle confirmation

### 4.2 Portfolio Components

**File: components/portfolio_card.py**

**Portfolio Card Component:**
- Portfolio name and description
- Total value display (large, prominent)
- Total cost basis
- Gain/loss amount (color-coded: green/red)
- Gain/loss percentage
- Base currency indicator
- Last updated timestamp
- Action buttons (View Details, Edit, Delete)

**Portfolio Detail View:**
- Portfolio header with metrics
- Asset allocation pie chart
- Position table with columns:
  - Asset symbol
  - Quantity
  - Average price
  - Current price
  - Position value
  - Gain/loss (amount and %)
  - Allocation percentage
- Performance line chart (if historical data available)

### 4.3 Portfolios Page

**File: pages/1_📊_Portfolios.py**

**Page Layout:**

**Overview Section:**
- Total portfolio count
- Combined portfolio value
- Combined gain/loss
- Best/worst performing portfolio

**Portfolio List:**
- Grid layout of portfolio cards
- Sort options (by value, gain/loss, name)
- Filter options (by currency)

**Create Portfolio Section:**
- Expandable form
- Name input (required)
- Description textarea
- Base currency selector
- Create button

**Portfolio Detail Modal/Section:**
- Triggered by clicking portfolio card
- Full portfolio details
- Position management
- Edit portfolio button
- Delete portfolio button (with confirmation)

**Charts:**
- Portfolio allocation donut chart
- Performance over time line chart
- Gain/loss bar chart

---

## Phase 5: Operations Management

### 5.1 Operation Service

**File: services/operation_service.py**

Implement OperationService class with methods:

**Operation CRUD:**
- `list_operations(portfolio_id, asset_symbol, operation_type, date_from, date_to, skip, limit)`: GET /api/v1/operations
  - Retrieve filtered operations
  - Support pagination
  - Return list of operations

- `get_operation(operation_id)`: GET /api/v1/operations/{operation_id}
  - Retrieve single operation details
  - Return operation data

- `create_operation(portfolio_id, asset_symbol, operation_type, quantity, price, fees, operation_date, notes)`: POST /api/v1/operations
  - Create buy or sell operation
  - Handle validation
  - Return created operation

- `update_operation(operation_id, notes)`: PUT /api/v1/operations/{operation_id}
  - Update operation notes
  - Return updated operation

**Statistics:**
- `get_portfolio_stats(portfolio_id)`: GET /api/v1/operations/stats/{portfolio_id}
  - Retrieve aggregated statistics
  - Return metrics (total operations, invested, withdrawn, fees)

### 5.2 Operation Components

**File: components/operation_form.py**

**Buy/Sell Form Component:**

**Common Fields:**
- Portfolio selector (dropdown of user portfolios)
- Asset symbol input with autocomplete
- Operation type selector (BUY/SELL radio buttons)
- Quantity input (numeric, required)
- Price per unit input (numeric, required)
- Fees input (numeric, optional, default 0)
- Operation date picker (default today)
- Notes textarea (optional)

**Validation:**
- Quantity must be positive
- Price must be positive
- For SELL: validate sufficient quantity in portfolio
- Date cannot be future

**Submit Button:**
- Shows loading state
- Displays success/error messages
- Clears form on success

**Operation History Table:**
- Columns: Date, Type, Asset, Quantity, Price, Total, Fees, Notes
- Color coding (BUY: blue, SELL: orange)
- Sort by date (newest first)
- Pagination controls
- Filter options

### 5.3 Operations Page

**File: pages/2_💰_Operations.py**

**Page Layout:**

**Quick Stats Section:**
- Total operations count
- Total invested
- Total withdrawn
- Total fees paid
- Number of unique assets

**Add Operation Section:**
- Prominent "New Operation" button
- Expandable form (Buy/Sell tabs)
- Form component from operation_form.py
- Real-time validation feedback

**Operations History:**
- Filter panel:
  - Portfolio filter
  - Asset symbol filter
  - Operation type filter (All/BUY/SELL)
  - Date range selector
- Operations table
- Pagination (50 per page default)
- Export to CSV option

**Statistics Dashboard:**
- Operations by type (pie chart)
- Operations over time (line chart)
- Top traded assets (bar chart)
- Average fees per operation

---

## Phase 6: Market Data Integration

### 6.1 Market Service

**File: services/market_service.py**

Implement MarketService class with methods:

**Asset Search:**
- `search_assets(query, limit)`: GET /api/v1/market/assets/search
  - Search assets by symbol or name
  - Return matching assets
  - Handle no results scenario

- `get_asset_info(symbol)`: GET /api/v1/market/assets/{symbol}
  - Get detailed asset information
  - Return asset metadata

**Price Data:**
- `get_current_price(symbol)`: GET /api/v1/market/prices/{symbol}/current
  - Get real-time price
  - Return price with timestamp
  - Handle API unavailability

- `get_historical_prices(symbol, days)`: GET /api/v1/market/prices/{symbol}/historical
  - Get OHLCV historical data
  - Return price series
  - Support different time ranges

**Asset Creation:**
- `create_asset(symbol, name, asset_type, currency, exchange, description)`: POST /api/v1/market/assets
  - Create custom asset
  - Return created asset

### 6.2 Chart Components

**File: components/charts.py**

**Price Chart Component:**
- Line chart for historical prices
- Candlestick chart option (OHLCV)
- Volume bars overlay
- Moving averages (optional)
- Zoom and pan controls
- Date range selector

**Portfolio Performance Chart:**
- Line chart for portfolio value over time
- Multiple portfolios comparison
- Benchmark comparison (optional)
- Annotations for major operations

**Allocation Charts:**
- Pie chart for asset allocation
- Donut chart variant
- Bar chart for position values
- Interactive legends with filtering

### 6.3 Market Page

**File: pages/3_📈_Market.py**

**Page Layout:**

**Asset Search Section:**
- Search input with autocomplete
- Search button
- Recent searches history
- Popular assets list

**Search Results:**
- Asset cards with:
  - Symbol and name
  - Asset type
  - Current price (if available)
  - Exchange information
  - "View Details" button

**Asset Detail View:**
- Asset information panel
- Current price (large display)
- Price change indicators
- Historical price chart
- OHLCV data table
- "Add to Portfolio" quick action

**Market Overview:**
- Top movers (if data available)
- Recently added assets
- Asset categories

---

## Phase 7: AI Analysis Integration

### 7.1 Analysis Service

**File: services/analysis_service.py**

Implement AnalysisService class with methods:

**Analysis Generation:**
- `generate_asset_analysis(symbol, force_regenerate)`: POST /api/v1/analysis/asset/{symbol}
  - Request AI analysis for asset
  - Handle processing time
  - Return analysis with technical indicators

- `generate_portfolio_analysis(portfolio_id, force_regenerate)`: POST /api/v1/analysis/portfolio/{portfolio_id}
  - Request AI analysis for portfolio
  - Handle processing time
  - Return comprehensive analysis

**Analysis History:**
- `get_analysis_history(portfolio_id, asset_symbol, limit)`: GET /api/v1/analysis/history
  - Retrieve past analyses
  - Support filtering
  - Return analysis list

**Cache Management:**
- `invalidate_asset_cache(symbol)`: DELETE /api/v1/analysis/cache/asset/{symbol}
  - Force analysis regeneration
  - Clear cached results

- `invalidate_portfolio_cache(portfolio_id)`: DELETE /api/v1/analysis/cache/portfolio/{portfolio_id}
  - Force analysis regeneration
  - Clear cached results

### 7.2 AI Analysis Page

**File: pages/4_🤖_AI_Analysis.py**

**Page Layout:**

**Analysis Type Selector:**
- Tab layout: "Asset Analysis" / "Portfolio Analysis"

**Asset Analysis Tab:**
- Asset symbol input with autocomplete
- "Generate Analysis" button
- Force regenerate checkbox
- Loading indicator during processing
- Analysis display area:
  - Technical indicators summary
  - AI-generated text analysis
  - Trend indicators
  - Support/resistance levels
  - Volatility metrics
- Historical analyses list

**Portfolio Analysis Tab:**
- Portfolio selector dropdown
- "Generate Analysis" button
- Force regenerate checkbox
- Loading indicator during processing
- Analysis display area:
  - Diversification score
  - Risk assessment
  - Position analysis
  - AI-generated recommendations
  - Allocation suggestions
- Historical analyses list

**Analysis Display:**
- Clean, readable formatting
- Expandable sections
- Disclaimer notice (not financial advice)
- Export to PDF option
- Share/save functionality

**Analysis History:**
- List of past analyses
- Filter by date
- Filter by type (asset/portfolio)
- View previous analysis details
- Delete old analyses

---

## Phase 8: Utilities and Helpers

### 8.1 Data Formatters

**File: utils/formatters.py**

Implement formatting functions:

**Currency Formatting:**
- `format_currency(amount, currency)`: Format decimal to currency string
- `format_percentage(value)`: Format decimal to percentage
- `format_number(value, decimals)`: Generic number formatting

**Date/Time Formatting:**
- `format_date(date)`: Format date for display
- `format_datetime(datetime)`: Format datetime for display
- `format_relative_time(datetime)`: "2 hours ago" format

**Data Formatting:**
- `format_asset_type(type)`: Human-readable asset type
- `format_operation_type(type)`: Human-readable operation type
- `color_for_gain_loss(value)`: Return color based on positive/negative

### 8.2 Input Validators

**File: utils/validators.py**

Implement validation functions:

**Field Validation:**
- `validate_email(email)`: Email format validation
- `validate_password(password)`: Password strength validation
- `validate_positive_number(value)`: Numeric validation
- `validate_date(date)`: Date format and range validation

**Business Logic Validation:**
- `validate_sell_quantity(portfolio_id, symbol, quantity)`: Check available quantity
- `validate_portfolio_name(name)`: Name format and uniqueness
- `validate_operation_date(date)`: Date not in future

### 8.3 Session Management

**File: utils/session.py**

Implement session utilities:

**State Management:**
- `init_session_state()`: Initialize all session variables
- `is_authenticated()`: Check if user is logged in
- `get_current_user()`: Retrieve user data from session
- `clear_session()`: Clear all session data on logout

**Token Management:**
- `store_tokens(access_token, refresh_token)`: Save tokens
- `get_access_token()`: Retrieve access token
- `get_refresh_token()`: Retrieve refresh token
- `token_needs_refresh()`: Check token expiration

---

## Phase 9: UI/UX Polish

### 9.1 Layout Consistency

**Global Styling:**
- Define consistent color scheme
- Set typography standards
- Establish spacing rules
- Configure component defaults

**Page Structure:**
- Header with app name and navigation
- Sidebar with user info and navigation
- Main content area with consistent padding
- Footer with version and links (optional)

### 9.2 User Feedback

**Loading States:**
- Spinners for API calls
- Progress bars for long operations
- Skeleton screens for initial loads

**Success/Error Messages:**
- Toast notifications for actions
- Success messages (green)
- Error messages (red)
- Warning messages (yellow)
- Info messages (blue)

**Confirmations:**
- Delete confirmations (modal dialogs)
- Logout confirmation
- Data loss warnings

### 9.3 Responsive Design

**Mobile Considerations:**
- Streamlit's native responsive behavior
- Collapsible sections for mobile
- Touch-friendly button sizes
- Simplified charts for small screens

### 9.4 Accessibility

**Best Practices:**
- Semantic HTML structure
- Descriptive labels for inputs
- Alt text for images
- Keyboard navigation support
- Color contrast compliance

---

## Phase 10: Error Handling and Resilience

### 10.1 API Error Handling

**Network Errors:**
- Connection timeout handling
- DNS resolution errors
- Network unavailable scenarios
- Retry mechanisms with exponential backoff

**HTTP Errors:**
- 400 Bad Request: Display validation errors
- 401 Unauthorized: Redirect to login
- 403 Forbidden: Show permission error
- 404 Not Found: Show "resource not found"
- 409 Conflict: Show conflict details
- 500 Server Error: Show generic error, log details

### 10.2 Data Validation

**Client-Side Validation:**
- Validate before API calls
- Display inline error messages
- Prevent invalid submissions
- Real-time validation feedback

**Server Response Validation:**
- Validate API response structure
- Handle unexpected data formats
- Graceful degradation for missing data

### 10.3 Logging and Debugging

**Logging Strategy:**
- Log API calls and responses
- Log errors with stack traces
- Log user actions for debugging
- Configurable log levels

**Debug Mode:**
- Toggle for development
- Display API request/response details
- Show session state inspector
- Performance metrics

---

## Phase 11: Configuration and Deployment

### 11.1 Environment Configuration

**Configuration Files:**
- `.env` for local development
- `.env.production` for production
- Config validation on startup

**Required Variables:**
- `API_BASE_URL`
- `API_TIMEOUT`
- `DEBUG_MODE`
- `LOG_LEVEL`

### 11.2 Dependencies Management

**Requirements.txt:**
- Pin versions for stability
- Include all dependencies
- Add comments for clarity

**Virtual Environment:**
- Setup instructions
- Activation commands
- Dependency installation

### 11.3 Running the Application

**Development:**
```bash
streamlit run app.py
```

**Production:**
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

**Configuration Options:**
- Port configuration
- Host binding
- CORS settings (if needed)
- SSL/TLS (if needed)

---

## Phase 12: Testing Strategy

### 12.1 Manual Testing Checklist

**Authentication Flow:**
- [ ] Register new user
- [ ] Login with valid credentials
- [ ] Login with invalid credentials
- [ ] Token refresh on expiration
- [ ] Logout single session
- [ ] Logout all sessions

**Portfolio Management:**
- [ ] Create portfolio
- [ ] List portfolios
- [ ] View portfolio details
- [ ] Update portfolio
- [ ] Delete portfolio
- [ ] Verify metrics calculations

**Operations:**
- [ ] Create buy operation
- [ ] Create sell operation
- [ ] Validate sell quantity check
- [ ] View operations list
- [ ] Filter operations
- [ ] View operation details
- [ ] Update operation notes
- [ ] View statistics

**Market Data:**
- [ ] Search assets
- [ ] View asset details
- [ ] Get current price
- [ ] Get historical prices
- [ ] Create custom asset

**AI Analysis:**
- [ ] Generate asset analysis
- [ ] Generate portfolio analysis
- [ ] View analysis history
- [ ] Force regenerate analysis
- [ ] Invalidate cache

**User Profile:**
- [ ] View profile
- [ ] Update profile
- [ ] Change password
- [ ] Verify session invalidation

### 12.2 Error Scenario Testing

**Network Issues:**
- [ ] Backend offline
- [ ] Slow network response
- [ ] Timeout scenarios

**Authentication Issues:**
- [ ] Expired token
- [ ] Invalid token
- [ ] Missing token

**Data Issues:**
- [ ] Empty results
- [ ] Invalid data format
- [ ] Missing required fields

---

## Phase 13: Documentation

### 13.1 User Documentation

**Create README.md:**
- Application overview
- Features list
- Installation instructions
- Running the application
- Configuration guide
- Screenshots

### 13.2 Developer Documentation

**Code Documentation:**
- Docstrings for all functions
- Comments for complex logic
- Type hints for function signatures

**Architecture Documentation:**
- System overview diagram
- Data flow diagrams
- Component interaction

---

## Implementation Sequence

Follow this order for systematic implementation:

1. **Foundation** (Phase 1): Project setup, configuration, base API client
2. **Authentication** (Phase 2): Login, register, session management
3. **Core Navigation** (Phase 2.3): Main app structure, sidebar
4. **User Profile** (Phase 3): Profile page, basic user management
5. **Portfolios** (Phase 4): Portfolio CRUD, display components
6. **Operations** (Phase 5): Operation management, history
7. **Market Data** (Phase 6): Asset search, prices, charts
8. **AI Analysis** (Phase 7): Analysis generation and display
9. **Polish** (Phase 9): UI/UX improvements, styling
10. **Utilities** (Phase 8): Formatters, validators, helpers
11. **Error Handling** (Phase 10): Comprehensive error management
12. **Testing** (Phase 12): Manual testing of all features
13. **Documentation** (Phase 13): User and developer docs

---

## Key Implementation Notes

### Minimalist Design Principles

**Visual Hierarchy:**
- Important metrics prominently displayed
- Clear action buttons
- Minimal color palette
- Generous whitespace
- Consistent typography

**Information Density:**
- Show essential data first
- Progressive disclosure for details
- Collapsible sections for advanced features
- Smart defaults to reduce choices

**Interaction Patterns:**
- Predictable navigation
- Inline editing where possible
- Confirmation only for destructive actions
- Keyboard shortcuts for power users

### Robustness Checklist

**API Integration:**
- All endpoints from backend documented
- Error handling for each endpoint
- Retry logic for transient failures
- Graceful degradation when features unavailable

**State Management:**
- Session persistence across page changes
- Token refresh before expiration
- Cache management for performance
- Cleanup on logout

**Data Integrity:**
- Client-side validation
- Server response validation
- Optimistic UI updates with rollback
- Conflict resolution strategies

---

## Success Criteria

The implementation is complete when:

1. All backend endpoints are integrated and functional
2. User can complete full workflow: register → login → create portfolio → add operations → view analysis
3. Error handling covers all common failure scenarios
4. UI is clean, intuitive, and professional
5. Application is responsive and performant
6. All features work without crashes or data loss
7. Documentation is complete and accurate

---

## Next Steps

After completing this implementation:

1. Gather user feedback
2. Identify pain points and usability issues
3. Optimize performance bottlenecks
4. Add advanced features (notifications, exports, etc.)
5. Consider migration to React if scalability becomes an issue

---

*End of Implementation Plan*
