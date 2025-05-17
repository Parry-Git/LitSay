import time
import MySQLdb
import sys
from decimal import Decimal # Import Decimal for potential formatting

# --- Database Connection Parameters ---
# WARNING: Avoid hardcoding credentials in production code. Use secure methods.
DB_HOST = "obmt6mf0yc1gvn4w-mi.aliyun-cn-hangzhou-internet.oceanbase.cloud"
DB_PORT = 3306
DB_USER = "parry"
DB_PASSWORD = "2739458679AAbb//"
DB_NAME = "tutorialdb"
# SSL options might be needed depending on your server configuration
# SSL_OPTIONS = {"ca": "database/ca.pem"} # Example

# --- Helper Function to Execute and Print Queries ---
def execute_and_print_query(cursor, title, query):
    """Executes a SQL query and prints the results in a formatted way."""
    print("-" * 80)
    print(f"Executing Query: {title}")
    print("-" * 80)
    try:
        cursor.execute(query)
        results = cursor.fetchall()

        if not results:
            print("Query returned no results.")
            print("-" * 80)
            return

        # Get column headers
        column_names = [desc[0] for desc in cursor.description]
        print(f"{' | '.join(column_names)}")
        print("-" * len(' | '.join(column_names))) # Separator line

        # Print rows
        for row in results:
            # Format row data for printing (handle None, Decimal, etc.)
            formatted_row = []
            for item in row:
                if isinstance(item, Decimal):
                    formatted_row.append(f"{item:.2f}") # Format decimals to 2 places
                elif item is None:
                    formatted_row.append("NULL")
                else:
                    formatted_row.append(str(item))
            print(f"{' | '.join(formatted_row)}")

    except MySQLdb.Error as e:
        print(f"Error executing query '{title}': {e}")
    finally:
        print("-" * 80)
        print("\n") # Add space after query output

# --- Main Script ---
connection = None # Initialize connection to None
cursor = None     # Initialize cursor to None
try:
    # Establish database connection
    print("Connecting to database...")
    connection = MySQLdb.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
        # ssl_mode="VERIFY_CA", # Uncomment and configure SSL if needed
        # ssl=SSL_OPTIONS      # Uncomment and configure SSL if needed
    )
    print("Connection successful.")

    # Create cursor object
    cursor = connection.cursor()

    # --- Interesting Queries ---

    # Query 1: Top 5 Customers by Total Purchase Amount (All Channels)
    query1_title = "Top 5 Customers by Total Purchase Amount"
    query1_sql = """
    WITH CombinedSales AS (
        SELECT ss_customer_sk AS customer_sk, ss_net_paid_inc_tax AS sales_amount FROM store_sales WHERE ss_customer_sk IS NOT NULL
        UNION ALL
        SELECT cs_bill_customer_sk AS customer_sk, cs_net_paid_inc_ship_tax AS sales_amount FROM catalog_sales WHERE cs_bill_customer_sk IS NOT NULL
        UNION ALL
        SELECT ws_bill_customer_sk AS customer_sk, ws_net_paid_inc_ship_tax AS sales_amount FROM web_sales WHERE ws_bill_customer_sk IS NOT NULL
    ),
    CustomerTotalSales AS (
        SELECT
            customer_sk,
            SUM(sales_amount) AS total_sales
        FROM CombinedSales
        GROUP BY customer_sk
    )
    SELECT
        c.c_customer_id,
        c.c_first_name,
        c.c_last_name,
        cts.total_sales
    FROM CustomerTotalSales cts
    JOIN customer c ON cts.customer_sk = c.c_customer_sk
    ORDER BY cts.total_sales DESC
    LIMIT 5;
    """
    execute_and_print_query(cursor, query1_title, query1_sql)

    # Query 2: Sales Performance by Product Category (Top 5)
    query2_title = "Top 5 Product Categories by Sales Revenue"
    query2_sql = """
    WITH CombinedSalesItems AS (
        SELECT ss_item_sk AS item_sk, ss_net_paid_inc_tax AS sales_amount FROM store_sales
        UNION ALL
        SELECT cs_item_sk AS item_sk, cs_net_paid_inc_ship_tax AS sales_amount FROM catalog_sales
        UNION ALL
        SELECT ws_item_sk AS item_sk, ws_net_paid_inc_ship_tax AS sales_amount FROM web_sales
    )
    SELECT
        i.i_category,
        SUM(csi.sales_amount) AS total_category_sales
    FROM CombinedSalesItems csi
    JOIN item i ON csi.item_sk = i.i_item_sk
    WHERE i.i_category IS NOT NULL -- Exclude items without a category if necessary
    GROUP BY i.i_category
    ORDER BY total_category_sales DESC
    LIMIT 5;
    """
    execute_and_print_query(cursor, query2_title, query2_sql)

    # Query 3: Monthly Sales Trend for Year 2001 (Example Year)
    query3_title = "Monthly Sales Revenue Trend for Year 2001"
    query3_sql = """
    WITH CombinedSalesDates AS (
        SELECT ss_sold_date_sk AS date_sk, ss_net_paid_inc_tax AS sales_amount FROM store_sales
        UNION ALL
        SELECT cs_sold_date_sk AS date_sk, cs_net_paid_inc_ship_tax AS sales_amount FROM catalog_sales
        UNION ALL
        SELECT ws_sold_date_sk AS date_sk, ws_net_paid_inc_ship_tax AS sales_amount FROM web_sales
    )
    SELECT
        d.d_year,
        d.d_moy, -- Month of Year
        SUM(csd.sales_amount) AS monthly_sales
    FROM CombinedSalesDates csd
    JOIN date_dim d ON csd.date_sk = d.d_date_sk
    WHERE d.d_year = 2001 -- Filter for a specific year (adjust as needed)
    GROUP BY d.d_year, d.d_moy
    ORDER BY d.d_year, d.d_moy;
    """
    execute_and_print_query(cursor, query3_title, query3_sql)

    # Query 4: Top 5 Reasons for Returns by Net Loss
    query4_title = "Top 5 Return Reasons by Net Loss"
    query4_sql = """
    WITH CombinedReturns AS (
        SELECT sr_reason_sk AS reason_sk, sr_net_loss AS net_loss FROM store_returns WHERE sr_reason_sk IS NOT NULL
        UNION ALL
        SELECT cr_reason_sk AS reason_sk, cr_net_loss AS net_loss FROM catalog_returns WHERE cr_reason_sk IS NOT NULL
        UNION ALL
        SELECT wr_reason_sk AS reason_sk, wr_net_loss AS net_loss FROM web_returns WHERE wr_reason_sk IS NOT NULL
    )
    SELECT
        r.r_reason_desc,
        SUM(cr.net_loss) AS total_net_loss
    FROM CombinedReturns cr
    JOIN reason r ON cr.reason_sk = r.r_reason_sk
    GROUP BY r.r_reason_desc
    ORDER BY total_net_loss DESC
    LIMIT 5;
    """
    execute_and_print_query(cursor, query4_title, query4_sql)

    tic = time.time()
    for _ in range(100):
        execute_and_print_query(cursor, query1_title, query1_sql)
    toc = time.time()
    print(f"average time token: {(toc - tic) / 100} seconds")


except MySQLdb.Error as e:
    print(f"Database error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    sys.exit(1)
finally:
    # Close cursor and connection
    if cursor:
        cursor.close()
    if connection and connection.open:
        connection.close()
        print("Database connection closed.")
    else:
        print("Database connection was not opened or already closed.")

