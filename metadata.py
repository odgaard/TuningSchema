import subprocess
import json
import jc
import xmltodict

from batbench.result.zenodo import Zenodo

class Metadata:
    """
    A class that provides methods to retrieve metadata about the environment and hardware.
    """
    @staticmethod
    def get_metadata():
        metadata = {}
        metadata["zenodo"] = Zenodo.get_zenodo_metadata()
        metadata["environment"] = Metadata.get_environment_metadata()
        metadata["hardware"] = Metadata.get_hardware_metadata()
        return metadata

    @staticmethod
    def get_environment_metadata():
        env_metadata = {}
        env_metadata["requirements"] = Metadata.save_requirements()
        env_metadata["lsb_release"] = Metadata.get_lsb_release()
        env_metadata["hostname"] = Metadata.get_hostname()
        return env_metadata

    @staticmethod
    def get_hardware_metadata():
        """
        Returns metadata about the hardware.
        """
        metadata = {}
        nvidia_smi_out = subprocess.run(["nvidia-smi", "--query", "-x"],
                                        capture_output=True, check=True)
        output = xmltodict.parse(nvidia_smi_out.stdout)
        del output["nvidia_smi_log"]["gpu"]["processes"]
        metadata["nvidia_query"] = output
        metadata["lshw"] = Metadata.get_lshw()
        lscpu_out = subprocess.run(["lscpu", "--json"], capture_output=True, check=True)
        metadata["lscpu"] = json.loads(lscpu_out.stdout)
        proc_out = subprocess.run(["cat", "/proc/meminfo"], capture_output=True, check=True)
        metadata["meminfo"] = jc.parse('proc_meminfo', proc_out.stdout.decode("utf-8"))
        metadata["lsblk"] = Metadata.get_lsblk()
        return metadata

    @staticmethod
    def save_requirements():
        with open("requirements.txt", 'r', encoding='utf-8') as file:
            requirements_list = [line.strip() for line in file.readlines()]
        return requirements_list

    @staticmethod
    def get_lsblk():
        try:
            lsblk_out = subprocess.run(["lsblk", "-a"], capture_output=True, check=True)
            return jc.parse('lsblk', lsblk_out.stdout.decode("utf-8"))
        except subprocess.CalledProcessError:
            print("lsblk command failed or not found.")
            return {}
        except ValueError:
            print("Parser does not exist for 'lsblk'.")
            return {}
        except jc.exceptions.ParseError:
            print("Failed to parse the output of 'lsblk'.")
            return {}


    @staticmethod
    def get_lsb_release():
        lsb_release_out = subprocess.run(["lsb_release", "-a"], capture_output=True, check=True)
        res = {}
        for line in lsb_release_out.stdout.decode("utf-8").split("\n"):
            line_list = line.split("\t")
            if line_list[0] == "" or line_list[-1] == "":
                continue
            res[line_list[0]] = line_list[-1]
        return res

    @staticmethod
    def get_hostname():
        return subprocess.run(["hostname"], capture_output=True,
                              check=True).stdout.decode("utf-8").strip()


    @staticmethod
    def get_lshw():
        try:
            lshw_out = subprocess.run(["lshw", "-json", "-sanitize"],
                                      capture_output=True, check=True)
            return json.loads(lshw_out.stdout)
        except subprocess.CalledProcessError:
            print("lshw command failed or not found.")
            return {}
        except json.JSONDecodeError:
            print("Failed to decode JSON from lshw output.")
            return {}
