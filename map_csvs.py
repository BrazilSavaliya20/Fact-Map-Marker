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
    st.title("Fact Map Marker")

    # Path to your sample geo.csv file
    sample_file_path = 'C:/Users/admin/Downloads/map/geo.csv'

    # Read the sample CSV file
    with open(sample_file_path, 'rb') as f:
        sample_csv = f.read()

    # Button to download the sample CSV file
    st.download_button(
        label="Download sample CSV",
        data=sample_csv,
        file_name="geo.csv",
        mime='text/csv',
    )

    # File uploader to upload CSV files
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    # Initialize session state
    if 'geocoded_data' not in st.session_state:
        st.session_state.geocoded_data = None
    if 'selected_addresses' not in st.session_state:
        st.session_state.selected_addresses = []

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

        # Sidebar for address checkboxes
        st.sidebar.title("Address Selection")

        # "Select All" checkbox
        select_all = st.sidebar.checkbox("Select All")

        # List of selected addresses
        selected_addresses = []
        for address in valid_df['address']:
            if select_all:
                # If "Select All" is checked, all individual checkboxes are pre-selected
                selected = st.sidebar.checkbox(f"Select {address}", value=True, key=address)
            else:
                # Otherwise, the individual checkboxes can be selected manually
                selected = st.sidebar.checkbox(f"Select {address}", key=address)
            
            if selected:
                selected_addresses.append(address)

        # Update session state
        st.session_state.selected_addresses = selected_addresses

        # Create a folium map with selected addresses
        if selected_addresses:
            # Focus on the first selected address
            first_selected_address = selected_addresses[0]
            selected_row = valid_df[valid_df['address'] == first_selected_address].iloc[0]
            center_lat, center_lon = selected_row['latitude'], selected_row['longitude']

            m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

            # Add markers for selected addresses
            for index, row in valid_df.iterrows():
                if row['address'] in selected_addresses:
                    folium.Marker(
                        location=[row['latitude'], row['longitude']],
                        icon=folium.Icon(color='blue', icon='info-sign'),  # Customize marker symbol
                        popup=f"Address: {row['address']}<br>Latitude: {row['latitude']}<br>Longitude: {row['longitude']}"
                    ).add_to(m)

            # Display the map in Streamlit
            st.write("Map with Selected Addresses")
            st_folium(m, width=700, height=500, use_container_width=True)
        else:
            st.warning("No addresses selected to display on the map.")

        # Save the updated DataFrame with latitudes and longitudes to your local folder
        output_path = 'C:/Users/admin/Downloads/store_data/geocoded_data.csv'
        try:
            df.to_csv(output_path, index=False)
            st.success(f"File saved to {output_path}")
        except Exception as e:
            st.error(f"Error saving file: {e}")

if __name__ == "__main__":
    main()
