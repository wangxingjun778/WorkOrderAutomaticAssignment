# coding: utf-8
#In[8]:


import pymssql
import pandas as pd
import os

class ARSystemHandler(object):
    
    def __init__(self):
        self.CSV_FILE_PATH = 'Data/INC_FOR_AUTO_ASSIGN.data'
        self.sql2 = """
            SELECT
            case when Product_Categorization_Tier_2 in ('ECC','Service ECC')
            and Product_Categorization_Tier_3='GL'
            then 'OF'
            when Product_Categorization_Tier_2 = 'GTS'
            then 'OF'
            when Product_Categorization_Tier_2 in ('IPG PLM', 'TPG PLM','LOIS','MBG PLM','LDTS','EBG PLM','TBG PLM','PCG PLM','ELOIS')
            then 'IPM'
            when Product_Categorization_Tier_2 in ('ECC','Service ECC') and Product_Categorization_Tier_3 ='Master Data'
            then 'IPM'
            when Product_Categorization_Tier_2 in ('3PO','Esourcing','SRM')
            THEN 'Procurement'
            when Product_Categorization_Tier_2 in ('ECC','Service ECC') and Product_Categorization_Tier_3='MM'
            then 'Procurement'
            when Product_Categorization_Tier_2 in ('I2-Strategic System','APO','HANA VMI','HANA Reporting') 
            then 'Planning'
            when Product_Categorization_Tier_2 in ('ECC','Service ECC') and Product_Categorization_Tier_3 in ( 'PP', 'QM', 'WM')
            then 'Planning' 
            else 'Other'
            end Team,
            case when InternetEmail like '%monitor%'
            then 'MONITOR'
            else 'USER'
            end USER_MONITOR,
            case when Assigned_Support_Organization like 'AO%'
            then 'AO'
            when Assigned_Support_Organization like 'CC%'
            then 'OLS'
            when Assigned_Support_Organization like 'Service Desk'
            then 'L1'
            else 'Other'
            end AO_CC,
             inc.*
            FROM
             DW_Incident inc
            WHERE
             inc.Reported_Date > '2014-04-01'
            AND 
             inc.Assigned_Support_Organization IN (
              'CC-Product Management',
              'CC-Marketing & Sales',
              'CC-Service',
              'CC-Supply Chain',
              'CC-Corporate Foundation',
              'AO-Back-end App.',
              'AO-Corporate App.,',
              'AO-LC Front-end App.',
              'AO-LI Front-end App.',
              'CC-Back End',
              'CC-Corporate',
              'CC-Front End','Service Desk'
             )
            """

        self.server = '10.99.110.132'
        self.user = 'i2pp'
        self.password = 'lenovo'
        self.conn2 = None

    def getINCData(self):
        inc2 = None        
        if(os.path.exists(self.CSV_FILE_PATH)):
            inc2 = pd.read_pickle(self.CSV_FILE_PATH)
        else:
            try:
                self.conn2 = pymssql.connect(self.server, self.user, self.password, "ARSystemDW")
                inc2 = pd.read_sql(self.sql2,self.conn2)
                inc2.to_pickle(self.CSV_FILE_PATH)
            except Exception as e:
                print(e)
            finally:
                self.conn2.close() #释放数据库资源    
            if self.conn2:
                self.conn2.close()
                   
        return inc2
    
    def main():
        pass

    if __name__ == "__main__":
        main()
        
# handler = ARSystemHandler()
# inc2 = handler.getINCData()
# print(inc2)


# In[ ]:




