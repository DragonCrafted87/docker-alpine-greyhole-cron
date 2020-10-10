#!/usr/bin/python3

# System Imports
from os import getenv
from pathlib import PurePath

# 3rd Party Imports
from kubernetes import config
from kubernetes.client import Configuration
from kubernetes.client.api import core_v1_api
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream
import urllib3

# Local Imports
from python_logger import create_logger

def main():
  logger = create_logger(PurePath(__file__).stem)

  config.load_incluster_config()

  configuration = Configuration()
  configuration.verify_ssl = False
  configuration.assert_hostname = False
  urllib3.disable_warnings()
  Configuration.set_default(configuration)

  api = core_v1_api.CoreV1Api()
  label_selector = getenv('LABEL_SELECTOR','role=greyhole')
  namespace = getenv('NAMESPACE','storage')
  command_switch = getenv('COMMAND_SWITCH', '')

  k8s_response = api.list_namespaced_pod(namespace=namespace,
                                 label_selector=label_selector)

  logger.info(f'ENV Commands {label_selector} {namespace} {command_switch}')
  logger.debug(f'{k8s_response}')

  for pod in k8s_response.items:
    name = pod.metadata.name

    k8s_response = api.read_namespaced_pod(name=name,
                                   namespace=namespace)

    exec_command = [
    '/bin/sh',
    '-c']

    if command_switch.lower() == 'monthly':
      exec_command.append('greyhole --fsck --checksums')
    elif command_switch.lower() == 'weekly':
      exec_command.append('greyhole --fsck --dont-walk-metadata-store --disk-usage-report')
    elif command_switch.lower() == 'daily':
      exec_command.append('greyhole --fsck --if-conf-changed --dont-walk-metadata-store')
    else:
      exec_command.append('greyhole --process-spool --keepalive')

    k8s_response = stream(api.connect_get_namespaced_pod_exec, name, namespace,
                command=exec_command,
                stderr=True, stdin=False,
                stdout=True, tty=False)

    logger.info(f'Cleanup {name}: {k8s_response}')

  logger.info(f'Successfully executed cron job')

if __name__ == '__main__':
  main()
