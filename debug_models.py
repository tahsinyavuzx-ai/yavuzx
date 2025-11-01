"""
Debug script to test model loading with XGBoost support.
"""
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os
import pickle
import xgboost as xgb
import tempfile

load_dotenv()

connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
container_name = 'trained-models'

print("🔍 Debugging Model Loading\n")
print(f"Container: {container_name}")
print(f"Connection string length: {len(connection_string) if connection_string else 0}\n")

try:
    # Connect to Azure
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    
    print("✅ Connected to Azure\n")
    
    # List all blobs
    print("📦 All files in container:")
    blobs = list(container_client.list_blobs())
    for blob in blobs:
        print(f"  {blob.name} ({blob.size} bytes)")
    
    print(f"\n📊 Total files: {len(blobs)}\n")
    
    # Try to load each asset
    assets = ['nasdaq', 'crypto', 'gold', 'silver', 'palladium']
    
    for asset in assets:
        print(f"\n🔍 Testing {asset.upper()}:")
        
        # Find matching files
        asset_prefix = f"{asset}_"
        matching_blobs = [b for b in blobs if b.name.startswith(asset_prefix) and b.name.endswith('.pkl')]
        
        if not matching_blobs:
            print(f"  ❌ No .pkl files found with prefix '{asset_prefix}'")
            continue
        
        print(f"  ✅ Found {len(matching_blobs)} model file(s):")
        for blob in matching_blobs:
            print(f"     - {blob.name}")
        
        # Try to load the latest one
        latest = sorted(matching_blobs, key=lambda x: x.name, reverse=True)[0]
        print(f"  📥 Loading latest: {latest.name}")
        
        try:
            blob_client = container_client.get_blob_client(latest.name)
            model_bytes = blob_client.download_blob().readall()
            
            # Try XGBoost Booster first
            model_loaded = False
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as tmp_file:
                    tmp_file.write(model_bytes)
                    tmp_path = tmp_file.name
                
                model = xgb.Booster()
                model.load_model(tmp_path)
                os.unlink(tmp_path)
                
                print(f"  ✅ Loaded as XGBoost Booster!")
                model_loaded = True
                
            except Exception as xgb_err:
                print(f"  ⚠️  Not XGBoost Booster format: {xgb_err}")
            
            # Try pickle if XGBoost failed
            if not model_loaded:
                try:
                    model = pickle.loads(model_bytes)
                    print(f"  ✅ Loaded as pickle! Model type: {type(model).__name__}")
                    model_loaded = True
                except Exception as pickle_err:
                    print(f"  ❌ Failed pickle load: {pickle_err}")
            
            if not model_loaded:
                print(f"  ❌ Could not load with any method")
                
        except Exception as e:
            print(f"  ❌ Failed to load: {e}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
