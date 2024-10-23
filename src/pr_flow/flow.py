
from crewai.flow.flow import Flow, listen, start, or_
from .crews.code_crew import CodeCrew
from .crews.doc_crew import DocCrew
from .state import AgentState
from .utils import parse_patch, parse_line_numbers
import time
count = 0

class PRFlow(Flow[AgentState]):
    @start()
    def fetch_pr(self):
        repo = self.state.github.get_repo(f"{self.state.repo}")  
        pr = repo.get_pull(self.state.pr_number)

        self.state.pr_title = pr.title
        self.state.pr_branch = pr.head.ref  
        self.state.state = "PR_FETCHED"
        self.state.steps = 1

    @listen(fetch_pr)
    def fetch_commits(self):
        repo = self.state.github.get_repo(f"{self.state.repo}")  
        pr = repo.get_pull(self.state.pr_number)

        commits = pr.get_commits()
        self.state.commit_messages = [commit.commit.message for commit in commits]
        self.state.state = "COMMITS_FETCHED"
        self.state.steps = 2

    @listen(fetch_commits)
    def fetch_files_and_patches(self):
        self.state.doc_files = []
        self.state.code_files = []
        self.state.terraform_files = []
        self.state.config_files = []
        self.state.script_files = []
        self.state.other_files = []

        repo = self.state.github.get_repo(f"{self.state.repo}")  
        pr = repo.get_pull(self.state.pr_number)

        pr_files = list(pr.get_files())
        for file in pr_files:
            filename = file.filename
            file_ext = filename.split(".")[-1].lower() if "." in filename else filename
            try:
                content = repo.get_contents(file.filename, ref=self.state.pr_branch).decoded_content.decode("utf-8")
            except Exception:
                content = repo.get_contents(file.filename, ref="main").decoded_content.decode("utf-8")
            file_data = {
                "filename": file.filename,
                "content": content,
                "status": file.status,
                "additions": file.additions,
                "deletions": file.deletions,
                "changes": file.changes,
                "patch": file.patch,
                "hunks": parse_patch(file.patch)
            }
            file_types = self.state.file_types
            if file_ext in file_types.doc_file_types:
                self.state.doc_files.append(file_data)
            elif file_ext in file_types.code_file_types:
                self.state.code_files.append(file_data)
            elif file_ext in file_types.terraform_file_types:
                self.state.terraform_files.append(file_data)
            elif file_ext in file_types.config_file_types:
                self.state.config_files.append(file_data)
            elif file_ext in file_types.script_file_types:
                self.state.script_files.append(file_data)
            else:
                self.state.other_files.append(file_data)
        
        print(self.state.code_files[0])
        self.state.state = "FILES_FETCHED"
        self.state.steps = 3    

    @listen(fetch_files_and_patches)
    async def code_review_crew(self):
        print('crc-executed')
        code_crew = CodeCrew()
        updated_code_files = []
        print(len(self.state.code_files))
        for file in self.state.code_files:
                new_crew = code_crew.copy()
                review_result = new_crew.kickoff(inputs={'diff': file['patch']})
                print('review done for ', file['filename'])
                updated_file = {**file, 'review': str(review_result.raw)}
                updated_code_files.append(updated_file)
                time.sleep(2)
        
        self.state.code_files = updated_code_files
        print("-"*10, "code review crew", "-"*10, "\n"*4)

        print(self.state.code_files[0])
        self.state.steps = 4

    @listen(fetch_files_and_patches)
    async def doc_review_crew(self):
        doc_crew = DocCrew()
        updated_doc_files = []
        for file in self.state.doc_files:
                new_crew = doc_crew.copy()
                review_result = new_crew.kickoff(inputs={'diff': file['patch']})
                print('review done for ', file['filename'])
                updated_file = {**file, 'review': str(review_result.raw)}
                updated_doc_files.append(updated_file)
                time.sleep(2)
        
        self.state.doc_files = updated_doc_files
        print("-"*10, "doc review crew", "-"*10, "\n"*4)
        print(self.state.doc_files[0])
        self.state.steps = 5

    @listen(or_(code_review_crew, doc_review_crew))
    def summary_crew(self):
        print('sum-executed')
        global count
        count += 1
        if count == 2:
            if len(self.state.code_files) > 0:
                for file in self.state.code_files:
                    filename = file['filename']
                    reviw = file['review']
                    ln_numbr = parse_line_numbers(file['patch'])
                    self.git_comment(filename, reviw, ln_numbr)

            if len(self.state.doc_files) > 0:
                for doc_file in self.state.doc_files:
                    filename = doc_file['filename']
                    reviw = doc_file['review']
                    ln_numbr = parse_line_numbers(doc_file['patch'])
                    self.git_comment(filename, reviw, ln_numbr)
        print(f"Documeent review: {self.state.doc_files[0]}")
        self.state.state = "SUMMARY_DONE"
        self.state.steps = 6

    def git_comment(self, filename, reviw, ln_numbr):
        repo = self.state.github.get_repo(f"{self.state.repo}")
        pr = repo.get_pull(self.state.pr_number)

        # Step 3: Get the latest commit
        commit_id = pr.head.sha  # Get the latest commit SHA
        commit = repo.get_commit(commit_id)
        print(f"Type of the ln_numbr: {type(ln_numbr)} and ln_numbr: {ln_numbr}")

        # Step 4: Comment on the first line of the diff
        pr.create_review_comment(
            body=reviw,
            commit=commit,
            path=filename,  # The file path in the pull request
            line=ln_numbr  # The first line of the diff
        )

async def run_flow():
    """
    Run the flow.
    """
    pr_flow = PRFlow()
    await pr_flow.kickoff()

async def plot_flow():
    """
    Plot the flow.
    """
    pr_flow = PRFlow()
    pr_flow.plot()
