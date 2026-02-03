import subprocess
import os
import zipfile

def create_lambda_deployment_package():
    """
    Create deployment package for Lambda function
    """
    print("Creating Lambda deployment package...")
    
    # Install dependencies
    print("Installing dependencies...")
    subprocess.run([
        'pip', 'install', '-r', 'lambda_requirements.txt', 
        '-t', 'lambda_package'
    ], check=True)
    
    # Copy Lambda function
    print("Copying Lambda function...")
    os.makedirs('lambda_package', exist_ok=True)
    subprocess.run([
        'cp', 'lambda_etl_function.py', 'lambda_package/'
    ], check=True)
    
    # Create ZIP file
    print("Creating ZIP file...")
    with zipfile.ZipFile('lambda_etl_function.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('lambda_package'):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, 'lambda_package')
                zipf.write(file_path, arcname)
    
    print("Deployment package created: lambda_etl_function.zip")

if __name__ == "__main__":
    create_lambda_deployment_package()
