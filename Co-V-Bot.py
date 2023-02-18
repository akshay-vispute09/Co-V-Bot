import telebot
import pandas as pd
import os
import numpy as np
import requests
path=os.getcwd()
while True:
    API_KEY=''  #API KEY REMOVED FOR SECURITY PURPOSE
    bot=telebot.TeleBot(API_KEY)
    recent_date=''
    df=pd.DataFrame()
    current_df=pd.DataFrame()
    new_df=pd.DataFrame()
    final_new_df=pd.DataFrame()
    try:
        statelist=['Alabama','Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'District of Columbia', 'Florida', 'Georgia','Guam', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska','Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Northern Mariana Islands', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Puerto Rico', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virgin Islands', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']
        countylist=[]

        current_counties=[]
        state_ip=''
        county_ip=''

        @bot.message_handler(commands=['Greet'])
        def greet(message):
            bot.reply_to(message,'Hey! Hows it going?')

        @bot.message_handler(commands=['hello'])
        def hello(message):
            bot.send_message(message.chat.id,'Hello!! Please type your State')
            
        @bot.message_handler(commands=['faq'])
        def faq(message):
            bot.send_message(message.chat.id,'How it works\n\nHii, We have calculated the transmission Risk for every county based on factors like Cases,Death,Vacination rate & Mobility. The Transmission risk is categorised into RED,AMBER & GREEN. Where Red signifies the most Dangerous and green signifies least.\n We have categorised the cases into the above said categories based on transmission categories categorised in CDC website along with other statistical inferences from the data.\nhttps://covid.cdc.gov/covid-data-tracker/#county-view\nSource:https://data.cdc.gov/Vaccinations/COVID-19-Vaccinations-in-the-United-States-County/8xkx-amqh')

        @bot.message_handler(func=lambda msg:(msg.text is not None and msg.text in statelist))
        def state(message):
            print("Entering State.....")
            global state_ip
            global current_counties
            global current_df
            global new_df
            global recent_date
            global statelist
            global countylist
            state_ip=message.text
            #------------------------------Getting Data ---------------------------------------------------
            url="https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv"
            df=pd.read_csv(url)
            new_df=df[df['state']==state_ip]
            recent_date=df['date'].max()
            current_df=df[df['date']==recent_date]
            statelist=current_df['state'].unique().tolist()
            countylist=current_df['county'].unique().tolist() #doesnt work out just for checing typo
            #-----------------------CREATION OF FILE---------------------------------------------------------
            print("RUNNING BEFORE CHECK FILE.....")
            
            def checkfile(filename):
                return os.path.isfile(filename)
#             #---------------------CREATES 7 DAY CSV FOR SLA CALC-------------------------
            def createTodayFile():
                import os
                directory = os.getcwd()
                files_in_directory = os.listdir(directory)
                filtered_files = [file for file in files_in_directory if file.endswith('.csv')]
                for file in filtered_files:
                    path_to_file = os.path.join(directory, file)
                    os.remove(path_to_file)

                from datetime import date
                import pandas as pd
                today = date.today()
                print(today)
                vacination_filename='vacination_'+str(today)+'.csv'
                df_filename='FINALDF_'+str(today)+'.csv'
                

                # RWAL TIME CASE ----------------------------------------------------------------------------------------------
                print("GETTING CASE DATA...")
                
                url = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/rolling-averages/us-counties-recent.csv"
                aveg = pd.read_csv(url)
             
                aveg['date'] = pd.to_datetime(aveg['date'])

                lastest_date=aveg['date'].max()
               
                from datetime import date
                today = date.today()
                from datetime import datetime, timedelta  
                # check_date = lastest_date- timedelta(days=8)

                # FIX NUMBER OF DAYS----------------------------------------------------------------------------------------------
                check_date = today - timedelta(days=14)
                print(check_date)
                print(type(check_date))

                aveg['date'] = pd.to_datetime(aveg['date'])
                mask = aveg["date"] >= str(check_date)
                new_df=aveg[mask]

                del new_df['geoid']


                new_df.drop(new_df.index[(new_df['county'] == 'Unknown')],axis=0,inplace=True)

                new_df['date']=new_df['date'].apply(lambda x: x.date())

                # Vaccination--------------------------------------------------------------------------------------------------

                print("GETTING VACINNATION DATA...")
                import requests

                lastday=lastest_date.date()

                daterange=pd.date_range(check_date,lastday-timedelta(days=1),freq='d')
                daterange=[i.date() for i in daterange]


                csv_file = open(vacination_filename, 'wb') #Eg =>vacination_2021-09-28.csv
                for i in daterange:
                    url=r"https://data.cdc.gov/resource/8xkx-amqh.csv?$where=date='"+str(i)+"'"
                    req = requests.get(url)
                    url_content = req.content
                    csv_file.write(url_content)
                csv_file.close()
                
                vac_df=pd.read_csv(vacination_filename) #Saving Vaccination----------------------------------------------------
                print("WROTE CSV...")
                indexes=[]
                for index,row in vac_df.iterrows():
                    if row['date']=='date':
                        indexes.append(index)


                vac_df = vac_df.drop(labels=indexes, axis=0)
                print("REMOVED UNWANTED DATES...")

                vac_df.drop(vac_df.index[(vac_df['recip_county'] == 'Unknown')],axis=0,inplace=True)

                replace_dict = {'AL' : 'Alabama','AK' : 'Alaska','AZ' : 'Arizona','AR' : 'Arkansas','CA' : 'California','CO' : 'Colorado','CT' : 'Connecticut','DE' : 'Delaware','FL' : 'Florida','GA' : 'Georgia','HI' : 'Hawaii','ID' : 'Idaho','IL' : 'Illinois','IN' : 'Indiana','IA' : 'Iowa','KS' : 'Kansas','KY' : 'Kentucky','LA' : 'Louisiana','ME' : 'Maine','MD' : 'Maryland','MA' : 'Massachusetts','MI' : 'Michigan','MN' : 'Minnesota','MS' : 'Mississippi','MO' : 'Missouri','MT' : 'Montana','NE' : 'Nebraska','NV' : 'Nevada','NH' : 'New Hampshire','NJ' : 'New Jersey','NM' : 'New Mexico','NY' : 'New York','NC' : 'North Carolina','ND' : 'North Dakota','OH' : 'Ohio','OK' : 'Oklahoma','OR' : 'Oregon','PA' : 'Pennsylvania','RI' : 'Rhode Island','SC' : 'South Carolina','SD' : 'South Dakota','TN' : 'Tennessee','TX' : 'Texas','UT' : 'Utah','VT' : 'Vermont','VA' : 'Virginia','WA' : 'Washington','WV' : 'West Virginia','WI' : 'Wisconsin','WY' : 'Wyoming'}
                vac_df.recip_state.replace(replace_dict,inplace=True)


                vac_df['recip_county']=vac_df['recip_county'].apply(lambda x:x.replace(' County','').strip(''))

                # vac_df['date']=vac_df['date'].apply(lambda x:x.split('T')[0].strip())

                vac_df['date']=pd.to_datetime(vac_df['date'])

#                 from dateutil import parser
                vac_df['date']=vac_df['date'].apply(lambda x: x.date())

                vac_df.rename(columns={'recip_state': 'state'}, inplace=True)
                vac_df.rename(columns={'recip_county': 'county'}, inplace=True)



                # Mobility--------------------------------------------------------------------------------------------------
                print("GETTING MOBILITY DATA.....")
                # https://stackoverflow.com/questions/5710867/downloading-and-unzipping-a-zip-file-without-writing-to-disk

                from io import BytesIO
                from zipfile import ZipFile
                from urllib.request import urlopen
                import pandas as pd
                from io import BytesIO
                from zipfile import ZipFile
                import pandas
                import requests

                url=r'https://www.gstatic.com/covid19/mobility/Region_Mobility_Report_CSVs.zip'
                content = requests.get(url)
                zf = ZipFile(BytesIO(content.content))

                # find the first matching csv file in the zip:
                match = [s for s in zf.namelist() if "2021_US_Region_Mobility_Report.csv" in s][0]
                # match=['2021_US_Region_Mobility_Report.csv']
                # the first line of the file contains a string - that line shall de     ignored, hence skiprows
                mobility_df = pandas.read_csv(zf.open(match), low_memory=False, skiprows=[1] )

                mobility_df.head()

                mobility_df['date']=pd.to_datetime(mobility_df['date'])

                mask = mobility_df["date"] >= str(check_date)
                new_mobility_df=mobility_df[mask]

                final_mobility_df=new_mobility_df[['sub_region_1','sub_region_2','date','retail_and_recreation_percent_change_from_baseline','grocery_and_pharmacy_percent_change_from_baseline','parks_percent_change_from_baseline','transit_stations_percent_change_from_baseline','workplaces_percent_change_from_baseline','residential_percent_change_from_baseline']]

                final_mobility_df.head()

                final_mobility_df.columns

                final_mobility_df.rename(columns={'sub_region_1': 'state'}, inplace=True)
                final_mobility_df.rename(columns={'sub_region_2': 'county'}, inplace=True)

                final_mobility_df['county'].unique()

                final_mobility_df['county']=final_mobility_df['county'].apply(lambda x:str(x).replace(' County','').strip(''))

                final_mobility_df.head(1)

                # Integration-----------------------------------------------------------------------------------------------------
                print("INTEGRATING DATA.....")
                new_df['state_county_date'] = new_df['state'].astype(str) + "_" + new_df['county'].astype(str) + "_" +  new_df['date'].astype(str)

                vac_df['state_county_date'] = vac_df['state'].astype(str) + "_" + vac_df['county'].astype(str) + "_" +  vac_df['date'].astype(str)

                final_mobility_df['state_county_date'] = final_mobility_df['state'].astype(str) + "_" + final_mobility_df['county'].astype(str) + "_" +  final_mobility_df['date'].astype(str)

                final = pd.merge(new_df, vac_df, on='state_county_date', how='inner')

                final_df=pd.merge(final, final_mobility_df, on='state_county_date', how='inner')


                # final.head()

                final_df.drop(['date_x','date_y','county_x','county_y','state_x','state_y','metro_status'], axis = 1, inplace = True)


                final_new_df=final_df[[ 'date','state', 'county','cases', 'cases_avg', 'cases_avg_per_100k', 'deaths', 'deaths_avg',
                       'deaths_avg_per_100k', 'state_county_date', 'fips', 'mmwr_week',
                       'series_complete_pop_pct', 'series_complete_yes',
                       'series_complete_12plus', 'series_complete_12pluspop',
                       'series_complete_18plus', 'series_complete_18pluspop',
                       'series_complete_65plus', 'series_complete_65pluspop',
                       'completeness_pct', 'administered_dose1_recip',
                       'administered_dose1_pop_pct', 'administered_dose1_recip_12plus',
                       'administered_dose1_recip_12pluspop_pct',
                       'administered_dose1_recip_18plus',
                       'administered_dose1_recip_18pluspop_pct',
                       'administered_dose1_recip_65plus',
                       'administered_dose1_recip_65pluspop_pct', 'svi_ctgy',
                       'series_complete_pop_pct_svi', 'series_complete_12pluspop_pct_svi',
                       'series_complete_18pluspop_pct_svi',
                       'series_complete_65pluspop_pct_svi',
                       'series_complete_pop_pct_ur_equity',
                       'series_complete_12pluspop_pct_ur_equity',
                       'series_complete_18pluspop_pct_ur_equity',
                       'series_complete_65pluspop_pct_ur_equity',
                       'retail_and_recreation_percent_change_from_baseline',
                       'grocery_and_pharmacy_percent_change_from_baseline',
                       'parks_percent_change_from_baseline',
                       'transit_stations_percent_change_from_baseline',
                       'workplaces_percent_change_from_baseline',
                       'residential_percent_change_from_baseline']]


                removecols=['mmwr_week','series_complete_12plus', 'series_complete_12pluspop','series_complete_18plus', 'series_complete_18pluspop','series_complete_65plus', 'series_complete_65pluspop','administered_dose1_recip','administered_dose1_pop_pct', 'administered_dose1_recip_12plus','administered_dose1_recip_12pluspop_pct','administered_dose1_recip_18plus','administered_dose1_recip_18pluspop_pct','administered_dose1_recip_65plus','administered_dose1_recip_65pluspop_pct','series_complete_12pluspop_pct_svi','series_complete_18pluspop_pct_svi','series_complete_65pluspop_pct_svi','series_complete_pop_pct_ur_equity','series_complete_12pluspop_pct_ur_equity','series_complete_18pluspop_pct_ur_equity','series_complete_65pluspop_pct_ur_equity','svi_ctgy' ,'series_complete_pop_pct_svi']

                final_new_df.drop(removecols, axis = 1, inplace = True)

                final_new_df.to_csv(df_filename)
            
            from datetime import date
            today = date.today()
            vacination_filename='vacination_'+str(today)+'.csv'
            df_filename='FINALDF_'+str(today)+'.csv'
            
            if checkfile(df_filename):
                print("TODAY's DATA FOUND ALREADY")
                stored_df=pd.read_csv(df_filename)
            else:
                print("Creating New File for today...")
                createTodayFile()
                print("FILE CREATED...")
                stored_df=pd.read_csv(df_filename)

        
            
            # giving counties based on the county list available in 7 day  Formed CSV
            current_counties=stored_df[stored_df['state']==state_ip]['county'].unique().tolist()
            text_message='Can you please tell which county you reside in from the below:\n\n'+', '.join(current_counties)
            bot.send_message(message.chat.id,text_message)

        @bot.message_handler(func=lambda msg:(msg.text is not None and msg.text in countylist))
        def county(message):
            
            def calculateSLA(final_new_df,state,county):
                formed_df=final_new_df[(final_new_df['state']==state) & (final_new_df['county']==county)]
                vac_per=formed_df['series_complete_pop_pct'].max() #New change.........................................
                Movingcases_avg=formed_df['cases_avg_per_100k'].mean()
                MovingDeath_avg=formed_df['deaths_avg_per_100k'].mean()
                MovingCompletePopPct=formed_df['series_complete_pop_pct'].mean()
                Retail=formed_df['retail_and_recreation_percent_change_from_baseline'].mean()
                grocery=formed_df['grocery_and_pharmacy_percent_change_from_baseline'].mean()
                parks=formed_df['parks_percent_change_from_baseline'].mean()
                transit=formed_df['transit_stations_percent_change_from_baseline'].mean()
                workplaces=formed_df['workplaces_percent_change_from_baseline'].mean()
                residential=formed_df['residential_percent_change_from_baseline'].mean()
                mobility_arr = np.array([Retail,grocery,parks,transit,workplaces,residential])
                mobility_value=np.nanmean(mobility_arr)
                print("Cases",Movingcases_avg)
                print("Death",MovingDeath_avg)
                print("Vaccination",MovingCompletePopPct)
                print("Mobility",mobility_value)
                SLA_RED=0
                SLA_AMBER=0
                SLA_GREEN=0

                #CASES----------------------------------------------------------------------------
                if (Movingcases_avg>=100):
                    SLA_RED+=5
                elif (Movingcases_avg>=50):
                    SLA_AMBER+=5
                elif (Movingcases_avg>=10) :
                    SLA_GREEN+=5

                #DEATH----------------------------------------------------------------------------
                if (MovingDeath_avg>15):
                    SLA_RED+=2
                elif (MovingDeath_avg>12) & (MovingDeath_avg<=15):
                    SLA_AMBER+=2
                elif  (MovingDeath_avg<=12):
                    SLA_GREEN+=2

                #VACINATION PERCENTAGE-----------------------------------------------------------------------    
                if (MovingCompletePopPct<35):
                    SLA_RED+=4
                elif (MovingCompletePopPct>=35) & (MovingCompletePopPct<70):
                    SLA_AMBER+=4
                elif  (MovingCompletePopPct>=70):
                    SLA_GREEN+=4


                 #Mobility PERCENTAGE-----------------------------------------------------------------------
                if (mobility_value>10):
                    SLA_RED+=1
                elif (mobility_value>=-10) & (mobility_value<=10):
                    SLA_AMBER+=1
                elif  (mobility_value<-10):
                    SLA_GREEN+=1


                print("RED",SLA_RED)
                print("AMBER",SLA_AMBER)
                print("GREEN",SLA_GREEN)
                return_sla=''
                if (SLA_RED==0) & (SLA_GREEN==0) & (SLA_AMBER==0):
                    return "SLA NOT FOUND"
                if (SLA_RED>=SLA_AMBER)&(SLA_RED>=SLA_GREEN):
                    return_sla= "RED"
                if (SLA_AMBER>SLA_RED)&(SLA_AMBER>=SLA_GREEN):
                    return_sla= "AMBER"
                if (SLA_GREEN>SLA_RED)&(SLA_GREEN>SLA_AMBER):
                    return_sla= "GREEN"
                return return_sla,vac_per
    
    
            global county_ip
            global current_df
            global new_df
            global state_ip
            global recent_date
            global df
            county_ip=message.text
            
            if state_ip=='':
                bot.send_message(message.chat.id,'Please type your State')
            if county_ip not in current_counties:
                text_message='Please Enter Correct County!'
                bot.send_message(message.chat.id,text_message)
            else:
                cases=current_df[(current_df['county']==county_ip) &(current_df['state']==state_ip)]['cases'].item()
                death=current_df[(current_df['county']==county_ip) &(current_df['state']==state_ip)]['deaths'].item()
                text_message='As on '+str(recent_date)+'\n'+str(state_ip)+' State, '+str(county_ip)+' County\n Cummulative Cases'+':'+str(cases)+' Total Deaths:'+str(death)
                bot.send_message(message.chat.id,text_message)
                #-----------------------------------------------------------------------------------
                import dash
                import dash_core_components as dcc
                import dash_html_components as html
                import plotly.graph_objects as go
                #-----------------------------------------------------------------------------------
                fig = go.Figure()
#                 app = dash.Dash()
#                 cases=new_df['cases']
                new_df=new_df[(new_df['county']==county_ip) &(new_df['state']==state_ip)]

                fig = go.Figure(data=go.Bar(y=new_df['cases'],x=new_df['date']))
                fig.update_layout(
                    title="United States Covid Trend- "+state_ip+" State"+county_ip+" County.",
                    xaxis_title="Date",
                    yaxis_title="Cummulative Number of Cases",
                    font=dict(
                        family="Courier New, monospace",
                        size=12,
                        color="RebeccaPurple"
                    )
                )
                print(fig)
                print(type(fig))
#                 app.layout = html.Div([
#                     dcc.Graph(figure=fig)
#                 ])
                chart_message='\n Sending latest Charts'
                bot.send_message(message.chat.id,chart_message)
                import plotly.express as px
                filename_html=state_ip+'_'+county_ip+'.html'
                fig.write_html(filename_html)
#                 fig.write_image("fig1.png")
                files={'document':open(filename_html,'rb')}
                # share_link='https://www.pythonanywhere.com/user/ajaykrishnan99/files/home/ajaykrishnan99/'+filename_html
                # bot.send_message(message.chat.id,share_link)
                requests.post(r'https://api.telegram.org/bot'+str(API_KEY)+'/sendDocument?chat_id='+str(message.chat.id),files=files)
                #Delete file After sending....
                
                
                #----Giving SLA RESPONSE------------------------------------------------------------
                from datetime import date
                import numpy as np
                today = date.today()
                vacination_filename='vacination_'+str(today)+'.csv'
                df_filename='FINALDF_'+str(today)+'.csv'
                
                stored_new_df=pd.read_csv(df_filename)
                FOUND_SLA,vacination_per=calculateSLA(stored_new_df,state_ip,county_ip)
                bot.send_message(message.chat.id,"Vacination Percentage is "+str(vacination_per)+"%") #New change........
                
                if FOUND_SLA=='RED':
                    sla_message=str(FOUND_SLA)+": In public, indoor situations, everyone in "+county_ip+","+state_ip+" should wear a mask. Make sure you're following any applicable local laws, rules, regulations, or guidelines."
                    bot.send_message(message.chat.id,sla_message)
                
                if FOUND_SLA=='AMBER':
                    sla_message=str(FOUND_SLA)+": In public, indoor settings, unvaccinated people in "+county_ip+","+state_ip+", should wear a mask. Make sure you're following any applicable local laws, rules, regulations, or guidelines."   
                    bot.send_message(message.chat.id,sla_message)
                if FOUND_SLA=='GREEN':
                    sla_message=str(FOUND_SLA)+": You are safe to travel.However people in "+county_ip+","+state_ip+", make sure you're following any applicable local laws, rules, regulations, or guidelines."
                    bot.send_message(message.chat.id,sla_message)

                #-----------------SLA CALCULATED------------------------------------------------------
                
                #----------Removing  HTML FILES------------------------------------------------------------
                
                
                import os
                directory = os.getcwd()
                files_in_directory = os.listdir(directory)
                filtered_files = [file for file in files_in_directory if file.endswith(filename_html)]
                for file in filtered_files:
                    path_to_file = os.path.join(directory, file)
                    os.remove(path_to_file)


        @bot.message_handler(func=lambda msg:(msg.text is not None))
        def defaultMessage(message):

            bot.send_message(message.chat.id,"Please Enter a State from USA")

        bot.polling()
    except Exception:
        print(Exception)
