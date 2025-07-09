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
    
    # Calculate word count
    total_words = 0
    for message in filtered_df['message']:
        if message and message.strip():
            total_words += len(message.split())
    
    # Show basic stats - Large metrics display
    st.subheader("📊 Key Statistics")
    
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    
    with col1:
        st.metric("Total Messages", len(filtered_df))
    with col2:
        st.metric("Total Words", total_words)
    with col3:
        media_count = len(filtered_df[filtered_df['media'] != ""])
        st.metric("Total Media Shared", media_count)
    with col4:
        url_count = len(filtered_df[filtered_df['urls'] != ""])
        st.metric("Total Links", url_count)
    with col5:
        # Count both phone numbers in messages and contact media types
        phone_count = len(filtered_df[filtered_df['phone_numbers'] != ""])
        contact_media_count = len(filtered_df[filtered_df['media'] == "contact"])
        total_contacts = phone_count + contact_media_count
        st.metric("Total Contacts Shared", total_contacts)
    with col6:
        emoji_count = len(filtered_df[filtered_df['emojis'] != ""])
        st.metric("Total Emojis Shared", emoji_count)
    with col7:
        mention_count = len(filtered_df[filtered_df['mentions'] != ""])
        st.metric("Total Mentions", mention_count)
    
    # Additional information row
    st.subheader("📋 Additional Information")
    col8, col9, col10 = st.columns([1, 1, 1.5])  # Give more space to the date range column
    
    with col8:
        if selected_user == "Overall":
            st.metric("Total Users", len(all_users))
        else:
            st.metric("Selected User", selected_user)
    with col9:
        st.metric("Total Records", len(master_df))
    with col10:
        if len(filtered_df) > 0:
            date_range = f"{filtered_df['datetime_ist'].min()[:10]} to {filtered_df['datetime_ist'].max()[:10]}"
            st.markdown("**Date Range**")
            st.text(date_range)
        else:
            st.markdown("**Date Range**")
            st.text("No data")
    
    # Word frequency analysis
    st.subheader("📊 Word Frequency Analysis")
    if len(filtered_df) > 0:
        # Load stop words
        try:
            with open('./stop_words_hinglish.txt', 'r', encoding='utf-8') as f:
                stop_words = set(word.strip().lower() for word in f.readlines() if word.strip())
        except FileNotFoundError:
            stop_words = set()
            st.warning("Stop words file not found. Word filtering may be less effective.")
        
        # Collect all words from messages with better filtering
        all_words = []
        for message in filtered_df['message']:
            if message and message.strip():
                # Split message into words and clean them
                words = message.lower().split()
                for word in words:
                    # Remove punctuation and special characters, keep only alphanumeric
                    clean_word = ''.join(char for char in word if char.isalnum())
                    # Filter: non-empty, length > 1, not in stop words, not pure numbers
                    if (clean_word and 
                        len(clean_word) > 1 and 
                        clean_word not in stop_words and
                        not clean_word.isdigit()):
                        all_words.append(clean_word)
        
        if all_words:
            from collections import Counter
            import plotly.express as px
            from wordcloud import WordCloud
            import matplotlib.pyplot as plt
            import io
            
            # Count word frequencies
            word_counts = Counter(all_words)
            top_words_chart = word_counts.most_common(10)  # For chart display
            all_words_sorted = word_counts.most_common()   # For scrollable list
            
            # Calculate percentages for chart (top 10)
            total_words_count = len(all_words)
            chart_data = []
            for word, count in top_words_chart:
                percentage = (count / total_words_count) * 100
                chart_data.append({
                    'word': word,
                    'count': count,
                    'percentage': percentage
                })
            
            # Calculate percentages for all words (scrollable list)
            all_words_data = []
            for word, count in all_words_sorted:
                percentage = (count / total_words_count) * 100
                all_words_data.append({
                    'word': word,
                    'count': count,
                    'percentage': percentage
                })
            
            # Create tabs for different visualizations
            tab1, tab2, tab3 = st.tabs(["📊 Bar Chart", "☁️ Word Cloud", "📋 Word List"])
            
            with tab1:
                # Create bar chart (top 10 only)
                words_df = pd.DataFrame(chart_data)
                fig = px.bar(
                    words_df,
                    x='count',
                    y='word',
                    orientation='h',
                    title='Top 10 Most Frequent Words',
                    labels={'count': 'Frequency', 'word': 'Word'},
                    height=500
                )
                fig.update_layout(
                    yaxis={'categoryorder': 'total ascending'},
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                # Create word cloud
                st.markdown("**Word Cloud Visualization**")
                
                # Generate word cloud
                wordcloud = WordCloud(
                    width=800, 
                    height=400, 
                    background_color='white',
                    colormap='viridis',
                    max_words=100,
                    stopwords=stop_words  # Pass stop words to WordCloud as well
                ).generate_from_frequencies(word_counts)
                
                # Create matplotlib figure
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                
                # Display the word cloud
                st.pyplot(fig)
                
                # Add some info about the word cloud
                st.info(f"""Word cloud generated from {len(all_words_data)} unique words 
                        (after filtering {len(stop_words)} stop words)""")
            
            with tab3:
                st.markdown("**All Words ({} total)**".format(len(all_words_data)))
                
                # Create scrollable list with all words
                scrollable_items = []
                for i, data in enumerate(all_words_data, 1):
                    scrollable_items.append(
                        f"<div style='margin-bottom: 8px; padding: 5px; background-color: #ffffff; border-radius: 3px; border-left: 3px solid #1f77b4;'>" +
                        f"<span style='color: #333333; font-weight: bold;'>{i}. {data['word']}</span>" +
                        f"<span style='color: #666666; margin-left: 10px;'>{data['percentage']:.2f}% ({data['count']})</span>" +
                        f"</div>"
                    )
                
                scrollable_content = "".join(scrollable_items)
                
                # Display in a container with scroll and better styling
                st.markdown(
                    f"""<div style='height: 500px; overflow-y: auto; padding: 10px; border: 1px solid #ddd; 
                    border-radius: 5px; background-color: #f8f9fa;'>
                    {scrollable_content}
                    </div>""",
                    unsafe_allow_html=True
                )
        else:
            st.info("No words found after filtering stop words and short words.")
    else:
        st.info("No messages available for word frequency analysis.")
    
    # Emoji analysis
    st.subheader("😊 Emoji Analysis")
    if len(filtered_df) > 0:
        # Extract all emojis from the filtered dataframe
        all_emojis = []
        emoji_messages = filtered_df[filtered_df['emojis'] != '']
        
        if len(emoji_messages) > 0:
            for emoji_str in emoji_messages['emojis']:
                if emoji_str and emoji_str != '':
                    try:
                        # Parse the emoji list string
                        import ast
                        emoji_list = ast.literal_eval(emoji_str)
                        if isinstance(emoji_list, list):
                            all_emojis.extend(emoji_list)
                        else:
                            # Handle case where it's just a string
                            all_emojis.append(str(emoji_list))
                    except (ValueError, SyntaxError):
                        # If parsing fails, treat as single emoji
                        all_emojis.append(emoji_str)
        
        if all_emojis:
            from collections import Counter
            import plotly.express as px
            import plotly.graph_objects as go
            
            # Count emoji frequencies
            emoji_counts = Counter(all_emojis)
            top_emojis_chart = emoji_counts.most_common(10)  # For charts
            all_emojis_sorted = emoji_counts.most_common()   # For scrollable list
            
            # Calculate percentages for top 10 emojis
            total_emoji_count = len(all_emojis)
            chart_data = []
            for emoji, count in top_emojis_chart:
                percentage = (count / total_emoji_count) * 100
                chart_data.append({
                    'emoji': emoji,
                    'count': count,
                    'percentage': percentage
                })
            
            # Calculate percentages for all emojis
            all_emoji_data = []
            for emoji, count in all_emojis_sorted:
                percentage = (count / total_emoji_count) * 100
                all_emoji_data.append({
                    'emoji': emoji,
                    'count': count,
                    'percentage': percentage
                })
            
            # Create tabs for different emoji visualizations
            emoji_tab1, emoji_tab2, emoji_tab3 = st.tabs(["📊 Bar Chart", "🥧 Pie Chart", "📋 Emoji List"])
            
            with emoji_tab1:
                # Create bar chart for top 10 emojis
                emojis_df = pd.DataFrame(chart_data)
                fig = px.bar(
                    emojis_df,
                    x='count',
                    y='emoji',
                    orientation='h',
                    title='Top 10 Most Used Emojis',
                    labels={'count': 'Frequency', 'emoji': 'Emoji'},
                    height=500
                )
                fig.update_layout(
                    yaxis={'categoryorder': 'total ascending'},
                    showlegend=False,
                    font=dict(size=16)  # Larger font for better emoji visibility
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with emoji_tab2:
                # Create pie chart for top 10 emojis
                emojis_df = pd.DataFrame(chart_data)
                fig = go.Figure(data=[go.Pie(
                    labels=emojis_df['emoji'],
                    values=emojis_df['count'],
                    textinfo='label+percent',
                    textfont_size=20,
                    hole=0.3,  # Donut chart style
                    textposition='outside',
                    automargin=True
                )])
                fig.update_layout(
                    title='Top 10 Most Used Emojis Distribution',
                    height=600,
                    font=dict(size=16),
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.01
                    ),
                    margin=dict(l=20, r=120, t=50, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Add emoji usage statistics
                st.info(f"""📊 **Emoji Usage Statistics:**
                - Total emojis used: {total_emoji_count:,}
                - Unique emojis: {len(all_emoji_data)}
                - Messages with emojis: {len(emoji_messages)} ({len(emoji_messages)/len(filtered_df)*100:.1f}% of all messages)
                - Average emojis per message: {total_emoji_count/len(emoji_messages):.1f}
                """)
            
            with emoji_tab3:
                st.markdown("**All Emojis ({} unique emojis)**".format(len(all_emoji_data)))
                
                # Create scrollable list with all emojis
                emoji_scrollable_items = []
                for i, data in enumerate(all_emoji_data, 1):
                    emoji_scrollable_items.append(
                        f"<div style='margin-bottom: 8px; padding: 8px; background-color: #ffffff; border-radius: 3px; border-left: 3px solid #ff6b6b; display: flex; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>" +
                        f"<div style='font-size: 24px; margin-right: 10px; background: linear-gradient(45deg, #f0f0f0, #e0e0e0); padding: 4px 8px; border-radius: 4px; text-shadow: 1px 1px 2px rgba(0,0,0,0.3); border: 1px solid #d0d0d0;'>{data['emoji']}</div>" +
                        f"<div>" +
                        f"<span style='color: #333333; font-weight: bold;'>#{i}</span>" +
                        f"<span style='color: #666666; margin-left: 10px;'>{data['percentage']:.2f}% ({data['count']} times)</span>" +
                        f"</div>" +
                        f"</div>"
                    )
                
                emoji_scrollable_content = "".join(emoji_scrollable_items)
                
                # Display emoji list in a scrollable container
                st.markdown(
                    f"""<div style='height: 500px; overflow-y: auto; padding: 10px; border: 1px solid #ddd; 
                    border-radius: 5px; background-color: #fff5f5;'>
                    {emoji_scrollable_content}
                    </div>""",
                    unsafe_allow_html=True
                )
        else:
            st.info("No emojis found in the selected messages.")
    else:
        st.info("No messages available for emoji analysis.")
    
    # Show sample data
    st.subheader("📋 Sample Messages")
    if len(filtered_df) > 0:
        # Create a display dataframe with better formatting
        display_df = filtered_df[['datetime_ist_human', 'sender', 'raw_message', 'message', 'media', 'media_file_name', 'urls', 'phone_numbers', 'mentions', 'emojis']].head(10).copy()
        
        # Show the dataframe with renamed columns - Message contains only user-typed content
        st.dataframe(
            display_df[['datetime_ist_human', 'sender', 'raw_message', 'message', 'media', 'media_file_name', 'urls', 'phone_numbers', 'mentions', 'emojis']].rename(columns={
                'datetime_ist_human': 'Time',
                'sender': 'Sender',
                'raw_message': 'Raw Message',
                'message': 'Clean Message',
                'media': 'Media Type',
                'media_file_name': 'Media File Name',
                'urls': 'URLs',
                'phone_numbers': 'Contacts',
                'mentions': 'Mentions',
                'emojis': 'Emojis'
            }), 
            use_container_width=True,
            column_config={
                'Time': st.column_config.TextColumn(width="medium"),
                'Sender': st.column_config.TextColumn(width="small"),
                'Raw Message': st.column_config.TextColumn(width="large"),
                'Clean Message': st.column_config.TextColumn(width="large"),
                'Media Type': st.column_config.TextColumn(width="small"),
                'Media File Name': st.column_config.TextColumn(width="medium"),
                'URLs': st.column_config.TextColumn(width="medium"),
                'Contacts': st.column_config.TextColumn(width="medium"),
                'Mentions': st.column_config.TextColumn(width="medium"),
                'Emojis': st.column_config.TextColumn(width="medium")
            }
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
            
            # Show caption statistics
            media_messages = filtered_df[filtered_df['media'] != '']
            media_with_captions = len(media_messages[media_messages['message'] != ''])
            media_without_captions = len(media_messages[media_messages['message'] == ''])
            
            st.write("\n**Caption Statistics:**")
            st.write(f"- Media with captions: {media_with_captions}")
            st.write(f"- Media without captions: {media_without_captions}")
        
        # Show URL statistics
        if len(filtered_df[filtered_df['urls'] != '']) > 0:
            st.write("\n**URL Statistics:**")
            url_messages = filtered_df[filtered_df['urls'] != '']
            st.write(f"- Messages with URLs: {len(url_messages)}")
            st.write(f"- Messages with URLs and text: {len(url_messages[url_messages['message'] != ''])}")
            st.write(f"- Messages with only URLs: {len(url_messages[url_messages['message'] == ''])}")
        
        # Show phone number statistics
        if len(filtered_df[filtered_df['phone_numbers'] != '']) > 0:
            st.write("\n**Phone Number Statistics:**")
            phone_messages = filtered_df[filtered_df['phone_numbers'] != '']
            st.write(f"- Messages with phone numbers: {len(phone_messages)}")
            st.write(f"- Messages with phones and text: {len(phone_messages[phone_messages['message'] != ''])}")
            st.write(f"- Messages with only phone numbers: {len(phone_messages[phone_messages['message'] == ''])}")
        
        # Show emoji statistics
        if len(filtered_df[filtered_df['emojis'] != '']) > 0:
            st.write("\n**Emoji Statistics:**")
            emoji_messages = filtered_df[filtered_df['emojis'] != '']
            st.write(f"- Messages with emojis: {len(emoji_messages)}")
            st.write(f"- Messages with emojis and text: {len(emoji_messages[emoji_messages['message'] != ''])}")
            st.write(f"- Messages with only emojis: {len(emoji_messages[emoji_messages['message'] == ''])}")
            
            # Show most common emojis
            all_emojis = []
            for emoji_str in emoji_messages['emojis']:
                if emoji_str:
                    all_emojis.extend(emoji_str.split(' '))
            
            if all_emojis:
                from collections import Counter
                emoji_counts = Counter(all_emojis)
                st.write("\n**Most Common Emojis:**")
                for emoji, count in emoji_counts.most_common(10):
                    st.write(f"- {emoji}: {count}")
        
        st.write("\n**Sample from Master DataFrame:**")
        st.dataframe(master_df[['datetime_ist_human', 'sender', 'raw_message', 'message', 'media', 'urls', 'phone_numbers', 'mentions', 'emojis', 'group_system_message']].head(5))
    
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
