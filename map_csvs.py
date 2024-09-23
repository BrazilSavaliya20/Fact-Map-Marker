import streamlit as st
import pandas as pd
import requests
import time
import folium
from streamlit_folium import st_folium

# Function to geocode addresses using LocationIQ
def geocode_address(address):
    api_key = 'pk.8ca300eb1a91aabe0d494aa1cfb43419'  # Your LocationIQ API key
    url = f"https://us1.locationiq.com/v1/search.php?key={api_key}&q={address}&format=json"

    try:
        response = requests.get(url)
        data = response.json()
        if data:
            return (float(data[0]['lat']), float(data[0]['lon']))
        else:
            return (None, None)
    except Exception as e:
        return (None, None)

# Main Streamlit function
def main():
    st.title("CSV File Upload and Address Geocoding")

    # File uploader to upload CSV files
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    # Initialize session state
    if 'geocoded_data' not in st.session_state:
        st.session_state.geocoded_data = None

    if uploaded_file is not None:
        # Load the CSV into a DataFrame
        df = pd.read_csv(uploaded_file)

        # Check if 'address' column exists in the uploaded CSV
        if 'address' not in df.columns:
            st.error("The CSV file does not contain an 'address' column.")
            return

        # Initialize lists for latitude and longitude
        latitudes = []
        longitudes = []

        # Geocode each address only if not already geocoded
        if st.session_state.geocoded_data is None:
            for address in df['address']:
                lat, lon = geocode_address(address)
                latitudes.append(lat)
                longitudes.append(lon)
                time.sleep(1)  # Delay before next request

            # Store all latitude and longitude in the DataFrame
            df['latitude'] = latitudes
            df['longitude'] = longitudes

            # Create a new DataFrame with valid latitude and longitude
            valid_df = df.dropna(subset=['latitude', 'longitude'])
            st.session_state.geocoded_data = valid_df  # Store in session state

            # Show the DataFrame with latitudes and longitudes
            st.write("Geocoded Data:")
            st.dataframe(valid_df[['address', 'latitude', 'longitude']])
        else:
            valid_df = st.session_state.geocoded_data

        # Create a folium map with all valid coordinates
        if not valid_df.empty:
            # Focus on the first valid address
            first_address_location = valid_df.iloc[0][['latitude', 'longitude']]
            m = folium.Map(location=[first_address_location['latitude'], first_address_location['longitude']], zoom_start=12)

            # Add markers to the map for valid addresses
            for index, row in valid_df.iterrows():
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    icon=folium.Icon(color='blue', icon='info-sign'),  # Customize marker symbol
                    popup=f"Address: {row['address']}<br>Latitude: {row['latitude']}<br>Longitude: {row['longitude']}"
                ).add_to(m)

            # Display the map in Streamlit
            st.write("Fact Map Marker")
            st_folium(m, width=700, height=500, use_container_width=True)
        else:
            st.warning("No valid coordinates to display on the map.")

        # Save the updated DataFrame with latitudes and longitudes to your local folder
        output_path = 'C:/Users/admin/Downloads/store_data/geocoded_data.csv'
        try:
            df.to_csv(output_path, index=False)
            st.success(f"File saved to {output_path}")
        except Exception as e:
            st.error(f"Error saving file: {e}")

if __name__ == "__main__":
    main()
