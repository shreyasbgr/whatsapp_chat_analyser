import streamlit as st
import pandas as pd
from parser import parse_chat_file

st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")
st.title("📱 WhatsApp Chat Analyzer")

# Sidebar Upload
uploaded_file = st.sidebar.file_uploader("Upload WhatsApp Chat (.txt)", type=["txt"])

if uploaded_file:
    try:
        # Master dataframe with ALL messages (including group notifications)
        master_df = parse_chat_file(uploaded_file)
        st.sidebar.success("Chat successfully parsed!")
    except Exception as e:
        st.sidebar.error(f"Error parsing file: {str(e)}")
        st.error("Failed to parse the uploaded file. Please ensure it's a valid WhatsApp chat export.")
        st.stop()
    
    # Create a copy with only user messages (excluding group notifications)
    user_messages_df = master_df[master_df['sender'] != "group_notification"].copy()
    
    # Get all users (excluding group notifications)
    all_users = sorted(user_messages_df['sender'].unique())
    user_options = ["Overall"] + all_users
    
    # Single dropdown for user selection
    selected_user = st.sidebar.selectbox("Show Analysis wrt", user_options, index=0)
    
    # Filter data based on selected user
    if selected_user == "Overall":
        filtered_df = user_messages_df.copy()
        display_title = "Overall Chat"
    else:
        filtered_df = user_messages_df[user_messages_df['sender'] == selected_user].copy()
        display_title = f"{selected_user}'s Messages"
    
    # Display header and basic info
    st.header(f"📊 Analysis - {display_title}")
    
    # Show basic stats
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Messages", len(filtered_df))
    with col2:
        if selected_user == "Overall":
            st.metric("Total Users", len(all_users))
        else:
            st.metric("User", selected_user)
    with col3:
        media_count = len(filtered_df[filtered_df['media'] != ""])
        st.metric("Media Messages", media_count)
    with col4:
        st.metric("Master DataFrame", len(master_df))
    with col5:
        if len(filtered_df) > 0:
            date_range = f"{filtered_df['datetime_ist'].min()[:10]} to {filtered_df['datetime_ist'].max()[:10]}"
            st.metric("Date Range", date_range)
        else:
            st.metric("Date Range", "No data")
    
    # Show sample data
    st.subheader("📋 Sample Messages")
    if len(filtered_df) > 0:
        # Create a display dataframe with better formatting
        display_df = filtered_df[['datetime_ist_human', 'sender', 'message', 'media']].head(10).copy()
        
        # For media messages, show the media type instead of empty message
        display_df['display_content'] = display_df.apply(
            lambda row: f"[{row['media'].upper()}]" if row['media'] else row['message'], axis=1
        )
        
        # Show the dataframe with renamed columns
        st.dataframe(
            display_df[['datetime_ist_human', 'sender', 'display_content', 'media']].rename(columns={
                'datetime_ist_human': 'Time',
                'sender': 'Sender', 
                'display_content': 'Message/Media',
                'media': 'Media Type'
            }), 
            use_container_width=True
        )
    else:
        st.warning("No messages found for the selected user.")
    
    # Debug section (expandable)
    with st.expander("🔍 Debug Information"):
        st.write("**Master DataFrame Info:**")
        st.write(f"- Total rows: {len(master_df)}")
        st.write(f"- Group notifications: {len(master_df[master_df['sender'] == 'group_notification'])}")
        st.write(f"- User messages: {len(user_messages_df)}")
        st.write(f"- Media messages: {len(master_df[master_df['media'] != ''])}")
        st.write(f"- All senders: {list(master_df['sender'].unique())}")
        
        st.write("\n**Filtered DataFrame Info:**")
        st.write(f"- Filtered rows: {len(filtered_df)}")
        st.write(f"- Selected user: {selected_user}")
        st.write(f"- Media messages in filter: {len(filtered_df[filtered_df['media'] != ''])}")
        
        # Show media type breakdown
        if len(filtered_df[filtered_df['media'] != '']) > 0:
            st.write("\n**Media Type Breakdown:**")
            media_counts = filtered_df[filtered_df['media'] != '']['media'].value_counts()
            for media_type, count in media_counts.items():
                st.write(f"- {media_type}: {count}")
        
        st.write("\n**Sample from Master DataFrame:**")
        st.dataframe(master_df[['datetime_ist_human', 'sender', 'message', 'media', 'group_system_message']].head(5))
    
else:
    st.info("Please upload a WhatsApp chat `.txt` file to begin analysis.")
    
    # Instructions
    st.markdown("""
    ## How to export WhatsApp chat:
    
    1. Open WhatsApp on your phone
    2. Go to the chat you want to analyze
    3. Tap on the chat name at the top
    4. Scroll down and tap "Export Chat"
    5. Choose "Without Media" for faster processing
    6. Save the `.txt` file and upload it here
    
    **Note:** This analyzer works with WhatsApp chat exports in the format:
    `[DD/MM/YY, HH:MM:SS AM/PM] Contact Name: Message`
    """)
