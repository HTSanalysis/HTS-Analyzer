import pandas as pd
import numpy as np
import statistics
from scipy import stats
from typing import List, Dict
import base64, io



lst_384= ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P']

pos_list=['C03','C04','D03','D04','M03','M04','N03','N04','C11','C12','D11','D12',
              'G11','G12','H11','H12','M11','M12','N11','N12','C21','C22','D21','D22',
              'M21','M22','N21','N22']

neg_list=['I11','I12','J11','J12']

lst_96=[]
    
for i in ['A','C','E','G','I','K','M','O']:
    for j in range (1,25):
        lst_96.append(i+str(j))
        

def reject_outliers(data, m=2.):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.)
    return data[s < m]


def get_data(contents, filename):
    assert(filename.endswith('csv')==True)
    
    try: 
        content_decoded = base64.b64decode(contents)
        data = io.StringIO(content_decoded.decode('utf-8', errors='ignore'))
        df=pd.read_csv(data, skiprows=7, encoding="utf-8")
        df.columns = df.columns.str.strip()
    except:
        raise Exception("Something went wrong!")
    
    return df
        

def get_final_time_options(df: pd.DataFrame)->List[Dict]:
    assert("time" or "Time" in df.columns==True)
    time_options=df.columns[3:].values.tolist()
    return [{'label': value, 'value': value} for value in time_options]



