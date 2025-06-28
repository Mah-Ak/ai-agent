import clickhouse_connect
import pandas as pd
from datetime import datetime
import time
import socket
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

def test_connection(host, port):
    """Test if we can reach the host"""
    try:
        socket.create_connection((host, port), timeout=5)
        print(f"✅ Can connect to {host}:{port}")
        return True
    except OSError as e:
        print(f"❌ Cannot connect to {host}:{port}")
        print(f"Error: {str(e)}")
        return False

def get_clickhouse_client():
    """Create and return a ClickHouse client connection"""
    host = 'proxy.bk0i.basalam.dev'
    port = 39677
    
    print(f"\n🔍 Testing connection to {host}:{port}...")
    if not test_connection(host, port):
        raise ConnectionError(f"Cannot establish connection to {host}:{port}")
    
    print("\n🔄 Creating ClickHouse client...")
    
    # Configure retries
    session = requests.Session()
    retries = Retry(
        total=5,  # total number of retries
        backoff_factor=1,  # wait 1, 2, 4, 8, 16 seconds between retries
        status_forcelist=[500, 502, 503, 504]  # retry on these status codes
    )
    session.mount('http://', HTTPAdapter(max_retries=retries))
    
    return clickhouse_connect.get_client(
        host=host,
        port=port,
        user='dev_jozi',
        password='PCRBnQTqW3rXEGvSgmiOHjbCelRhasGI',
        connect_timeout=60,  # increased timeout
        request_timeout=60,  # request timeout
        session=session,
        settings={
            'max_execution_time': 60,
            'keep_alive_timeout': 60
        }
    )

def fetch_test_record(client):
    """Fetch just one record for testing"""
    query = """
    SELECT 1 AS test
    """
    
    print("\n📊 Testing query execution...")
    try:
        # First try a simple test query
        result = client.query(query)
        print("✅ Test query successful!")
        
        # Now try the actual query
        print("\n📊 Fetching test record from model_sales...")
        result = client.query("SELECT * FROM OLAPBasalam.model_sales LIMIT 1")
        
        if result.result_rows:
            print("✅ Successfully fetched a record!")
            return result.result_rows[0], result.column_names
        else:
            print("⚠️ No records found")
            return None, None
    except Exception as e:
        print(f"❌ Query error: {str(e)}")
        return None, None

def save_test_record(data, columns):
    """Save test record to CSV"""
    if not data:
        return None
        
    print("\n💾 Saving test record...")
    df = pd.DataFrame([data], columns=columns)
    filename = f'agents/test_record_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    df.to_csv(filename, index=False)
    return filename

def main():
    start_time = time.time()
    
    try:
        # Connect to ClickHouse
        client = get_clickhouse_client()
        
        # Fetch test record
        data, columns = fetch_test_record(client)
        
        if data:
            # Save test record
            filename = save_test_record(data, columns)
            if filename:
                print(f"✅ Test record saved to {filename}")
        
        # Show execution time
        elapsed_time = time.time() - start_time
        print(f"\n⏱️ Total time: {elapsed_time:.2f} seconds")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nDebug information:")
        if hasattr(e, 'response'):
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
    finally:
        if 'client' in locals():
            client.close()
            print("\n🔒 ClickHouse connection closed")

if __name__ == "__main__":
    main() 