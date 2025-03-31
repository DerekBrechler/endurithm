# fueling_engine.py

# -----------------------------
# Sports Profile Definitions
# -----------------------------
sports_profiles = {
    'marathon_running': {
        'type': 'endurance',
        'carb_ratio': 60,
        'protein_ratio': 20,
        'fat_ratio': 20,
        'priority_goal': 'maintain'
    },
    'track_and_field_distance': {
        'type': 'endurance',
        'carb_ratio': 60,
        'protein_ratio': 20,
        'fat_ratio': 20,
        'priority_goal': 'maintain'
    },
    'track_and_field_power': {
        'type': 'power',
        'carb_ratio': 45,
        'protein_ratio': 30,
        'fat_ratio': 25,
        'priority_goal': 'maintain'
    },
    'track_and_field_mid': {
        'type': 'hybrid',
        'carb_ratio': 50,
        'protein_ratio': 25,
        'fat_ratio': 25,
        'priority_goal': 'maintain'
    }
}

# -----------------------------
# Goal Logic Functions
# -----------------------------
def sport_check(sport):
    if sport in ['marathon_running', 'track_and_field']:
        print(f'You have selected {sport} for sport use.')
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
        'maintain': True,
        'bulking': True
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
    if goal_status.get(goal.lower()):
        print('Goal is validated. You may continue with the selected goal.')
        return True
    else:
        print(f'{goal} is not validated. You may choose a new goal.')
        return False

def goal_confirmation(is_valid, goal):
    if is_valid:
        print(f'Your selected goal is {goal}.')
        return goal.lower()
    else:
        print(f'{goal} is not allowed. Defaulting to maintain.')
        return 'maintain'

def goal_logic_run(user, age, height, weight, goal, sport):
    sport_check(sport)
    defining_cutting(weight)
    goal_status = finding_nutrition_goal(user, age, height, weight, goal, sport)
    is_valid = goal_validation(goal, goal_status)
    final_goal = goal_confirmation(is_valid, goal)
    return final_goal

# -----------------------------
# Macro Recommender
# -----------------------------
def get_replenish_ratio_by_goal(goal):
    goal = goal.lower()
    return {
        'maintain': 1.0,
        'cutting': 0.75,
        'bulking': 1.15
    }.get(goal, 1.0)

def recommend_macros(calories_burned, sport_profile, goal='maintain'):
    if sport_profile not in sports_profiles:
        raise ValueError(f"Unknown sport profile: {sport_profile}")

    profile = sports_profiles[sport_profile]
    replenish_ratio = get_replenish_ratio_by_goal(goal)
    total_replenish_kcal = calories_burned * replenish_ratio

    # Extract ratios
    carb_pct = profile['carb_ratio']
    protein_pct = profile['protein_ratio']
    fat_pct = profile['fat_ratio']

    # Calculate kcal from each macro
    carb_kcal = total_replenish_kcal * (carb_pct / 100)
    protein_kcal = total_replenish_kcal * (protein_pct / 100)
    fat_kcal = total_replenish_kcal * (fat_pct / 100)

    # Convert to grams (4 kcal/g for carbs & protein, 9 kcal/g for fat)
    return {
        'total_kcal_to_replenish': round(total_replenish_kcal, 1),
        'carbs_g': round(carb_kcal / 4, 1),
        'protein_g': round(protein_kcal / 4, 1),
        'fat_g': round(fat_kcal / 9, 1),
        'carbs_kcal': round(carb_kcal, 1),
        'protein_kcal': round(protein_kcal, 1),
        'fat_kcal': round(fat_kcal, 1),
        'profile_type': profile['type'],
        'goal': goal
    }
