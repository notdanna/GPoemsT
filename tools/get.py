from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="unsloth/Llama-3.2-3B-Instruct",
    local_dir="./mi_modelo_privado",
    local_dir_use_symlinks=False
)
