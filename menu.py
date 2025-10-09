from pickle import GLOBAL

from task_manager import TaskManager
from task import Task

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


def main():
    pm = TaskManager()
    while True:
        show_menu()
        choice = input("Choose options: ").strip()

        if choice == "1":
            pm.system_preset()
            print("The system is now initialized")
        elif choice == "2":
            try:
                desc = input("description: ")
                dur = int(input("duration (in days): "))
                pr = int(input("priority: "))
                pm.add_task(Task(desc, pr, dur))
                print("task added successfully!")
            except ValueError:
                print("Invalid input...")
        elif choice == "3":
            try:
                tid = int(input("Enter ID to delete: "))
                ok = pm.remove_task(tid)
                print("Task deleted" if ok else "Task not found.")
            except ValueError:
                print("Invalid input...")
        elif choice == "4":
            assigned, bumped = pm.assign_month_simple(CAPACITY_DAYS)
            print(f"Updated the execution queue (up to {CAPACITY_DAYS} days):")
            for t in assigned:
                print(" -", t)
            if bumped:
                print(f"\nTasks that aren't scheduled for this month (priority + {Added_Priority} applied and returned to priority list):")
                for t in bumped:
                    print(" -", t)
            else:
                print("\nAll fitting tasks scheduled. No other tasks to schedule.")
        elif choice == "5":
            print(pm.print_tasks_by_priority())
        elif choice == "6":
            try:
                tid = int(input("Enter ID to search:"))
                t = pm.get_task(tid)
                print("Found:", t if t else "Not found.")
            except ValueError:
                print("Invalid input...")
        elif choice == "7":
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
        elif choice == "8":
            try:
                tid = int(input("Enter ID to Update: "))
                desc = input("New Description (Leave empty if no update needed)): ").strip()
                dur = input("New Duration (Leave empty if no update needed)): ").strip()
                pr = input("New Priority (Leave empty if no update needed)):").strip()
                dur = int(dur) if dur else None
                pr = int(pr) if pr else None
                desc = desc if desc else None
                ok, msg = pm.update_task(tid, description=desc, duration=dur, priority=pr)
                print("Task has been ", msg)
            except ValueError:
                print("Invalid input...")
        elif choice == "9":
            pq = pm.create_priority_queue()
            print("Tasks in Priority line: ")
            for t in pq:
                print(" ", t)
        elif choice == "10":
            q = pm.exec_queue_as_list
            if not q:
                print("No tasks in the execution queue.")
            else:
                print("Tasks to Execute this month:")
                for idx, t in enumerate(q, 1):
                    print(f"{idx}. {t}")
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Wrong input...try again...")

if __name__ == "__main__":
    main()