from cterasdk import ServicesPortal
import cterasdk.settings

# Disable SSL verification (if needed for your environment)
cterasdk.settings.core.syn.settings.connector.ssl = False

def backward_compatibility_test():
    """
    Test BACKWARD COMPATIBILITY: Ensure original move syntax still works.
    Original syntax: move(file, destination=dest) returns single task reference.
    """
    admin = ServicesPortal('hcpaw.ctera.me')
    try:
        admin.login('Administrator', 'Password1!')

        source_file = "Users/enduser1/My Files/backward_test.txt"
        destination_dir = "Users/enduser1/My Files/backward_dest/"

        print("🔄 BACKWARD COMPATIBILITY TEST")
        print("=" * 50)
        print("Testing ORIGINAL move syntax:")
        print(f"Source: {source_file}")
        print(f"Destination: {destination_dir}")
        print("=" * 50)

        try:
            # Use the ORIGINAL move syntax
            print("🚀 Executing original move syntax...")
            print("   admin.files.move(source_file, destination=destination_dir)")
            
            task_ref = admin.files.move(source_file, destination=destination_dir)
            
            # Verify return type
            print(f"\n📋 Task Reference Type: {type(task_ref)}")
            print(f"📋 Task Reference Value: {task_ref}")
            
            # This should be a STRING, not a LIST
            if isinstance(task_ref, str):
                print("✅ CORRECT: Returns single task reference (string)")
            elif isinstance(task_ref, list):
                print("❌ ERROR: Returns list instead of single task reference")
                print(f"   List contents: {task_ref}")
            else:
                print(f"❌ ERROR: Unexpected return type: {type(task_ref)}")

            # Wait for the task (original way)
            print("\n⏳ Waiting for background task to complete...")
            task_result = admin.tasks.wait(task_ref)
            
            # Print results in original format
            print("\n===== BACKGROUND TASK RESULT =====")
            print(f"Status      : {getattr(task_result, 'status', 'N/A')}")
            print(f"Progress    : {getattr(task_result, 'progstring', 'N/A')}")
            
            if hasattr(task_result, 'errorType') and task_result.errorType:
                print(f"Error       : {task_result.errorType}")
            else:
                print("Error       : None")
            print("==================================")
            
            # Final compatibility check
            if isinstance(task_ref, str) and hasattr(task_result, 'status'):
                print("\n🎉 BACKWARD COMPATIBILITY: PASSED")
                print("   ✅ Original syntax works unchanged")
                print("   ✅ Returns single task reference")
                print("   ✅ Existing code will work without modification")
            else:
                print("\n❌ BACKWARD COMPATIBILITY: FAILED")
                
        except Exception as e:
            print(f"❌ Move failed: {e}")
            
    except Exception as e:
        print(f"❌ Error occurred: {e}")
    finally:
        admin.logout()

if __name__ == "__main__":
    backward_compatibility_test() 