import os
import zipfile
import urllib.request
import ssl

def setup_and_download_data():
    # 1. Define and create the directories cleanly on your Mac
    raw_dir = os.path.join("data", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    
    # 2. Link to Cricsheet's official IPL CSV download bundle
    cricsheet_url = "https://cricsheet.org/downloads/ipl_csv2.zip"
    zip_target_path = os.path.join("data", "ipl_raw_bundle.zip")
    
    print("Downloading IPL dataset from Cricsheet... This might take a moment.")
    
    # Mac Optimization: Create an unverified SSL context to bypass local certificate errors
    mac_ssl_context = ssl._create_unverified_context()
    
    # Request agent header to prevent the server from blocking the connection
    req = urllib.request.Request(
        cricsheet_url, 
        headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    )
    
    try:
        # Pass the custom context into urlopen
        with urllib.request.urlopen(req, context=mac_ssl_context) as response, open(zip_target_path, 'wb') as out_file:
            out_file.write(response.read())
            
        print("Download complete! Extracting files to data/raw/...")
        
        # 3. Extract the ZIP contents cleanly into your target directory
        with zipfile.ZipFile(zip_target_path, 'r') as zip_ref:
            zip_ref.extractall(raw_dir)
            
        # 4. Clean up the leftover zip container file
        os.remove(zip_target_path)
        print(f"Success! All raw match files are now sitting safely in: {raw_dir}")
        
    except Exception as e:
        print(f"An error occurred during execution on macOS: {e}")

if __name__ == "__main__":
    setup_and_download_data()