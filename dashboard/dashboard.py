import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set_theme(style='dark')


if __name__ == "__main__":
    main_data = pd.read_csv("dashboard/main_data.csv")
    main_data['dteday'] = pd.to_datetime(main_data['dteday'])

    
    # Membuat header
    st.write('''
             # Bike Corp. Dashboard :bike:
             #### Welcome to our dashboard!! :sunglasses:
        ''')
    
    # Komponen filter
    min_date = main_data["dteday"].min()
    max_date = main_data["dteday"].max()
    
    with st.sidebar:
        # Menampilkan ikon
        st.write('''
                 # Bike Corp. :bike:
            ''')

        # Mengambil start_date & end_date dari date_input
        start_date, end_date = st.date_input(
            label='Rentang Waktu',
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )
    
    type_user = 'cnt'
    # Membuat dataframe berdasarkan filter
    main_df = main_data[(main_data["dteday"] >= str(start_date)) & 
                (main_data["dteday"] <= str(end_date))]

    with st.subheader("Filter"):
        option = st.selectbox(
            label="Filter User",
            options=['all', 'casual', 'registered'],
            placeholder='Pilih jenis pengguna',
            format_func= lambda user: user 
            )
        type_user = 'cnt' if option == 'all' else option
    
    daily_user_df = main_df.groupby(by='dteday').agg({type_user : 'sum'})
    daily_user_df = daily_user_df.reset_index()

    seasonal_user_df = main_df.groupby(by='season').agg({type_user : 'sum'})
    seasonal_user_df.index = seasonal_user_df.index.to_series().map({1:'springer', 2:'summer', 3:'fall', 4:'winter'})


    

    # Membuat daily users
    st.subheader('Daily Users')
    total_users = daily_user_df[type_user].sum() #berdasarkan tipe pengguna
    st.metric("Total users", value=total_users)

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(
        daily_user_df["dteday"],
        daily_user_df[type_user],
        marker='o', 
        linewidth=2,
        color="#90CAF9"
    )
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15)
    
    st.pyplot(fig)



    # Membuat seasonal user
    st.subheader("Best & Worst Total User")
 
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
    
    colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    
    sns.barplot(x=type_user, y="season", data=seasonal_user_df.sort_values(by=type_user, ascending=False), palette=colors, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("Number of User", fontsize=30)
    ax[0].set_title("Best Total User", loc="center", fontsize=50)
    ax[0].tick_params(axis='y', labelsize=35)
    ax[0].tick_params(axis='x', labelsize=30)
    
    sns.barplot(x=type_user, y="season", data=seasonal_user_df.sort_values(by=type_user, ascending=True), palette=colors, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("Number of User", fontsize=30)
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].set_title("Worst Total User", loc="center", fontsize=50)
    ax[1].tick_params(axis='y', labelsize=35)
    ax[1].tick_params(axis='x', labelsize=30)
    
    st.pyplot(fig)




    # Membuat RFM parameters
    st.write('''
            ### Best Dates and Days Based on RFM Parameters
            #### Day/Date with more than 5000 user
        
            ''')

    # Recency
    recency_df = main_df[(main_df[type_user]>=5000)].sort_values(by='dteday', ascending=False)
    if (recency_df['dteday'].count()==0):
        recency_df[type_user]= [0]


    fm_df = main_df.groupby(by='dteday').agg({type_user:'sum'})
    fm_df['weekdays'] = fm_df.index.to_series().dt.day_name()

    # Frequency
    frequency_df = fm_df[fm_df[type_user]>=5000].groupby(by='weekdays').agg({'weekdays':'count'})
    frequency_df.columns = ['frequency']
    if (frequency_df['frequency'].count()==0):
        frequency_df['frequency']= [0]
    # Monetary
    monetary_df = fm_df.groupby(by='weekdays').agg({type_user:'sum'})
 
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric('Recently User', value=recency_df[type_user].head(1))
    with col2:
        st.metric('Avg. Frequency', value=f"{frequency_df['frequency'].mean():.2f}")
        
    with col3:
        st.metric('Avg. Total User', value=f"{monetary_df[type_user].mean():.0f}")
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 10))
    
    colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]
    
    sns.barplot(y=type_user, x="dteday", data=recency_df.head(5), palette=colors, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel(None)
    ax[0].set_title("Pengguna lebih dari 5000 dalam 3 tanggal terakhir", loc="center", fontsize=18)
    ax[0].tick_params(axis ='x', labelsize=15)
    
    sns.barplot(y="frequency", x="weekdays", data=frequency_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel(None)
    ax[1].set_title("Frekuensi seberapa sering hari tertentu\nmencapai lebih dari 5000 pengguna", loc="center", fontsize=18)
    ax[1].tick_params(axis='x', labelsize=15)
    
    sns.barplot(y=type_user, x="weekdays", data=monetary_df.sort_values(by=type_user, ascending=False).head(5), palette=colors, ax=ax[2])
    ax[2].set_ylabel(None)
    ax[2].set_xlabel(None)
    ax[2].set_title("Hari dengan total pengguna terbanyak", loc="center", fontsize=18)
    ax[2].tick_params(axis='x', labelsize=15)
    

    
    st.pyplot(fig)
    
    st.caption('Copyright (c) Bike Corp.')