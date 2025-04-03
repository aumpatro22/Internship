import subprocess
import sys
import time

# Compatible packages versions less likely to cause metadata issues
PACKAGES = [
    "requests==2.28.2",
    "sqlalchemy==1.4.48",
    "pandas==1.5.3",
    "pydantic==1.10.8",
    "python-multipart==0.0.6",
    "fastapi==0.95.2",
    "uvicorn==0.21.1",
]

def install_package(package):
    print(f"Installing {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        print(f"Failed to install {package}. Trying with --no-cache-dir...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", package])
            return True
        except subprocess.CalledProcessError:
            print(f"ERROR: Failed to install {package}")
            return False

def main():
    print("Starting installation of packages for Stock Market Tracker...")
    success_count = 0
    fail_count = 0
    
    # Try to update pip first
    try:
        print("Attempting to upgrade pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    except:
        print("Warning: Could not upgrade pip. Continuing with installation...")
    
    # Install each package individually
    for package in PACKAGES:
        if install_package(package):
            success_count += 1
        else:
            fail_count += 1
        time.sleep(1)  # Small pause between installations
    
    print("\n====== Installation Summary ======")
    print(f"Successfully installed: {success_count}")
    print(f"Failed installations: {fail_count}")
    
    if fail_count == 0:
        print("\nAll packages were installed successfully!")
        print("You can now run the application with: uvicorn stock_tracker_agent:app --reload")
    else:
        print("\nSome packages failed to install.")
        print("Please try installing them manually or check the README for alternative methods.")

if __name__ == "__main__":
    main()
