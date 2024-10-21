from typing import List, Union, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from github import Github
import os


# Define a Pydantic model for Hunk
class Hunk(BaseModel):
    additions: List[str]
    deletions: List[str]


# Define a Pydantic model for FileTypes
class FileTypes(BaseModel):
    doc_file_types: List[str] = ["md"]
    code_file_types: List[str] = ["go"]
    terraform_file_types: List[str] = ["tf"]
    config_file_types: List[str] = ["yaml", "json"]
    script_file_types: List[str] = ["sh"]


# Define a Pydantic model for AgentState
class AgentState(BaseModel):
    steps: int = 0  # Provide a default value if it can start from 0
    github: Github = Field(default_factory=lambda: Github(os.environ['PAT_TOKEN']))  # Use a default factory
    owner: str = os.environ['REPOSITORY_OWNER']
    repo: str = os.environ['REPOSITORY_NAME']
    pr_number: int = int(os.environ['PR_NUMBER'])
    pr_title: Optional[str] = None
    pr_branch: Optional[str] = None
    commit_messages: List[str] = Field(default_factory=list)

    doc_files: List[Dict[str, Union[str, int, List[str], List[Hunk]]]] = Field(default_factory=list)
    code_files: List[Dict[str, Union[str, int, List[str], List[Hunk]]]] = Field(default_factory=list)
    terraform_files: List[Dict[str, Union[str, int, List[str], List[Hunk]]]] = Field(default_factory=list)
    config_files: List[Dict[str, Union[str, int, List[str], List[Hunk]]]] = Field(default_factory=list)
    script_files: List[Dict[str, Union[str, int, List[str], List[Hunk]]]] = Field(default_factory=list)
    other_files: List[Dict[str, Union[str, int, List[str], List[Hunk]]]] = Field(default_factory=list)

    file_types: FileTypes = Field(default_factory=FileTypes)  # Ensure this field is initialized
    state: str = "initialized"  # Provide a default state value

    model_config = ConfigDict(arbitrary_types_allowed=True)
