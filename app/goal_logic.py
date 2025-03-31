def sport_check(sport):
    if sport == 'marathon_running' or sport == 'track_and_field':
        print('You have selected ___ for sport use.')
        return True
    else:
        print('Continue')
        return False

def defining_cutting(weight):
    target = 150
    if weight < target:
        print('You do not meet the required weight to allow a healthy cut. Select a new goal.')
        return False
    else:
        print('You meet the required weight for a healthy cut, you may continue.')
        return True

def finding_nutrition_goal(user, age, height, weight, goal, sport):
    goal_status = {
        'cutting': True,
        'Maintain': True,
        'Bulking': True
    }
    if weight <= 150:
        goal_status['cutting'] = False
    if weight >= 150:
        goal_status['bulking'] = False
    if sport in ['marathon_running', 'track_and_field']:
        goal_status['bulking'] = False
    print(f"{user}'s allowed goals based on inputs: {goal_status}")
    return goal_status

def goal_validation(goal, goal_status):
    if goal_status.get(goal):
        print('Goal is validated. You may continue with the selected goal.')
        return True
    else:
        print(f'{goal} is not validated. You may choose a new goal.')
        return False

def goal_confirmation(is_valid, goal):
    if is_valid:
        print(f'Your selected goal is {goal}.')
        return goal
    else:
        print(f'{goal} is not allowed. Defaulting to maintain.')
        return 'Maintain'

def goal_logic_run(user, age, height, weight, goal, sport):
    sport_check(sport)
    defining_cutting(weight)
    goal_status = finding_nutrition_goal(user, age, height, weight, goal, sport)
    is_valid = goal_validation(goal, goal_status)
    final_goal = goal_confirmation(is_valid, goal)
    return final_goal

# Test it
print(goal_logic_run('A001', 23, 183, 160, 'cutting', 'marathon_running'))
