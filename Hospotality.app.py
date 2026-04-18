import streamlit as st
import numpy as np
import pandas as pd
# Mock data generator (replaces real API)
class MockBookingAPI:
    def __init__(self):
        np.random.seed(42)  # Reproducible results
        
    def generate_properties(self, city: str, count: int = 50) -> List[Dict]:
        """Generate realistic mock hotel data"""
        base_price = self.get_city_base_price(city)
        properties = []
        
        for i in range(count):
            rating = np.clip(np.random.normal(8.2, 0.8), 1, 10)
            reviews = int(np.random.exponential(500) + 50)
            price_per_night = max(50, np.random.normal(base_price, base_price * 0.3))
            
            prop = {
                'hotel_id': 10000 + i,
                'hotel_name': f"{city} {'Luxury' if rating > 9 else 'Premium' if rating > 8 else 'Comfort'} Hotel #{i+1}",
                'city': city,
                'country': self.get_city_country(city),
                'price_total': round(price_per_night * 3, 2),
                'price_per_night': round(price_per_night, 2),
                'rating': round(rating, 1),
                'review_score': round(rating * 10, 1),
                'total_reviews': reviews,
                'room_type': np.random.choice(['Entire apartment', 'Private room', 'Hotel room']),
                'url': f"https://booking.com/hotel/{10000+i}",
                'stars': np.random.choice([3, 3.5, 4, 4.5, 5]),
                'distance_city_center': f"{np.random.uniform(0.1, 15):.1f} km",
                'amenities': np.random.choice(['Free WiFi', 'Pool', 'Gym', 'Parking', 'Breakfast'], 3).tolist()
            }
            properties.append(prop)
        
        return sorted(properties, key=lambda x: x['price_per_night'])
    
    def get_city_base_price(self, city: str) -> float:
        """Realistic base prices by city"""
        prices = {
            'New York': 280, 'Los Angeles': 240, 'Miami': 220, 'Austin': 180,
            'Chicago': 200, 'San Francisco': 320, 'Las Vegas': 190, 'Orlando': 170,
            'Seattle': 260, 'Boston': 270, 'Denver': 200, 'Phoenix': 160
        }
        return prices.get(city, 200)
    
    def get_city_country(self, city: str) -> str:
        countries = {'New York': 'USA', 'Los Angeles': 'USA', 'Miami': 'USA', 'Paris': 'France', 'London': 'UK'}
        return countries.get(city, 'USA')

class BookingRentalAggregator:
    def __init__(self):
        self.api = MockBookingAPI()
        self.cache = {}
    
    def search_properties(self, city: str, checkin: str = None, checkout: str = None, guests: int = 2, limit: int = 50) -> List[Dict]:
        """Search properties (mock API)"""
        cache_key = f"{city}_{limit}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        properties = self.api.generate_properties(city, limit)
        for prop in properties:
            prop.update({
                'search_city': city,
                'checkin': checkin or (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'checkout': checkin or (datetime.now() + timedelta(days=33)).strftime('%Y-%m-%d'),
                'guests': guests,
                'search_date': datetime.now().isoformat()
            })
        
        self.cache[cache_key] = properties
        return properties
    
    def aggregate_rentals(self, cities: List[str], filename: str = None) -> pd.DataFrame:
        """Aggregate across multiple cities"""
        all_properties = []
        for city in cities:
            st.info(f"🔍 Searching {city}...")
            properties = self.search_properties(city, limit=25)
            all_properties.extend(properties)
        
        df = pd.DataFrame(all_properties)
        if filename:
            df.to_csv(filename, index=False)
            st.success(f"💾 Saved {len(df)} properties to {filename}")
        
        return df

# Streamlit Dashboard
def main():
    st.set_page_config(page_title="Booking.com Rental Aggregator", layout="wide")
    st.title("🏠 Booking.com Rental Data Aggregator")
    st.markdown("**Fully functional prototype with realistic mock data** ✅")
    
    aggregator = BookingRentalAggregator()
    
    # Sidebar controls
    st.sidebar.header("Search Settings")
    city = st.sidebar.text_input("City", value="New York")
    limit = st.sidebar.slider("Results", 10, 100, 50)
    cities_list = st.sidebar.multiselect(
        "Multi-city aggregation", 
        ["New York", "Los Angeles", "Miami", "Austin", "Chicago", "San Francisco"],
        default=["New York", "Los Angeles"]
    )
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Single Search", "🌍 Multi-City", "📊 Analytics", "📈 Visualizations"])
    
    with tab1:
        if st.button("Search Rentals", key="single_search"):
            with st.spinner("Searching..."):
                properties = aggregator.search_properties(city, limit=limit)
                df = pd.DataFrame(properties)
                
                if not df.empty:
                    st.success(f"Found {len(df)} properties in {city}")
                    
                    # Price distribution
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Avg Price/Night", f"${df['price_per_night'].mean():.0f}")
                    with col2:
                        st.metric("Top Rating", f"{df['rating'].max():.1f}/10")
                    
                    # Properties table
                    st.dataframe(
                        df[['hotel_name', 'price_per_night', 'rating', 'total_reviews', 'room_type', 'url']]
                        .sort_values('price_per_night'),
                        use_container_width=True,
                        hide_index=True
                    )
    
    with tab2:
        if st.button("Aggregate Multiple Cities", key="multi_city"):
            with st.spinner("Aggregating data..."):
                df = aggregator.aggregate_rentals(cities_list)
                
                if not df.empty:
                    st.dataframe(df.head(20), use_container_width=True)
    
    with tab3:
        if st.button("Generate Analytics", key="analytics"):
            df = pd.concat([
                pd.DataFrame(aggregator.search_properties(city, limit=100))
                for city in cities_list[:3]
            ])
            
            if not df.empty:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Properties", len(df))
                with col2:
                    st.metric("Avg Price/Night", f"${df['price_per_night'].mean():.0f}")
                with col3:
                    st.metric("Avg Rating", f"{df['rating'].mean():.1f}")
                with col4:
                    st.metric("Best Value", f"${df.loc[df['rating'].idxmax(), 'price_per_night']:.0f}")
    
    with tab4:
        # Interactive charts
        df_sample = pd.concat([
            pd.DataFrame(aggregator.search_properties(c, limit=30)) 
            for c in cities_list[:4]
        ])
        
        if not df_sample.empty:
            # Price vs Rating scatter
            fig1 = px.scatter(
                df_sample, x='rating', y='price_per_night', 
                size='total_reviews', color='city',
                hover_data=['hotel_name', 'room_type'],
                title="🏨 Price vs Rating by City",
                labels={'price_per_night': 'Price per Night ($)', 'rating': 'Rating'}
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            # Price distribution histogram
            fig2 = px.histogram(
                df_sample, x='price_per_night', color='city',
                nbins=20, title="💰 Price Distribution",
                labels={'price_per_night': 'Price per Night ($)'}
            )
            st.plotly_chart(fig2, use_container_width=True)
            
            # City comparison
            city_stats = df_sample.groupby('city').agg({
                'price_per_night': ['mean', 'count'],
                'rating': 'mean'
            }).round(1)
            fig3 = px.bar(
                city_stats, x=city_stats.index, y=('price_per_night', 'mean'),
                title="📊 Average Price by City",
                labels={'value': 'Avg Price/Night ($)'}
            )
            st.plotly_chart(fig3, use_container_width=True)

if __name__ == "__main__":
    main()
