import mysql.connector

conn = mysql.connector.connect(host = 'localhost', user = 'root', password = '', database = 'examchecker')
cursor = conn.cursor()

# if conn.is_connected():
#     print('Connection Success')
# else:
#     print('Connection Fail')

###############################
#        SQL COMMANDS         #
###############################

uniqueCode = ['1fhqzu']
query = "SELECT anskey FROM `tbl_ans` WHERE uniqueCode = %s"
cursor.execute(query,(uniqueCode))

for row in cursor:
    anskey = row[0]

###############################
cursor.close()
conn.close()