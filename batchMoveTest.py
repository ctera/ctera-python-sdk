from cterasdk import ServicesPortal
import cterasdk.settings

# Disable SSL verification (if needed for your environment)
cterasdk.settings.core.syn.settings.connector.ssl = False

def batch_move_test():
    """
    Test tuple move with 10 files where file #5 has wrong name to test failure handling.
    Expected: 9 files succeed, 1 fails, we can track each individual result.
    """
    admin = ServicesPortal('hcpaw.ctera.me')
    try:
        admin.login('Administrator', 'Password1!')

        # Define all moves - file #5 intentionally has wrong name
        moves = [
            ("Users/enduser1/My Files/test_move_01.txt", "Users/enduser1/My Files/dest01/"),
            ("Users/enduser1/My Files/test_move_02.txt", "Users/enduser1/My Files/dest02/"),
            ("Users/enduser1/My Files/test_move_03.txt", "Users/enduser1/My Files/dest03/"),
            ("Users/enduser1/My Files/test_move_04.txt", "Users/enduser1/My Files/dest04/"),
            ("Users/enduser1/My Files/test_move_05_WRONG.txt", "Users/enduser1/My Files/dest05/"),  # Wrong filename!
            ("Users/enduser1/My Files/test_move_06.txt", "Users/enduser1/My Files/dest06/"),
            ("Users/enduser1/My Files/test_move_07.txt", "Users/enduser1/My Files/dest07/"),
            ("Users/enduser1/My Files/test_move_08.txt", "Users/enduser1/My Files/dest08/"),
            ("Users/enduser1/My Files/test_move_09.txt", "Users/enduser1/My Files/dest09/"),
            ("Users/enduser1/My Files/test_move_10.txt", "Users/enduser1/My Files/dest10/"),
        ]

        print("🧪 BATCH TUPLE MOVE TEST - 10 Files, 1 Intentional Failure")
        print("=" * 60)
        for i, (src, dst) in enumerate(moves, 1):
            marker = "❌ (WRONG NAME)" if "WRONG" in src else "✅"
            print(f"{i:2d}. {marker} {src.split('/')[-1]} -> {dst.split('/')[-1]}")
        print("=" * 60)

        try:
            # Execute tuple move with all 10 files
            print("\n🚀 Initiating batch tuple move...")
            task_refs = admin.files.move(*moves)
            print(f"📋 Task References: {len(task_refs)} tasks created")

            # Track each task individually
            print("\n⏳ Tracking all background tasks...")
            print("=" * 60)
            
            success_count = 0
            failure_count = 0
            
            for i, task_ref in enumerate(task_refs, 1):
                print(f"\n--- Task {i:2d}/10: {task_ref} ---")
                try:
                    task_result = admin.tasks.wait(task_ref)
                    status = getattr(task_result, 'status', 'N/A')
                    progress = getattr(task_result, 'progstring', 'N/A')
                    
                    if 'completed' in status.lower() and 'warning' not in status.lower():
                        print(f"✅ SUCCESS: {status}")
                        success_count += 1
                    else:
                        print(f"❌ FAILED/WARNING: {status}")
                        failure_count += 1
                    
                    print(f"   Progress: {progress}")
                    
                    if hasattr(task_result, 'errorType') and task_result.errorType:
                        print(f"   Error: {task_result.errorType}")
                        
                except Exception as e:
                    print(f"❌ TASK ERROR: {e}")
                    failure_count += 1

            print("=" * 60)
            print(f"\n📊 FINAL RESULTS:")
            print(f"✅ Successful moves: {success_count}")
            print(f"❌ Failed moves: {failure_count}")
            print(f"📁 Total operations: {len(task_refs)}")
            
            # Verify expected results
            if success_count == 9 and failure_count == 1:
                print("🎉 TEST PASSED: 9 succeeded, 1 failed as expected!")
            else:
                print("⚠️  TEST UNEXPECTED: Different results than expected")
                
        except Exception as e:
            print(f"Batch move failed: {e}")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        admin.logout()

if __name__ == "__main__":
    batch_move_test() 