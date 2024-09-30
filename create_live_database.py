import sqlite3
import os

def copy_tables(source_db, target_db, tables):
    # Remove the target file if it exists (it will be recreated)
    try:
        os.unlink(target_db)
        print(f'Removed existing database file: {target_db}')
    except FileNotFoundError:
        print(f'Database file does not exist, proceeding: {target_db}')


    # Connect to the source database
    source_conn = sqlite3.connect(source_db)
    source_cursor = source_conn.cursor()
    
    # Connect to the target database (create if it doesn't exist)
    target_conn = sqlite3.connect(target_db)
    target_cursor = target_conn.cursor()
    
    for table in tables:
        # Get the schema of the table from the source database
        source_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}';")
        create_table_sql = source_cursor.fetchone()

        if create_table_sql is not None:
            # Create the table in the target database
            target_cursor.execute(create_table_sql[0])
            
            # Copy all the records from the table in the source database
            source_cursor.execute(f"SELECT * FROM {table}")
            rows = source_cursor.fetchall()

            # Get column information to build the INSERT statement
            source_cursor.execute(f"PRAGMA table_info({table})")
            column_names = [col[1] for col in source_cursor.fetchall()]
            placeholders = ', '.join('?' for _ in column_names)
            insert_sql = f"INSERT INTO {table} ({', '.join(column_names)}) VALUES ({placeholders})"
            
            # Insert the records into the target database
            if rows:
                target_cursor.executemany(insert_sql, rows)

    # Commit and close connections
    target_conn.commit()
    source_conn.close()
    target_conn.close()

# Example usage
source_db = 'data.db'
target_db = 'jobs.db'
table_list = ['jobs', 'context_groups', 'context_keywords', 'context_group_keywords']
copy_tables(source_db, target_db, table_list)
