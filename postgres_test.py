import psycopg2 as sql


conn = sql.connect(host='ec2-54-235-156-60.compute-1.amazonaws.com',
                   database='d90dv1hptfo8l9',
                   user='tagnipsifgbhic',
                   port='5432',
                   password='c26e906de3e7d5f7f54872432bcab7cbbcee3ab24b530964dfe4480fa4fef9e2')
cursor = conn.cursor()
cursor.execute("DROP TABLE test")
cursor.execute("CREATE TABLE test (test VARCHAR(32))")
cursor.execute("INSERT INTO test (test) VALUES (%s)", ("test_string", ))
cursor.execute("SELECT test FROM test")
data = cursor.fetchall()
print(data)
conn.commit()
conn.close()
