from datetime import datetime
import os
import re
from tqdm import tqdm # type: ignore
from github import Github, InputGitTreeElement
from github.Repository import Repository
from github.GitTree import GitTree

def upload_directory(repository: Repository, local_dir: str, branch: str, commit_message: str):
    tree_elements = []
    local_paths: set[str] = set()
    is_update = False
    for root, _, files in os.walk(local_dir):
        for file in tqdm(files, desc=f"📁 ファイル処理中({root})"):
            local_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_file_path, local_dir)
            github_file_path = relative_path.replace("\\", "/")

            if is_excluded(github_file_path, EXCLUDE_PATTERNS):
                # print(f"🚫 除外対象: {github_file_path}")
                continue

            local_paths.add(github_file_path)

            with open(local_file_path, "r") as f:
                try:
                    content = f.read()
                except Exception as e:
                    # print(f"{f.name}:{e}")
                    continue

            is_update |= is_file_changed(repository=repository, branch=branch, github_path=github_file_path, local_content=content)

            blob = repository.create_git_blob(content, "utf-8")
            tree_element = InputGitTreeElement(path=github_file_path, mode='100644', type='blob', sha=blob.sha)
            tree_elements.append(tree_element)
            
    base = repository.get_branch(branch=branch)
    base_tree: GitTree = repository.get_git_tree(sha=base.commit.sha)

    remote_paths = {item.path for item in base_tree.tree if item.type == "blob"}

    delete_paths = remote_paths - local_paths
    for path in delete_paths:
        tree_elements.append(InputGitTreeElement(path=path, mode='100644', type='blob', sha=None))  # `sha=None`で削除

    if not (is_update or delete_paths):
        commit_message = "[変更なし]" + commit_message

    new_tree = repository.create_git_tree(tree_elements, base_tree)
    new_commit = repository.create_git_commit(commit_message, new_tree, [base.commit.commit])
    repository.get_git_ref(f"heads/{branch}").edit(sha=new_commit.sha)

def is_file_changed(repository: Repository, branch: str, github_path: str, local_content: str | bytes):
    try:
        remote_file = repository.get_contents(github_path, ref=branch)
        remote_content = remote_file.decoded_content.decode("utf-8")# type: ignore
        return remote_content != local_content
    except:
        return True
    
def is_excluded(path: str, patterns: list) -> bool:
    return any(re.match(p, path) for p in patterns)

def create_branch(repository: Repository, base_branch: str, new_branch: str):
    base_ref = repository.get_git_ref(f"heads/{base_branch}")
    try:
        repository.get_git_ref(f"heads/{new_branch}")
        print(f"⚠️ ブランチ '{new_branch}' は既に存在します")
    except:
        repository.create_git_ref(ref=f"refs/heads/{new_branch}", sha=base_ref.object.sha)
        print(f"✅ ブランチ '{new_branch}' を作成しました")

EXCLUDE_PATTERNS = [
    # r'^\.gitignore$',            # .gitignore を除外
    # r'^logs/.*\.log$',           # logs/ 以下の .log ファイルを除外
    # r'^.*\.tmp$',                # .tmp ファイルを除外
    r'^.*pin.md$',
]

local_dir = r"C:\Users"

# GitHubトークンで認証（セキュリティのため環境変数推奨）
token = ""
github = Github(login_or_token=token)

# 対象リポジトリ
repository: Repository = github.get_repo(full_name_or_id="")

# create_branch(repository=repository, base_branch="main", new_branch="develop/test")
upload_directory(
    repository=repository,
    local_dir=local_dir,
    branch="main",
    commit_message=datetime.now().strftime("%Y-%m-%d %H:%M"),
)
