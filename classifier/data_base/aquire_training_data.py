# coding:utf-8
import sys
import json
import pymssql
from datetime import datetime, timedelta

server = '10.99.110.132'
username = 'i2pp'
password = 'lenovo'
db = 'ARSystemDW'


def validate(datestr):
    try:
        return datetime.strptime(datestr, '%Y-%m-%d')
    except ValueError:
        # raise ValueError("Incorrect date format, should be yyyy-mm-dd")
        return None

def update_train_data_online(start_date, end_date, pc_type='ECC'):
    """
    Brief: get the training data from the DATA-BASE(SQL).
    Output:
        l_res_all <list>: Ex: [{'description': u'xxxx', 'id': u'001', 'label': u'OLS'} , ...]
    """
    l_res_all = []
    #start_date = validate(date_str)
    if not start_date:
        raise ValueError("Incorrect date format, should be yyyy-mm-dd")

    with pymssql.connect(server, username, password, database=db) as conn:
        with conn.cursor(as_dict=True) as cur:
            sql = """
            SELECT
                inc.IncidentID,
                CASE
            WHEN inc.Assignee_Login_ID LIKE 'helpdesk%' THEN
                'L1'
            ELSE
                'OLS'
            END AS AO_CC,
             inc.Description,
             inc.Reported_Date
            FROM
                DW_Incident inc
            WHERE
                inc.Reported_Date > '{}'
            AND inc.Reported_Date < '{}'
            AND inc.Assigned_Support_Organization IN (
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
                'CC-Front End',
                'Service Desk'
            )
            AND inc.InternetEmail NOT LIKE '%monitor%'
            AND inc.Product_Categorization_Tier_1 ='Applications - Strategic'
            AND inc.Product_Categorization_Tier_2 = '{}'
            """.format(start_date, end_date, pc_type)
            cur.execute(sql)

            for row in cur.fetchall():
                d_res = {
                    'label': row['AO_CC'],
                    'id': row['IncidentID'],
                    'description': row['Description']
                }
                l_res_all.append(d_res)

    return l_res_all


def update_train_data_load(date_str, days=60, pc_type='ECC'):
    """
    Note: discarded.
    """
    start_date = validate(date_str)
    if not start_date:
        raise ValueError("Incorrect date format, should be yyyy-mm-dd")
    end_date = start_date + timedelta(60)
    with pymssql.connect(server, username, password, database=db) as conn:
        with conn.cursor(as_dict=True) as cur:
            sql = """
            SELECT
                inc.IncidentID,
                CASE
            WHEN inc.Assignee_Login_ID LIKE 'helpdesk%' THEN
                'L1'
            ELSE
                'OLS'
            END AS AO_CC,
            inc.Description,
            inc.Reported_Date,
            inc.Product_Categorization_Tier_2 AS PC
            FROM
                DW_Incident inc
            WHERE
                inc.Reported_Date > '{}'
            AND inc.Reported_Date < '{}'
            AND inc.Assigned_Support_Organization IN (
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
                'CC-Front End',
                'Service Desk'
            )
            AND inc.InternetEmail NOT LIKE '%monitor%'
            AND inc.Product_Categorization_Tier_1 ='Applications - Strategic'
            AND inc.Product_Categorization_Tier_2 = '{}'
            """.format(date_str, end_date.strftime('%Y-%m-%d'), pc_type)
            cur.execute(sql)
            with open("incremetal_train.json", "w") as f:
                for row in cur.fetchall():
                    data = {
                        'label': row['AO_CC'],
                        'id': row['IncidentID'],
                        'description': row['Description'],
                        'pc': row['PC']
                    }
                    f.write(json.dumps(data) + '\n')


if __name__ == '__main__':
    USAGE = 'python aquire_training_data.py start_date[yyyy-mm-dd] end_date[yyyy-mm-dd] pc_type'
    if len(sys.argv) != 4:
        print "Parameters Error!"
        print USAGE
        sys.exit(1)

    l_res = update_train_data_online(sys.argv[1], sys.argv[2], sys.argv[3])
    print l_res, '\n', len(l_res)
    #Example: python aquire_training_data.py 2016-01-01 2016-02-02 ECC

