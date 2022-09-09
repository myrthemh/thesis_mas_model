from .model import SocialNetwork

import os
print("hoi")
session_id = "test"
model_dir = os.path.join('results', session_id)
model_path = os.path.join(model_dir, f"model_{session_id}.pkl")

model_test = SocialNetwork()
model_test.run_until_stable()
print(
    f"Model {session_id} converged in {model_test.schedule.steps} steps")