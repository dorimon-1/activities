from pickle import GLOBAL

from task_manager import TaskManager
from task import Task
from task_status import Status

CAPACITY_DAYS = 22
Added_Priority = 17


def show_menu():
    print("""
==== ACTIVITIES ====
1. System initialization
2. Add new task
3. Delete task
4. Task assignment (22 days)
5. Show all tasks by priority
6. Show task by id
7. Add task to execution queue
8. Update task
9. Show priority list
10. Show execution queue
11. show completed tasks
0. Exit
============================
""")


# 5. הצגת כל המשימות לפי עדיפות
# 6. איתור משימה לפי ID
# 7. הוספת משימה לתור הביצוע
# 8. עדכון משימה
# 9. יצירת תור עדיפויות חדש
# 10. הצגת תור משימות לביצוע
# 0. יציאה

def update_menu():
    print("""
    ==== Update task ====
    1. Description
    2. Duration
    3. Priority
    4. Status
    """)


def status_menu():
    print("""
    ==== status options ====
    1. pending)
    2. scheduled
    3. completed
    4. cancelled
    5. delayed
    6. in progress
    """)


def main():
    pm = TaskManager()
    while True:
        show_menu()
        try:
            choice = int(input("Choose options: ").strip())
        except ValueError:
            print("Invalid input, please try again")
            continue

        match choice:

            case 1:
                pm.system_preset()
                print("The system is now initialized")
                continue

            case 2:
                try:
                    desc = input("description: ")
                    dur = int(input("duration (in days): "))
                    pr = int(input("priority: "))
                    pm.add_task(Task(desc, pr, dur))
                    print("task added successfully!")
                except ValueError:
                    print("Invalid input...")
                continue

            case 3:
                try:
                    tid = int(input("Enter ID to delete: "))
                    ok = pm.remove_task(tid)
                    print("Task deleted" if ok else "Task not found.")
                except ValueError:
                    print("Invalid input...")
                continue

            case 4:
                assigned, bumped = pm.assign_month_simple(CAPACITY_DAYS)
                print(f"Updated the execution queue (up to {CAPACITY_DAYS} days):")
                for t in assigned:
                    print(" -", t)
                if bumped:
                    print(
                        f"\nTasks that aren't scheduled for this month (priority + {Added_Priority} applied and "
                        f"returned to priority list):")
                    for t in bumped:
                        print(" -", t)
                else:
                    print("\nAll fitting tasks scheduled. No other tasks to schedule.")
                continue

            case 5:
                print(pm.print_tasks_by_priority())
                continue

            case 6:
                try:
                    tid = int(input("Enter ID to search:"))
                    t = pm.get_task(tid)
                    print("Found:", t if t else "Not found.")
                except ValueError:
                    print("Invalid input...")
                continue

            case 7:
                try:
                    tid = int(input("Enter ID to enter to the execution queue: "))
                    ok, msg, removed = pm.force_insert_to_execution_queue(tid)
                    print(msg)
                    if removed:
                        print("Removed from queue (returned to priority repo):")
                        for t in removed:
                            print(" -", t)
                except ValueError:
                    print("Invalid input...")
                continue

            case 8:
                try:
                    tid = int(input("Enter task ID to update: "))
                    t = pm.get_task(tid)
                    if not t:
                        print("Not found.")

                    while True:
                        update_menu()
                        uc = int(input("What data would you like to update? "))

                        match uc:
                            case 1:
                                print(f"Current description: {t.get_description()}")
                                desc = input("Enter new description").strip()
                                pm.update_task(tid, desc)
                                break

                            case 2:
                                print(f"Current duration: {t.get_duration()}")
                                dur = int(input("Enter new duration"))
                                if dur <= 0:
                                    raise ValueError("Duration must be non-negative")
                                pm.update_task(tid, duration=dur)
                                break

                            case 3:
                                print(f"Current priority: {t.get_priority()}")
                                pr = int(input("Enter new priority (1 to 10)"))
                                if pr <= 0:
                                    raise ValueError("Priority must be non negative")
                                pm.update_task(tid, priority=pr)
                                break

                            case 4:
                                print(f"Current Status: {t.get_status()}")
                                status_menu()
                                sc = int(input("Please choose new status for task"))
                                pm.update_task(tid, status=sc)
                                break

                            case _:
                                raise ValueError("Invalid input")

                except ValueError:
                    print("Invalid input")
                continue

                #     tid = int(input("Enter ID to Update: "))
                #     desc = input("New Description (Leave empty if no update needed)): ").strip()
                #     dur = input("New Duration (Leave empty if no update needed)): ").strip()
                #     pr = input("New Priority (Leave empty if no update needed)):").strip()
                #     st = input("New status (leave empty if no update needed)):").strip()
                #     dur = int(dur) if dur else None
                #     pr = int(pr) if pr else None
                #     desc = desc if desc else None
                #     st = st if st else True
                #     ok, msg = pm.update_task(tid, description=desc, duration=dur, priority=pr, status=st)
                #     print("Task has been ", msg)
                # except ValueError:
                #     print("Invalid input...")

            case 9:
                pq = pm.create_priority_queue()
                print("Tasks in Priority line: ")
                for t in pq:
                    print(" ", t)
                continue

            case 10:
                q = pm.exec_queue_as_list
                if not q:
                    print("No tasks in the execution queue.")
                else:
                    print("Tasks to Execute this month:")
                    for idx, t in enumerate(q, 1):
                        print(f"{idx}. {t}")
                continue

            case 11:
                if not pm.completed_tasks:
                    print("No completed tasks yet")
                else:
                    pm.completed_tasks.list_all()
                continue

            case 0:
                print("Goodbye!")
                exit(0)

            case _:
                print("Invalid input...try again...")
                continue


if __name__ == "__main__":
    main()