def generate_dfs_for_plots(df: pd.DataFrame, final_time:str)-> List[pd.DataFrame]:
    
    DF_384_zero= pd.DataFrame(np.nan, index= lst_384,columns = range(1,25))
    DF_384_final= pd.DataFrame(np.nan, index= lst_384,columns = range(1,25))


    time_zero= df['0 min'].values.tolist()
    
    time_final= df[final_time].values.tolist()
    
    for i in range(df.shape[0]):
        DF_384_zero.iloc[i//24,i%24]=time_zero[i]
        DF_384_final.iloc[i//24,i%24]=time_final[i]
        
        
    return DF_384_zero, DF_384_final



def generate_dfs_for_cv_analysis(df:pd.DataFrame, DF_384_zero: pd.DataFrame, DF_384_final:pd.DataFrame)->List[pd.DataFrame]:
    DF_CV_zero= pd.DataFrame(np.nan, index= lst_384[:8],columns = range(1,25))
    DF_CV_final= pd.DataFrame(np.nan, index= lst_384[:8],columns = range(1,25))
    
    cvZero_list=[]
    cvFinal_list=[]
    
    for k in range(24):
        for row in range(0,15,2):
            ave_zero=np.average([DF_384_zero.iloc[row,k],DF_384_zero.iloc[row+1,k]])
            stde_zero=np.std([DF_384_zero.iloc[row,k],DF_384_zero.iloc[row+1,k]])
            cv_zero=stde_zero/ave_zero*100
            cvZero_list.append(cv_zero)
            ave_final=np.average([DF_384_final.iloc[row,k],DF_384_final.iloc[row+1,k]])
            stde_final=np.std([DF_384_final.iloc[row,k],DF_384_final.iloc[row+1,k]])
            cv_final=stde_final/ave_final*100
            cvFinal_list.append(cv_final)
            
    for i in range(192):
        DF_CV_zero.iloc[i%8,i//8]=cvZero_list[i]
        DF_CV_final.iloc[i%8,i//8]=cvFinal_list[i]
        
    return DF_CV_zero, DF_CV_final



def perform_z_analysis(df:pd.DataFrame, final_time:str):
    negative_list=[]
    posetive_list=[]
    pl_i=[]
    pl_f=[]
    nl_i=[]
    nl_f=[]
    ml_i=[]
    ml_f=[]
    
    
    for i in df.index:
        if df.loc[i]['Unnamed: 0'] in pos_list:
            posetive_list.append(df.loc[i][final_time]-df.loc[i]['0 min'])
            pl_i.append(df.loc[i]['0 min'])
            pl_f.append(df.loc[i][final_time])
        elif df.loc[i]['Unnamed: 0'] in neg_list:
            negative_list.append(df.loc[i][final_time]-df.loc[i]['0 min'])
            nl_i.append(df.loc[i]['0 min'])
            nl_f.append(df.loc[i][final_time])
        else:
            ml_i.append(df.loc[i]['0 min'])
            ml_f.append(df.loc[i][final_time])

    pa=np.mean(reject_outliers(np.array(posetive_list)))
    na=np.mean(negative_list)
    ps=np.std(posetive_list)
    ns=np.std(negative_list)
    u=(ps+ns)
    d=pa-na
    z=1-3*u/d

    
    # Plate distribution-this should be interactive 
    plate1_i={"EV":nl_i,"WT":pl_i,"MU":ml_i}
    plate1_f={"EV":nl_f,"WT":pl_f,"MU":ml_f}
    plate_i={'derivative':plate1_i}
    plate_f={'derivative':plate1_f}
    plate=[]
    for k,v in plate_i.items():
        for i,j in v.items():
            for t in j:
                if [k,i,'Zero',t] not in plate:
                    plate.append([k,i,'Zero',t])

    for k,v in plate_f.items():
        for i,j in v.items():
            for t in j:
                if [k,i,'Final',t] not in plate:
                    plate.append([k,i,'Final',t])

    df_plate= pd.DataFrame(plate, columns = ['plate', 'test','time','Fluorescence'])  
    
    return pa, na, ps, ns, z, df_plate

 


def perform_more_advanced_stuffs(df:pd.DataFrame)->List[pd.DataFrame]:
    lst_temp=[]
    k=0
    m=0
    
    DF_96= pd.DataFrame(np.nan, index= range(384),columns = ['well', 'Flourecense','384_index','activity'])
    time=len(df.columns)-2
    for row in range(0,360,2):
        if df.iloc[row,0][0] in ['A','C','E','G','I','K','M','O']:

            DF_96.iloc[m,0]=lst_96[k]
            DF_96.iloc[m,1]=df.iloc[row,time]-df.iloc[row,2]
            DF_96.iloc[m,2]=df.iloc[row,0]

            DF_96.iloc[m+1,0]=lst_96[k+1]
            DF_96.iloc[m+1,1]=df.iloc[row+1,time]-df.iloc[row+1,2]
            DF_96.iloc[m+1,2]=df.iloc[row+1,0]

            DF_96.iloc[m+2,0]=lst_96[k]
            DF_96.iloc[m+2,1]=df.iloc[row+24,time]-df.iloc[row+24,2]
            DF_96.iloc[m+2,2]=df.iloc[row+24,0]

            DF_96.iloc[m+3,0]=lst_96[k+1]
            DF_96.iloc[m+3,1]=df.iloc[row+25,time]-df.iloc[row+25,2]
            DF_96.iloc[m+3,2]=df.iloc[row+25,0]

            k +=2
            m +=4

    for row in range(0,df.shape[0]-1):
        if DF_96.iloc[row,2] in pos_list:
            lst_temp.append(DF_96.iloc[row,1])

    lst_temp=list(reject_outliers(np.array(lst_temp)))
    indexes_to_drop = []
    for row in range(0,df.shape[0]-1):
        if DF_96.iloc[row,2] in pos_list:
            if DF_96.iloc[row,1] in lst_temp:
                DF_96.iloc[row,0]='WT'
            else:
                indexes_to_drop.append(row)
        elif DF_96.iloc[row,2] in neg_list:
            DF_96.iloc[row,0]='EV'

    DF_96.drop(df.index[indexes_to_drop], inplace=True )
    #needed functions 
    wt_list=DF_96[DF_96['well']=='WT'].groupby(['well'])['Flourecense'].apply(list).tolist()[0] #to get all WT value used in statisitc 
    ave=DF_96[DF_96['well']=='EV'].groupby(['well']).mean().iloc[0,0]
    

    def acti(num):
        act=100*(num-ave)/ave
        return act

    DF_96['activity']=DF_96['Flourecense'].apply(acti)


    def t_test(group):
        lst=[]
        for i in list(group['Flourecense']):
            lst.append(i)
        t=stats.ttest_ind(lst,wt_list,equal_var = False)
        return t[0]

    def p_value (group):
        lst=[]
        for i in list(group['Flourecense']):
            lst.append(i)
        t=stats.ttest_ind(lst,wt_list,equal_var = False)
        return t[1]

    def stde(group):
        lst=[]
        for i in list(group['activity']):
            lst.append(i)
        st=statistics.pstdev(lst)
        return st

    def activity(group):
        lst=[]
        ave=DF_96[DF_96['well']=='EV'].groupby(['well']).mean().iloc[0,0]
        for i in list(group['Flourecense']):
            lst.append(i)
        act=100*(statistics.mean(lst)-ave)/ave
        return act


    ta=len(DF_96.groupby(['well']).apply(activity).index.get_level_values(0).tolist())
    DF_flash= pd.DataFrame(np.nan, index= range(ta),columns = ['well','activity','t_test','p_value'])
    DF_flash['well']=DF_96.groupby(['well']).apply(activity).index.get_level_values(0).tolist()
    DF_flash['Adjusted Flourecense']=DF_96.groupby(['well'],as_index = False).mean()['Flourecense']
    DF_flash['activity']=DF_96.groupby(['well'],as_index = False).apply(activity)
    DF_flash['t_test']=DF_96.groupby(['well'],as_index = False).apply(t_test)
    DF_flash['p_value']=DF_96.groupby(['well'],as_index = False).apply(p_value)
    DF_flash['stde for activity']=DF_96.groupby(['well'],as_index = False).apply(stde)
    pa=DF_flash[DF_flash['well']=='WT'].iloc[0,1]
    pt=DF_flash[DF_flash['well']=='WT'].iloc[0,2]
    DF_temp=DF_flash[(DF_flash['well']=='WT')|(DF_flash['activity']>=pa) & (DF_flash['p_value']<=0.1)]
    
    
    return DF_flash, DF_temp, DF_96



