from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="lambdaWalker/creditCardDetectionDS",
    repo_type="dataset",
    local_dir="dataset",
    local_dir_use_symlinks=False
)

print("Dataset fully downloaded.")