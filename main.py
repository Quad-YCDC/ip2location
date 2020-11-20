import os ,json , requests , psycopg2
from psycopg2 import pool
from config import config
from datetime import datetime
from urllib.parse import urlparse
import dns.resolver



class Connectdb:
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        threaded_pool = psycopg2.pool.ThreadedConnectionPool(1, 20, **params)
        if (conn and threaded_pool):
            print("DB connected")
            pool_conn = threaded_pool.getconn()
    except (Exception, psycopg2.DatabaseError) as error:
        print("DB connect fail", error)



class List: #리스트 변환
    
    def list_int(self,d):
        return list(d)[0]
    
    def list_str(self,s):
        return list(s)[0]


class Service:

    def Collect_url(): # url 수집
        Connectdb.cur.execute("SELECT indicator FROM reputation_data;")
        url = List().list_str(Connectdb.cur.fetchone())
        host = urlparse(url)
        netloc = host.netloc()
        ip = netloc.split(':')[0]

        #print(host.netloc())
        return ip 


    def Find_ip(): #도메인 ip로 검색
        domain = Service.Collect_url(ip)
        p = dns.resolver.Resolver()
        p.nameservers = ['8.8.8.8']
        ip = dns.resolver.query(domain).response
        print(ip)

        return ip

    

class Calculation: # 공식계산
    
    
    def Calcul_ip ():
        ip = Service.Collect_url()
        ip1 = int(ip.split('.')[0])
        ip2 = int(ip.split('.')[1])
        ip3 = int(ip.split('.')[2])
        ip4 = int(ip.split('.')[3])
        ipcomputation = int(ip1*(256*256*256) + ip2*(256*256) + ip3*(256) + ip4)

        return ipcomputation

    def put_ipcomput (): # ip값 DB insert
        
        insert = Calculation.Calcul_ip()
        Connection_db.cur.execute('INSERT into IP2LOCATION_Result(ipcomputation) values(%d);'(insert))
        Connection_db.conn.commit()
        sleep(0.1)


    def compare_sql (): #ip_from - ip_to compare
        Connection_db.cur.execute(
        'SELECT * FROM ip2location_result WHERE ipcomputation BETWEEN (SELECT * FROM ip2location_data WHERE IP_FROM) AND (SELECT * FROM ip2location_data WHERE IP_TO);')
        Connection_db.conn.commit()


    def query_to_grafana ():
        Connectdb.cur.execute('SELECT LATITUDE FROM ip2location_data;')
        grafana = Connectdb.cur.fetchone()
        Connectdb.cur.execute('INSERT into ip2location_Result(Lati) values(%f);'(grafana))
        Connection_db.conn.commit()
        
