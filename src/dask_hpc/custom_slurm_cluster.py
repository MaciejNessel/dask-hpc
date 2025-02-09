import getpass
import os
import socket

from dask_jobqueue import SLURMCluster

from dask.distributed import Client

SCRATCH = os.environ.get("SCRATCH")


class CustomSLURMCluster(SLURMCluster):
    """
    CustomSLURMCluster is a custom Dask SLURMCluster setup for the HPC environment.

    This class extends the SLURMCluster to configure a Dask cluster on the HPC system
    with specific settings and job submission commands.

    Attributes:
        account (str): The account name for SLURM job submission.
        project_dir (str): The directory of the project to be copied to the MEMFS.
                           It is required that the project_dir contains a pyproject.toml file with the dependencies.
        cores (int): Number of cores per job.
        processes (int): Number of processes per job.
        memory (str): Amount of memory per job.
        login_node (str): The login node to submit jobs from.
        queue (str): The SLURM queue to submit jobs to.
        walltime (str): The walltime for each job. Default is "02:00:00".
        local_directory (str): Local directory for Dask temporary files.
        log_directory (str): Directory for Dask log files.
        silence_logs (str): Logging level for Dask. Default is "info".
        **kwargs: Additional keyword arguments passed to the SLURMCluster constructor.

    Methods:
        client: Returns a Dask Client connected to the cluster.
        get_dashboard_info: Prints instructions to tunnel to the Dask dashboard.
    """

    def __init__(
        self,
        account: str,
        project_dir: str,
        cores=1,
        processes=1,
        memory="10GB",
        login_node="ares.cyfronet.pl",
        queue="plgrid",
        walltime="02:00:00",
        local_directory=f"{SCRATCH}/dask_tmp",
        log_directory=f"{SCRATCH}/dask_logs",
        silence_logs="info",
        **kwargs,
    ):
        # Set the submit command to use ssh to submit jobs on the login node.
        # It is required, because it is not allowed to use sbatch command on compute nodes.
        plg_user = getpass.getuser()
        self.job_cls.submit_command = f"ssh {plg_user}@{login_node} sbatch"

        # Set up Python environment with Poetry in the MEMFS.
        job_script_prologue = [
            "module load poetry/1.8.3-gcccore-12.3.0",
            "export POETRY_CONFIG_DIR=$MEMFS/poetry_config",
            "export POETRY_DATA_DIR=$MEMFS/poetry_data",
            "export POETRY_CACHE_DIR=$MEMFS/poetry_cache",
            "export POETRY_VIRTUALENVS_IN_PROJECT=false",
            f"cp -r {project_dir} $MEMFS",
            f"cd $MEMFS/{os.path.basename(project_dir)}",
            "poetry install --with=dev",
            "source $(poetry env info --path)/bin/activate",
        ]

        super().__init__(
            cores=cores,
            memory=memory,
            processes=processes,
            account=account,
            queue=queue,
            interface="ib0",
            walltime=walltime,
            local_directory=local_directory,
            log_directory=log_directory,
            silence_logs=silence_logs,
            python="python",
            job_extra_directives=["-C memfs"],
            job_script_prologue=job_script_prologue,
            **kwargs,
        )

    @property
    def client(self):
        return Client(self)

    def get_dashboard_info(self):
        host = self.client.run_on_scheduler(socket.gethostname)
        port = self.client.scheduler_info()["services"]["dashboard"]
        login_node_address = f"{getpass.getuser()}@ares.cyfronet.pl"

        print("To tunnel to the Dask dashboard, run the following command on your local machine:")
        print(f"ssh -L {port}:{host}:{port} {login_node_address}")
        print(f"Then open http://localhost:{port} to view the Dask dashboard.")