from cterasdk import ServicesPortal
import cterasdk.settings

# Disable SSL verification (if needed for your environment)
cterasdk.settings.core.syn.settings.connector.ssl = False

def move_special_char_file():
    """
    Test the new TUPLE functionality: move multiple files to different destinations in a single call.
    """
    admin = ServicesPortal('hcpaw.ctera.me')
    try:
        admin.login('Administrator', 'Password1!')

        source_file = "Users/enduser1/My Files/HPE + CTERA 2023 Edited.pptx"
        source_file2 = "Users/enduser1/My Files/CTERA Company Profile.pdf"
        destination_dir = "Users/enduser1/My Files/moved1/"
        destination_dir2 = "Users/enduser1/My Files/moved2/"

        print(f"Source 1: {source_file} -> {destination_dir}")
        print(f"Source 2: {source_file2} -> {destination_dir2}")

        try:
            # Test the NEW TUPLE functionality - move multiple files to different destinations
            print("🚀 Initiating background move task with TUPLE format...")
            task_ref = admin.files.move(
                (source_file, destination_dir),
                (source_file2, destination_dir2)
            )
            print(f"📋 Background Task Reference: {task_ref}")

            # Wait for the background task to complete and fetch the result
            print("⏳ Waiting for background task to complete...")
            task_result = admin.tasks.wait(task_ref)

            # Print the key task information in a structured way
            print("\n===== BACKGROUND TASK RESULT =====")
            print(f"Status      : {getattr(task_result, 'status', 'N/A')}")
            print(f"Progress    : {getattr(task_result, 'progstring', 'N/A')}") 
            if hasattr(task_result, 'errorType') and task_result.errorType:
                print(f"Error       : {task_result.errorType}")
            else:
                print("Error       : None")

            # Show additional details if it's a failure or warning
            if hasattr(task_result, 'status'):
                status = task_result.status.lower()
                if 'warning' in status or 'failed' in status or 'error' in status:
                    print("Additional Details:")
                    print(f"  Files Processed: {getattr(task_result, 'filesProcessed', 0)}")
                    print(f"  Total Files    : {getattr(task_result, 'totalFiles', 0)}")
                    print(f"  Elapsed Time   : {getattr(task_result, 'elapsedTime', 0)}s")
            print("==================================\n")
        except Exception as e:
            print(f"Move failed: {e}")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        admin.logout()

if __name__ == "__main__":
    move_special_char_file()


