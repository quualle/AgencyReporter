# Agency Comparison Dashboard Implementation

## Implemented Features

### 1. Agency Ranking Lists
- Created reusable `AgencyRankingList` component for displaying top/bottom agencies by any metric
- Implemented color-coding for top/bottom performers
- Added ability to click on agencies to select them

### 2. Problematic Stays Comparison
- Top and bottom agencies by problematic stays percentage
- Top and bottom agencies by cancellation before arrival rate
- Top and bottom agencies by shortened stays after arrival rate
- Top agencies by total care stays volume

### 3. Integration with Existing Application
- Added new route in App.tsx
- Added sidebar navigation item
- Connected to existing app state management
- Leverages existing components (TimeFilter, AgencySelector)

## Implementation Details

### Data Sources
The implementation uses the existing `/api/problematic_stays/overview` endpoint without an agency_id parameter to fetch data for all agencies, which includes:
- Total care stays per agency
- Total problematic stays per agency
- Problematic percentage 
- Cancellations before arrival (count & percentage)
- Shortened stays after arrival (count & percentage)
- Instant departures (count & percentage)

### Component Structure
- Created a reusable `AgencyRankingList` component that can be configured for different metrics
- Created a new page component `AgencyComparisonPage` that displays multiple ranking lists
- Both components support all visual states (loading, empty, error)

### User Interaction
- The dashboard supports clicking on an agency in the rankings to select it
- This selection is propagated to the app store, making it available to other components
- Time period filtering is synced with the app store

## Limitations of Current Implementation

- The dashboard only shows metrics from the problematic stays dataset
- Average care stay duration metrics are not yet implemented (needs backend API support)
- Contract duration (over multiple care stays) is not yet implemented
- No visualizations other than ranking lists (could add charts in future iterations)

## Next Steps

### Short-term Enhancements
- Add visual indicators for previous ranking changes (↑, ↓, ⟳)
- Add ability to toggle between absolute and percentage values
- Enhance mobile view support

### Medium-term Additions
- Add charts comparing top/bottom agencies on key metrics
- Add heatmap visualization for problematic stays reasons across agencies
- Implement visualization for care stay duration across agencies

### Long-term Features (may require backend changes)
- Add contract duration analysis comparing agencies
- Add customer satisfaction comparison metrics
- Implement agency performance score based on weighted metrics
- Add monitoring features for tracking agency performance changes over time