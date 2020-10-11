import numpy as np
import pandas as pd
import sys
import time

start = time.process_time()

np = [
      #case 0: Moba Loses
      {'Case':"Normal",'bid_id':"2018/041155-9-LE187",'Proveedor_Asociado':"Moba" ,'Estado':"Adjudicada", 'Promedio':17},
      {'Case':"Normal",'bid_id':"2018/041155-9-LE187",'Proveedor_Asociado':"Opko" ,'Estado':"No Adjudicada", 'Promedio':21},
      {'Case':"Normal",'bid_id':"2018/041155-9-LE187",'Proveedor_Asociado':"BBB" ,'Estado':"No Adjudicada", 'Promedio':24} ,
     
      #Case1 : WinPrice<SECOND_PRICE -Typical case - get the second highest after win
      {'Case':"Normal",'bid_id':"2019/111051765-53-LE192",'Proveedor_Asociado':"Moba", 'Estado':"No Adjudicada", 'Promedio':74},
      {'Case':"Normal",'bid_id':"2019/111051765-53-LE192",'Proveedor_Asociado':"Opko" ,'Estado':"Adjudicada", 'Promedio':58},
      {'Case':"Normal",'bid_id':"2019/111051765-53-LE192",'Proveedor_Asociado':"BBB", 'Estado':"No Adjudicada", 'Promedio':100},
   
      #Case 2:  WinPrice>SECOND_PRICE --> GAP TO SECOND = 0 --> Find the first lowest price after winning --> 420 (not 370)
      {'Case':"Not_Normal",'bid_id':"2019/111058045-27-LQ192",'Proveedor_Asociado':"Opko", 'Estado':"No Adjudicada", 'Promedio':370},
      {'Case':"Not_Normal",'bid_id':"2019/111058045-27-LQ192",'Proveedor_Asociado':"BBB" ,'Estado':"No Adjudicada", 'Promedio':425},
      {'Case':"Not_Normal",'bid_id':"2019/111058045-27-LQ192",'Proveedor_Asociado':"Moba",'Estado':"Adjudicada", 'Promedio':420},
     
      # Case 3: No Winner --> Take only Lowest_Price, and second_price (if there is) if second=win --> second
      {'Case':"Not_Normal",'bid_id':"2019/111058088-25-LE1914",'Proveedor_Asociado':"Moba" ,'Estado':"No Adjudicada", 'Promedio':31},
      {'Case':"Not_Normal",'bid_id':"2019/111058088-25-LE1914",'Proveedor_Asociado':"BBB" ,'Estado':"Adjudicada", 'Promedio':40},
      {'Case':"Not_Normal",'bid_id':"2019/111058088-25-LE1914",'Proveedor_Asociado':"Opko", 'Estado':"No Adjudicada", 'Promedio':26}]

wds=pd.DataFrame(np)
wds


def encode_values(wds): 
    object_df=wds.select_dtypes(exclude=['number'])  #filer the non-numeric cols (we don't want to encode them)
    filtered_df=object_df.drop(['bid_id'], axis=1) #dropping bid_id, it must not be encrpyed (add other colums too, if needed)
    cols=filtered_df.columns.tolist() #get all column names
    encodingDict={}
    
    for col in cols:
        my_df=pd.DataFrame()
        rows=wds[col].unique()
        my_df[col]=rows
        my_df['value']=my_df.index # adding index Column as value
        my_df.set_index(col,inplace=True)
        encodingDict.update(my_df.to_dict())
             
    df_encodingDict = pd.DataFrame.from_dict(encodingDict, orient ='index')  #create df from dict
    df_encodingDict=df_encodingDict.transpose() #flip cols/rows
    df_encodingDict.to_csv(r'encodingDict(forReference).csv') # create a csv (for reference)
    
    return encodingDict  


def calculate_gap1st(moba_price,winning_price):
    #Gordon's formula is: Percentage Increase = |MobaPrice - WinPrice| / |MobaPrice|
    g1s=round(((moba_price-winning_price)/moba_price)*100,0)
    return g1s


def calculate_gap2nd(second_price, lowest_price):
    g2s = round(((second_price-lowest_price)/lowest_price),2)*100
    if(g2s>0):
        return g2s
    else:
        return 0

wds.loc[(wds['Estado']=='Adjudicada')& (wds['Proveedor_Asociado']=='Moba'), 'MobaWins'] = 1
wds.loc[(wds['Estado']=='No Adjudicada')& (wds['Proveedor_Asociado']=='Moba'), 'MobaWins'] = 0


#wds=wds.loc[wds['bid_id']=="2019/111051765-53-LE192"]

ids_list2= wds.bid_id.unique()

for bid in ids_list2:
    
    temp_wds = wds[wds['bid_id']==bid]
        
    lowest_price= temp_wds['Promedio'].drop_duplicates().nsmallest(1).iloc[-1]
    second_price= temp_wds['Promedio'].drop_duplicates().nsmallest(2).iloc[-1]    
    
    wds.loc[wds['bid_id'] == bid, 'lowest_price'] = lowest_price
    wds.loc[wds['bid_id'] == bid, 'second_price'] = second_price

    #check cuz sometimes there are no winners
    any_winner = (temp_wds.Estado == 'Adjudicada').any()
    moba_wins= (temp_wds['MobaWins'] == 1).any()
    
   
    if (any_winner):
        #add a column for the winning price
        win_wds=temp_wds[(temp_wds['bid_id']==bid) & (wds['Estado'] == "Adjudicada")]
        winning_price= win_wds['Promedio'].drop_duplicates().nsmallest(1).iloc[-1]    
        wds.loc[wds['bid_id'] == bid, 'Winning_price'] = winning_price
        
        #check the second price for cases in which winPrice>lowestPrice
        if (winning_price>lowest_price):
            prices_list=temp_wds.Promedio.unique()
            prices_list.sort()
            for item in prices_list:
                if item>winning_price:
                    second_price=item
                    wds.loc[wds['bid_id'] == bid, 'second_price'] = second_price  
                    break
                else:
                    pass  
            #for the cases in which the winning price is the highest number
            if (winning_price>second_price):
                second_price=0
                wds.loc[wds['bid_id'] == bid, 'second_price'] = second_price
                
        #If Moba wins, calculate g2s
        if (moba_wins):
            wds.loc[wds['MobaWins']==1,'G2S_Percentage'] = wds.apply(lambda x: calculate_gap2nd(x['second_price'], x['Winning_price']), axis=1)
        else:
            # else Gap1st
            wds.loc[wds['MobaWins']==0,'G1S_Percentage'] = wds.apply(lambda x: calculate_gap1st(x['Promedio'], x['Winning_price']), axis=1)     
    else:
        # because sometimes there are not tenders won
        wds.loc[wds['bid_id'] == bid, 'Winning_price'] = 0
        wds.loc[wds['bid_id'] == bid, 'G2S_Percentage'] = 0
        wds.loc[wds['bid_id'] == bid, 'G1S_Percentage'] = 0
        
        
                 
print(time.process_time() - start)
wds.fillna(0, inplace=True)



# options = ['2019/111058088-25-LE1914', '2018/041155-9-LE187'] 
  
# # selecting rows based on condition 
# wds.loc[wds['bid_id'].isin(options)] 


## MappingTable in case we need to do it from external CSV 
# mappingTable = pd.read_csv("mappignTable.csv", delimiter=';', engine='python')
# #mappingTable.rename(columns = {'Proveedor_Asociado':'TEST'}, inplace = True) 
# mappingTable

encodingDict=encode_values(wds)