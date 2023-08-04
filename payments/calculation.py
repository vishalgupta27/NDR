from accounts.models import *

def reward_calculation(amountInPoints, user_id ):
    print(amountInPoints)
    points = int(amountInPoints * float(1.5) / 100)
    user = User.objects.get(account_id = user_id)
    # Get User and save their rewards
    if user:
        print(points, "poniysjgfdfghdkh")
        avl_points = float(user.reward_points)
        if avl_points is None:
            print(avl_points,"available point")
            user.reward_points = float(points)
            user.save()
            return True
        user.reward_points = float(avl_points) + float(points)
        user.save()
        return True
    return False