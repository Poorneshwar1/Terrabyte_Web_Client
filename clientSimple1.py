import threading
import asyncio
import datetime
from dataclasses import dataclass, field
from typing import List
from clientSimple import send_req, API_URL, logger, traceback, prezipped_download, logging, get_files, USER_URL

def download_cmd(query_data=None, download_dir=None, **kwargs):
    # Send Request
    query_data["sample_size"] = 20
    data = send_req(
        method="POST",
        endpoint=API_URL,
        url="prepare",
        req_data=query_data,
        parameters=None
    )
    ack_download_data = []

    # Process response data
    if "error" not in data.keys():
        if data["archived"] is False:
            try:
                download_thread = DownloadThread(
                    [x for x in range(data["parts"])],
                    data["job_id"],
                    download_dir
                )
                download_thread.join()  # Wait for the download thread to finish
                ack_download_data = download_thread.ack_download_data
            except Exception as e:
                logger.error("Unable to download files.")
                logger.error(type(e))
                logger.error(traceback.format_exc())
        elif data["archived"] is True:
            try:
                logger.info("Downloading prezipped files")
                asyncio.run(
                    prezipped_download(
                        data["parts"],
                        archive_name=data["archive_name"],
                        download_dir=download_dir
                    )
                )
            except Exception as e:
                logger.error("Unable to download files.")
                logger.error(type(e))
                logger.error(traceback.format_exc())

    return ack_download_data  # Return the data of ack_download


@dataclass(eq=False)
class DownloadThread(threading.Thread):
    part_numbers: List[int] = field(default_factory=list)
    job_id: str = ""
    directory: str = ""
    ack_download_data: List[dict] = field(default_factory=list)

    def __post_init__(self):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger("Client.DLThread")
        self.logger.setLevel(logging.DEBUG)

        self.start()
        self.total_wait_time_on_server = 0.0

    def run(self):
        self.logger.info(f"Starting Download Thread for job {self.job_id}")
        for part in self.part_numbers:
            self.logger.info(f"Getting part {part}")
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            success, time_slept = loop.run_until_complete(
                get_files(part, self.job_id, self.directory)
            )
            self.logger.info(f"Download successful: {success}. "
                            f"Time waited on server: {time_slept}")
            self.total_wait_time_on_server += time_slept
            parameters = {
                "job_id": self.job_id,
                "part_number": part,
                "final_part": (part == len(self.part_numbers) - 1)
            }
            ack_data = send_req(
                method="GET",
                endpoint=API_URL,
                url="ack_download",
                req_data=None,
                parameters=parameters
            )
            self.ack_download_data.append(ack_data)  # Collect ack_download data

        self.logger.info(f"Download Thread for {self.job_id} FINISHED")
        self.logger.info("We waited {0} on server".format(
            self.total_wait_time_on_server)
        )



req_data = {
                'eagli_parameters.start_date': datetime.datetime(2020,4,17),
                'eagli_parameters.end_date':  datetime.datetime(2024,7,12),
                'eagli_parameters.min_age': 0,
                'eagli_parameters.max_age': 1000,
                'eagli_parameters.plants': 'Canola',
                'eagli_parameters.plant_id': '',
                'eagli_parameters.min_res': 1500,
                'eagli_parameters.max_res': 4000,
                'eagli_parameters.single_plant_output': True,
                'eagli_parameters.multiple_plant_output': False,
                'eagli_parameters.bounding_box_output': False,
                'eagli_parameters.json_output': True,
                'eagli_parameters.archive_selection': '',
                'eagli_parameters.perspectives': 'Any',
                'eagli_parameters.custom_query_string': '',
                'field_parameters.start_date': datetime.datetime.now(),
                'field_parameters.end_date':  datetime.datetime.now(),
                'field_parameters.plants': '',
                'field_parameters.archive_selection': '',
                'field_parameters.custom_query_string': '',
                'dataset': 'combined_images',
                'sample_size': 5
            }



    



# dir = "downloadedImages"
# data = download_cmd(query_data=req_data,download_dir=dir)

# print("the data returned from server is : ")
# print(data.keys())
# print("the image is saved as : ",type(data["file_list"]))
# print("the image is saved as : ",data["file_list"][0])