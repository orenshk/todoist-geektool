import todoist
import argparse
from datetime import datetime
from dateutil import parser as date_parser, tz

# every hour refresh the entire task list, because why not.
FULL_REFRESH_PERIOD = 3600


def main(api_token):
    api = todoist.TodoistAPI(api_token)
    api.sync_token = '*'
    today = datetime.today().day
    api.sync()

    # geektool's shell script doesn't seem to do all 16 colours?
    priority_colors = {
        1: '\033[1;31m',  # bold red
        2: '\033[1;33m',  # bold yellow
        3: '\033[0;35m',  # pink (don't clash with yello)
        4: '\033[0m'  # no color
    }
    task_str_template = '{}(P{})\033[0m {}'

    today_tasks = []
    for task in api.state['items']:
        if task['checked'] == 0 and task['due_date_utc'] is not None:
            # get task due date as local date.
            task_date = date_parser.parse(task['due_date_utc']).astimezone(tz.tzlocal())
            if task_date.day == today:
                # for some reason todoist filps the priorities (4--> 1, ... 1 --> 4).
                task['priority'] = 4 - task['priority'] + 1
                today_tasks.append(task)

    today_tasks.sort(key=lambda task: (task['priority'], task['day_order']))
    print("Today")
    for task in today_tasks:
        p = task['priority']
        p_color = priority_colors[p]
        print(task_str_template.format(p_color, p, task['content']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser('todoist-for-geektool')
    parser.add_argument('api_token')
    args = parser.parse_args()
    main(args.api_token)
