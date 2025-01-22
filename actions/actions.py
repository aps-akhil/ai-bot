from rasa_sdk import Action
from rasa_sdk.executor import CollectingDispatcher
import requests
import asyncio

# Global variable to store the run ID (for simplicity; use a persistent store for production)
pipeline_run_id = None

class ActionTriggerPipeline(Action):
    def name(self) -> str:
        return "action_trigger_pipeline"

    async def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        global pipeline_run_id  # Use global to store run ID (temporary for demonstration)

        # Azure DevOps details
        organization = "nbs0909"
        project = "Microservices"
        pipeline_id = "4"
        personal_access_token = (
            "OjNBNzVkQkpFeUtGQjJZQ2tHMDVra2pXdGVYV0ZpQlJMd3htRVhSd0tZVjVzWUtSenVDVVFKUVFKOTlCQUFDQUFBQUFXQ0lQaEFBQVNBWkRPOEthMQ=="
        )

        # Azure DevOps API URL
        trigger_url = f"https://dev.azure.com/{organization}/{project}/_apis/pipelines/{pipeline_id}/runs?api-version=6.0-preview.1"
                    # Generate the URL to the pipeline run
        pipeline_run_url = f"https://dev.azure.com/{organization}/{project}/_build/results?buildId={pipeline_run_id}&view=results"
        headers = {
            "Authorization": f"Basic {personal_access_token}",
            "Content-Type": "application/json",
        }

        # Trigger payload for the pipeline
        payload = {
            "resources": {
                "repositories": {
                    "self": {
                        "refName": "refs/heads/master"  # Branch name
                    }
                }
            }
        }

        try:
            # Trigger the pipeline
            response = requests.post(trigger_url, json=payload, headers=headers)

            if response.status_code not in [200, 201]:
                dispatcher.utter_message(
                    f"Failed to trigger deployment pipeline. Error: {response.status_code} - {response.text}"
                )
                return []

            # Get the run ID from the response
            pipeline_run_id = response.json().get("id")
            if not pipeline_run_id:
                dispatcher.utter_message("Deployment started but failed to retrieve the run ID.")
                return []

            dispatcher.utter_message(
                f"Deployment pipeline triggered successfully! Run ID: {pipeline_run_id}. "
                # f"You will receive the email notification once the deployment run has completed"
                f"Check details here: ({pipeline_run_url})"
                # "You can check the status by asking me to check the pipeline status."
            )

        except requests.RequestException as e:
            dispatcher.utter_message(f"An error occurred: {str(e)}")

        return []

class ActionCheckPipelineStatus(Action):
    def name(self) -> str:
        return "action_check_pipeline_status"

    async def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        global pipeline_run_id

        if not pipeline_run_id:
            dispatcher.utter_message("No deployment run ID found. Please trigger the pipeline first.")
            return []

        # Azure DevOps details
        organization = "nbs0909"
        project = "Microservices"
        pipeline_id = "4"
        personal_access_token = (
            "OjNBNzVkQkpFeUtGQjJZQ2tHMDVra2pXdGVYV0ZpQlJMd3htRVhSd0tZVjVzWUtSenVDVVFKUVFKOTlCQUFDQUFBQUFXQ0lQaEFBQVNBWkRPOEthMQ=="
        )

        # Azure DevOps API URL
        status_url = f"https://dev.azure.com/{organization}/{project}/_apis/pipelines/{pipeline_id}/runs/{pipeline_run_id}?api-version=6.0-preview.1"
        headers = {
            "Authorization": f"Basic {personal_access_token}",
            "Content-Type": "application/json",
        }

        try:
            # Check the pipeline status
            status_response = requests.get(status_url, headers=headers)

            if status_response.status_code != 200:
                dispatcher.utter_message(
                    f"Error checking pipeline status: {status_response.status_code} - {status_response.text}"
                )
                return []

            status_data = status_response.json()
            status = status_data.get("state")
            result = status_data.get("result")

            # Generate the URL to the pipeline run
            pipeline_run_url = f"https://dev.azure.com/{organization}/{project}/_build/results?buildId={pipeline_run_id}&view=results"

            if status == "completed":
                if result == "succeeded":
                    dispatcher.utter_message(
                        f"Deployment completed successfully! 🎉\n"
                        f"View the details here: {pipeline_run_url}"
                    )
                else:
                    dispatcher.utter_message(
                        f"Deployment run failed with result: {result}.\n"
                        f"Check details here: ({pipeline_run_url})"
                    )
            else:
                dispatcher.utter_message(f"Deployment is in progress. Please wait... or you can check the status here : ({pipeline_run_url}) ")

        except requests.RequestException as e:
            dispatcher.utter_message(f"An error occurred: {str(e)}")

        return []
