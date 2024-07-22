import pymysql
import json

# RDS connection details
RDS_URL = 'edge-care.c1c040sm422f.us-east-1.rds.amazonaws.com'
RDS_USER = 'admin'
RDS_PASSWORD = 'root12345'
RDS_PORT = 3306  # Default for MySQL
DB_NAME = 'edgecare'  # Replace with your desired database name

def insert_data(id,data,platform):
    # Connect to the RDS instance
    connection = pymysql.connect(
        host=RDS_URL,
        user=RDS_USER,
        database=DB_NAME,
        password=RDS_PASSWORD,
        port=RDS_PORT
    )

    print("user_id in rds",id)
    cursor = connection.cursor()
    create_table_query = f'''
    CREATE TABLE IF NOT EXISTS {platform} (
    id INTEGER PRIMARY KEY,
    data TEXT NOT NULL
    );
    '''
    cursor.execute(create_table_query)
    print("table ready")
    data = json.dumps(data)
    upsert_query = f'''
        INSERT INTO {platform} (id, data)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE data = VALUES(data);
        '''
    print("Upsert query:", upsert_query)
    cursor.execute(upsert_query, (id, data))
    connection.commit()
    print("upsert query executed")
    connection.close()

#if __name__ == "__main__":
 #   insert_data(1,{'niceeee':'goooood'},'google')
  #  print("add row")
