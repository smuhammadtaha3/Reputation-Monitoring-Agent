# from huggingface_hub import login, upload_folder

# # (optional) Login with your Hugging Face credentials
# login()

# # Push your model files
# upload_folder(folder_path=".", repo_id="TAHA4/reputation-sentiment-model", repo_type="model")


# notebooks/ mein ye run karo
import os

from huggingface_hub import HfApi

api = HfApi()
api.upload_folder(
    folder_path="../models/fine_tuned_model",
    repo_id="TAHA4/reputation-sentiment-model",
    repo_type="model",
    token=os.environ.get("HF_TOKEN") # huggingface.co/settings/tokens
)