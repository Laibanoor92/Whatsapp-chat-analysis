
import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # fetch unique users
    user_list = df['user'].unique().tolist()

    # Check if 'group_notification' exists in the list before attempting to remove it
    if 'group_notification' in user_list:
        user_list.remove('group_notification')

    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):

        # Stats Area
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # monthly timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        if not timeline.empty:
            fig, ax = plt.subplots()
            ax.plot(timeline['time'], timeline['message'], color='green')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        else:
            st.write("Not enough data to generate monthly timeline.")

        # daily timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        if not daily_timeline.empty:
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        else:
            st.write("Not enough data to generate daily timeline.")

        # activity map
        st.title('Activity Map')
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_user, df)
            if not busy_day.empty:
                fig, ax = plt.subplots()
                ax.bar(busy_day.index, busy_day.values, color='purple')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            else:
                st.write("Not enough data to determine busy days.")

        with col2:
            st.header("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            if not busy_month.empty:
                fig, ax = plt.subplots()
                ax.bar(busy_month.index, busy_month.values, color='orange')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            else:
                st.write("Not enough data to determine busy months.")

        # Weekly Activity Map with error handling
        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        
        # Check if heatmap data is valid before plotting
        if user_heatmap.size > 0 and not user_heatmap.isna().all().all():
            fig, ax = plt.subplots()
            ax = sns.heatmap(user_heatmap)
            st.pyplot(fig)
        else:
            st.write("Not enough data to generate the weekly activity heatmap.")

        # finding the busiest users in the group(Group level)
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x = helper.most_busy_users(df)
            if not x[0].empty:
                fig, ax = plt.subplots()
                col1, col2 = st.columns(2)
                with col1:
                    ax.bar(x[0].index, x[0].values, color='red')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)
                with col2:
                    st.dataframe(x[1])
            else:
                st.write("Not enough data to determine busy users.")

        # WordCloud
        st.title("Wordcloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # most common words
        st.title('Most common words')
        most_common_df = helper.most_common_words(selected_user, df)

        # Check if DataFrame is not empty and has both columns
        if not most_common_df.empty and len(most_common_df.columns) >= 2:
            fig, ax = plt.subplots()
            ax.barh(most_common_df[0], most_common_df[1])
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        else:
            st.write("Not enough data to show common words.")

        # emoji analysis
        st.title("Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)
        
        # Check if emoji dataframe has data
        if not emoji_df.empty and len(emoji_df.columns) >= 2:
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(emoji_df)
            with col2:
                fig, ax = plt.subplots()
                if len(emoji_df) > 0:  # Check if there are any rows
                    ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f")
                    st.pyplot(fig)
                else:
                    st.write("No emojis found in the selected messages.")
        else:
            st.write("No emojis found in the selected messages.")