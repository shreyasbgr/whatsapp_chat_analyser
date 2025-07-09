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
                        emoji_list = ast.literal_eval(emoji_str)  # type: ignore
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
    
    # Timeline analysis
    st.subheader("📈 Timeline Analysis")
    if len(filtered_df) > 0:
        import plotly.express as px
        import plotly.graph_objects as go
        from datetime import datetime
        import calendar
        
        # Convert datetime strings to datetime objects for analysis
        filtered_df_copy = filtered_df.copy()
        filtered_df_copy['datetime_obj'] = pd.to_datetime(filtered_df_copy['datetime_ist'])  # type: ignore
        
        # Extract date components
        filtered_df_copy['year'] = filtered_df_copy['datetime_obj'].dt.year  # type: ignore
        filtered_df_copy['month'] = filtered_df_copy['datetime_obj'].dt.month  # type: ignore
        filtered_df_copy['day'] = filtered_df_copy['datetime_obj'].dt.day  # type: ignore
        filtered_df_copy['weekday'] = filtered_df_copy['datetime_obj'].dt.day_name()  # type: ignore
        filtered_df_copy['hour'] = filtered_df_copy['datetime_obj'].dt.hour  # type: ignore
        filtered_df_copy['year_month'] = filtered_df_copy['datetime_obj'].dt.to_period('M')  # type: ignore
        filtered_df_copy['date'] = filtered_df_copy['datetime_obj'].dt.date  # type: ignore
        
        # Create tabs for different timeline analyses
        time_tab1, time_tab2, time_tab3, time_tab4, time_tab5 = st.tabs(["📅 Monthly Timeline", "📆 Daily Timeline", "📇 Month Analysis", "📃 Weekday Analysis", "🔥 Activity Heatmap"])
        
        with time_tab1:
            st.markdown("**Monthly Message Timeline**")
            
            # Monthly timeline - messages per month
            monthly_counts = filtered_df_copy.groupby('year_month').size().reset_index(name='message_count')
            monthly_counts['year_month_str'] = monthly_counts['year_month'].astype(str)
            
            fig_monthly = px.line(
                monthly_counts,
                x='year_month_str',
                y='message_count',
                title='Messages per Month Over Time',
                labels={'year_month_str': 'Month', 'message_count': 'Number of Messages'},
                markers=True,
                height=500
            )
            fig_monthly.update_layout(
                xaxis_title="Month",
                yaxis_title="Number of Messages",
                hovermode='x unified'
            )
            fig_monthly.update_xaxes(tickangle=45)
            st.plotly_chart(fig_monthly, use_container_width=True)
            
            # Monthly statistics
            if len(monthly_counts) > 0:
                max_month = monthly_counts.loc[monthly_counts['message_count'].idxmax()]
                min_month = monthly_counts.loc[monthly_counts['message_count'].idxmin()]
                avg_monthly = monthly_counts['message_count'].mean()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Most Active Month", str(max_month['year_month_str']))  # type: ignore
                    st.write(f"📊 {int(max_month['message_count'])} messages")  # type: ignore
                with col2:
                    st.metric("Least Active Month", str(min_month['year_month_str']))  # type: ignore
                    st.write(f"📊 {int(min_month['message_count'])} messages")  # type: ignore
                with col3:
                    st.metric("Average Monthly", f"{avg_monthly:.0f} messages")
        
        with time_tab2:
            st.markdown("**Daily Message Timeline**")
            
            # Daily timeline - messages per day
            daily_counts = filtered_df_copy.groupby('date').size().reset_index(name='message_count')
            daily_counts['date_str'] = daily_counts['date'].astype(str)
            
            fig_daily = px.line(
                daily_counts,
                x='date_str',
                y='message_count',
                title='Messages per Day Over Time',
                labels={'date_str': 'Date', 'message_count': 'Number of Messages'},
                height=500
            )
            fig_daily.update_layout(
                xaxis_title="Date",
                yaxis_title="Number of Messages",
                hovermode='x unified'
            )
            fig_daily.update_xaxes(tickangle=45)
            st.plotly_chart(fig_daily, use_container_width=True)
            
            # Daily statistics
            if len(daily_counts) > 0:
                max_day = daily_counts.loc[daily_counts['message_count'].idxmax()]
                min_day = daily_counts.loc[daily_counts['message_count'].idxmin()]
                avg_daily = daily_counts['message_count'].mean()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Most Active Day", str(max_day['date_str']))
                    st.write(f"📊 {int(max_day['message_count'])} messages")
                with col2:
                    st.metric("Least Active Day", str(min_day['date_str']))
                    st.write(f"📊 {int(min_day['message_count'])} messages")
                with col3:
                    st.metric("Average Daily", f"{avg_daily:.0f} messages")
        
        with time_tab3:
            st.markdown("**Month-based Analysis**")
            
            # Month analysis - aggregate by month name across all years
            month_counts = filtered_df_copy.groupby('month').size().reset_index(name='message_count')
            month_counts['month_name'] = month_counts['month'].apply(lambda x: calendar.month_name[x])
            
            # Bar chart for month analysis
            fig_month = px.bar(
                month_counts,
                x='month_name',
                y='message_count',
                title='Messages by Month (All Years Combined)',
                labels={'month_name': 'Month', 'message_count': 'Number of Messages'},
                height=500,
                color='message_count',
                color_continuous_scale='viridis'
            )
            fig_month.update_layout(
                xaxis_title="Month",
                yaxis_title="Number of Messages",
                showlegend=False
            )
            st.plotly_chart(fig_month, use_container_width=True)
            
            # Month statistics
            if len(month_counts) > 0:
                max_month = month_counts.loc[month_counts['message_count'].idxmax()]
                min_month = month_counts.loc[month_counts['message_count'].idxmin()]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Most Active Month", str(max_month['month_name']))
                    st.write(f"📊 {int(max_month['message_count'])} messages")
                with col2:
                    st.metric("Least Active Month", str(min_month['month_name']))
                    st.write(f"📊 {int(min_month['message_count'])} messages")
        
        with time_tab4:
            st.markdown("**Weekday Analysis**")
            
            # Weekday analysis
            weekday_counts = filtered_df_copy.groupby('weekday').size().reset_index(name='message_count')
            
            # Order weekdays properly
            weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekday_counts['weekday'] = pd.Categorical(weekday_counts['weekday'], categories=weekday_order, ordered=True)
            weekday_counts = weekday_counts.sort_values('weekday')
            
            # Bar chart for weekday analysis
            fig_weekday = px.bar(
                weekday_counts,
                x='weekday',
                y='message_count',
                title='Messages by Day of Week',
                labels={'weekday': 'Day of Week', 'message_count': 'Number of Messages'},
                height=500,
                color='message_count',
                color_continuous_scale='plasma'
            )
            fig_weekday.update_layout(
                xaxis_title="Day of Week",
                yaxis_title="Number of Messages",
                showlegend=False
            )
            st.plotly_chart(fig_weekday, use_container_width=True)
            
            # Weekday statistics
            if len(weekday_counts) > 0:
                max_weekday = weekday_counts.loc[weekday_counts['message_count'].idxmax()]
                min_weekday = weekday_counts.loc[weekday_counts['message_count'].idxmin()]
                total_weekdays = weekday_counts['message_count'].sum()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Most Active Day", str(max_weekday['weekday']))  # type: ignore
                    st.write(f"📊 {int(max_weekday['message_count'])} messages")  # type: ignore
                with col2:
                    st.metric("Least Active Day", str(min_weekday['weekday']))  # type: ignore
                    st.write(f"📊 {int(min_weekday['message_count'])} messages")  # type: ignore
                with col3:
                    avg_weekday = total_weekdays / 7
                    st.metric("Average per Weekday", f"{avg_weekday:.0f} messages")
                
                # Additional weekday insights
                st.markdown("**Weekday Insights:**")
                weekend_messages = weekday_counts[weekday_counts['weekday'].isin(['Saturday', 'Sunday'])]['message_count'].sum()
                weekday_messages = weekday_counts[~weekday_counts['weekday'].isin(['Saturday', 'Sunday'])]['message_count'].sum()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**Weekend Activity:** {weekend_messages} messages ({weekend_messages/total_weekdays*100:.1f}%)")
                with col2:
                    st.info(f"**Weekday Activity:** {weekday_messages} messages ({weekday_messages/total_weekdays*100:.1f}%)")
        
        with time_tab5:
            st.markdown("**Activity Heatmap - Weekday vs Hour**")
            
            # Create heatmap data: weekday vs hour
            heatmap_data = filtered_df_copy.groupby(['weekday', 'hour']).size().reset_index(name='message_count')
            
            # Create a complete grid of all weekdays and hours
            weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            hours = list(range(24))
            
            # Create a pivot table for the heatmap
            heatmap_pivot = heatmap_data.pivot(index='weekday', columns='hour', values='message_count')
            
            # Reindex to ensure all weekdays and hours are present
            heatmap_pivot = heatmap_pivot.reindex(weekday_order, fill_value=0)
            heatmap_pivot = heatmap_pivot.reindex(columns=hours, fill_value=0)
            
            # Create heatmap using plotly
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=heatmap_pivot.values,
                x=[f"{h:02d}:00" for h in hours],
                y=weekday_order,
                colorscale='YlOrRd',
                showscale=True,
                hoverongaps=False,
                hovertemplate='<b>%{y}</b><br>Hour: %{x}<br>Messages: %{z}<extra></extra>'
            ))
            
            fig_heatmap.update_layout(
                title='Message Activity Heatmap: Weekday vs Hour',
                xaxis_title='Hour of Day',
                yaxis_title='Day of Week',
                height=500,
                font=dict(size=12)
            )
            
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
            # Heatmap insights
            if len(heatmap_data) > 0:
                # Find peak activity hour and day
                peak_activity = heatmap_data.loc[heatmap_data['message_count'].idxmax()]
                total_messages = heatmap_data['message_count'].sum()
                
                # Find most active hour overall
                hourly_activity = heatmap_data.groupby('hour')['message_count'].sum().reset_index()
                most_active_hour = hourly_activity.loc[hourly_activity['message_count'].idxmax()]
                
                # Find most active day overall (should match weekday analysis)
                daily_activity = heatmap_data.groupby('weekday')['message_count'].sum().reset_index()
                most_active_day = daily_activity.loc[daily_activity['message_count'].idxmax()]
                
                # Extract scalar values to avoid type issues
                peak_weekday = str(peak_activity['weekday'])
                peak_hour = int(peak_activity['hour'])
                peak_count = int(peak_activity['message_count'])
                
                active_hour = int(most_active_hour['hour'])
                active_hour_count = int(most_active_hour['message_count'])
                
                active_day = str(most_active_day['weekday'])
                active_day_count = int(most_active_day['message_count'])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "Peak Activity Period", 
                        f"{peak_weekday} at {peak_hour:02d}:00"
                    )
                    st.write(f"📊 {peak_count} messages")
                with col2:
                    st.metric(
                        "Most Active Hour", 
                        f"{active_hour:02d}:00"
                    )
                    st.write(f"📊 {active_hour_count} messages")
                with col3:
                    st.metric(
                        "Most Active Day", 
                        active_day
                    )
                    st.write(f"📊 {active_day_count} messages")
                
                # Additional insights
                st.markdown("**Activity Insights:**")
                
                # Morning, afternoon, evening, night breakdown
                morning_hours = list(range(6, 12))
                afternoon_hours = list(range(12, 18))
                evening_hours = list(range(18, 22))
                night_hours = list(range(22, 24)) + list(range(0, 6))
                
                morning_msgs = heatmap_data[heatmap_data['hour'].isin(morning_hours)]['message_count'].sum()
                afternoon_msgs = heatmap_data[heatmap_data['hour'].isin(afternoon_hours)]['message_count'].sum()
                evening_msgs = heatmap_data[heatmap_data['hour'].isin(evening_hours)]['message_count'].sum()
                night_msgs = heatmap_data[heatmap_data['hour'].isin(night_hours)]['message_count'].sum()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"""**Time of Day Breakdown:**
                    - Morning (06:00-12:00): {morning_msgs} messages ({morning_msgs/total_messages*100:.1f}%)
                    - Afternoon (12:00-18:00): {afternoon_msgs} messages ({afternoon_msgs/total_messages*100:.1f}%)
                    """)
                with col2:
                    st.info(f"""**Evening & Night:**
                    - Evening (18:00-22:00): {evening_msgs} messages ({evening_msgs/total_messages*100:.1f}%)
                    - Night (22:00-06:00): {night_msgs} messages ({night_msgs/total_messages*100:.1f}%)
                    """)
    else:
        st.info("No messages available for timeline analysis.")
    
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
