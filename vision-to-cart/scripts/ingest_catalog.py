import os
import sys

# Ensure root path is in PYTHONPATH for direct running
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.catalog_intelligence_tool import run_catalog_intelligence

def main():
    print("--------------------------------------------------")
    print("Vision-to-Cart: Starting Catalog Ingestion Script")
    print("--------------------------------------------------")

    # Set parameters — use absolute path relative to project root (not CWD)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    catalog_path = os.path.join(project_root, "data_services", "catalog", "catalog.json")
    
    # Run the intelligence tool
    payload = {"catalog_path": catalog_path}
    try:
        result = run_catalog_intelligence(payload)
        print("Ingestion execution completed.")
        print(f"Status: {result.get('status')}")
        print(f"Products Processed: {result.get('products_processed')}")
        print(f"Vector Store Populated: {result.get('vector_store_populated')}")
        print("--------------------------------------------------")
    except Exception as e:
        print(f"CRITICAL ERROR running catalog ingestion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
