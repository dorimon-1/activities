# WRITTEN BY:
#דניאל קצ'מרק + סתיו עזרא
from task_manager import TaskManager
from task import Task
from task_status import Status

CAPACITY_DAYS = 22
Added_Priority = 17


def pre_init_menu():
    print("""
==== ACTIVITIES ====
1. System initialization
0. Exit
============================
""")


def post_init_menu():
    print("""
==== ACTIVITIES ====
1. Reset system
2. Add new task
3. Delete task
4. Task assignment (22 days)
5. Show all tasks by priority
6. Show task by id
7. Add task to execution queue
8. Update task
9. Show priority list
10.Show execution queue
11.Show completed tasks
12.Show all tasks
0. Exit
============================
""")


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
    1. pending
    2. scheduled
    3. completed
    4. cancelled
    5. delayed
    """)


def main():
    pm = TaskManager()
    initialized = False
    while True:
        if not initialized:
            pre_init_menu()
        else:
            post_init_menu()
        try:
            choice = int(input("Choose options: ").strip())
        except ValueError:
            print("Invalid input, please try again")
            continue

        if not initialized:
            match choice:
                case 1:
                    pm.system_preset()
                    initialized = True
                    print("The system is now initialized.")
                case 0:
                    print("Goodbye!")
                    exit(0)
                case _:
                    print("Invalid input... You must initialize the system first!")

        else:
            match choice:
                case 1:
                    pm.reset_system()
                    print("System has been reset.")

                case 2:
                    try:
                        desc = input("description: ")
                        dur = int(input("duration (in days): "))
                        pr = int(input("priority: "))
                        pm.add_task(Task(desc, pr, dur))
                        print("Task added successfully!")
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
                        print(f"\nTasks that aren't scheduled for this month:")

                        for t in bumped:
                            while True:
                                ca = input(f"Does task {t} have client's approval? (y/n)\n").strip().lower()
                                if ca in ('y', 'n'):
                                    break
                                print("Invalid input, please try again")

                            match ca:
                                case 'y':
                                    pm.set_task_status(t.task_id, Status.DELAYED)
                                    t_priority = t.get_priority()
                                    t.set_priority(t_priority + Added_Priority)
                                    print(
                                        f"Task #{t.task_id} updated successfully: "
                                        f"+{Added_Priority} to priority, status changed to {t.get_status().name}")

                                case 'n':
                                    try:
                                        pm.set_task_status(t.task_id, Status.CANCELLED)
                                        print(f"Task #{t.task_id} status changed to {t.get_status().name}")
                                        pm.remove_task(t.task_id)
                                        print("Task removed from system.")
                                    except ValueError:
                                        print("Couldn't remove task from system.")

                                case _:
                                    print("Invalid input. Please enter 'y' or 'n'.")

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
                                while True:
                                    ca = input(f"Does task {t} have client's approval? (y/n)\n").strip().lower()
                                    if ca in ('y', 'n'):
                                        break
                                    print("Invalid input, please try again")

                                match ca:
                                    case 'y':
                                        pm.set_task_status(t.task_id, Status.DELAYED)
                                        t_priority = t.get_priority()
                                        t.set_priority(t_priority + Added_Priority)
                                        print(
                                            f"Task #{t.task_id} updated successfully: "
                                            f"+{Added_Priority} to priority, status changed to {t.get_status().name}"
                                        )

                                    case 'n':
                                        try:
                                            pm.set_task_status(t.task_id, Status.CANCELLED)
                                            print(f"Task #{t.task_id} status changed to {t.get_status().name}")
                                            pm.remove_task(t.task_id)
                                            print("Task removed from system.")
                                        except ValueError:
                                            print("Couldn't remove task from system.")

                                    case _:
                                        print("Invalid input. Please enter 'y' or 'n'.")
                    except ValueError:
                        print("Invalid input...")

                case 8:
                    try:
                        tid = int(input("Enter task ID to update: "))
                        t: Task = pm.get_task(tid)
                        if not t:
                            print("Not found.")

                        while True:
                            update_menu()
                            uc = int(input("What data would you like to update?\n "))

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
                                    sc = input("Please choose new status for task: ").strip()
                                    mapping = {  # map the status to a number to know what to change in the task status
                                        "1": Status.PENDING,
                                        "2": Status.SCHEDULED,
                                        "3": Status.COMPLETED,
                                        "4": Status.CANCELLED,
                                        "5": Status.DELAYED,
                                    }
                                    st = mapping.get(sc)
                                    if not st:
                                        print("Invalid status choice.")
                                        continue

                                    ok, msg = pm.set_task_status(tid, st)
                                    print(msg)
                                    break

                            print("Invalid selection. Choose 1/2/3/4 or Q.")

                    except ValueError:
                        print("Invalid input.")

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
                    items = pm.completed_tasks_as_list()
                    if not items:
                        print("No completed tasks yet")
                    else:
                        for t in items:
                            print(t)
                    continue

                case 12:
                    pm.table.display()
                    continue

                case 0:
                    print("Goodbye!")
                    exit(0)

                case _:
                    print("Invalid input...try again...")
                    continue


if __name__ == "__main__":
    main()
