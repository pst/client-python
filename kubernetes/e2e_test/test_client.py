# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import unittest
import uuid

from kubernetes.client import api_client
from kubernetes.client.apis import core_v1_api
from kubernetes.e2e_test import base


class TestClient(unittest.TestCase):
    @unittest.skipUnless(
        base.is_k8s_running(), "Kubernetes is not available")
    def test_pod_apis(self):
        client = api_client.ApiClient('http://127.0.0.1:8080/')
        api = core_v1_api.CoreV1Api(client)

        name = 'test-' + str(uuid.uuid4())
        pod_manifest = {'apiVersion': 'v1',
                        'kind': 'Pod',
                        'metadata': {'color': 'blue', 'name': name},
                        'spec': {'containers': [{'image': 'dockerfile/redis',
                                                 'name': 'redis'}]}}

        resp = api.create_namespaced_pod(body=pod_manifest,
                                         namespace='default')
        self.assertEqual(name, resp.metadata.name)
        self.assertTrue(resp.status.phase)

        resp = api.read_namespaced_pod(name=name,
                                       namespace='default')
        self.assertEqual(name, resp.metadata.name)
        self.assertTrue(resp.status.phase)

        number_of_pods = len(api.list_pod_for_all_namespaces().items)
        self.assertTrue(number_of_pods > 0)

        resp = api.delete_namespaced_pod(name=name, body={},
                                         namespace='default')

    @unittest.skipUnless(
        base.is_k8s_running(), "Kubernetes is not available")
    def test_service_apis(self):
        client = api_client.ApiClient('http://127.0.0.1:8080/')
        api = core_v1_api.CoreV1Api(client)

        name = 'frontend-' + str(uuid.uuid4())
        service_manifest = {'apiVersion': 'v1',
                            'kind': 'Service',
                            'metadata': {'labels': {'name': name},
                                         'name': name,
                                         'resourceversion': 'v1'},
                            'spec': {'ports': [{'name': 'port',
                                                'port': 80,
                                                'protocol': 'TCP',
                                                'targetPort': 80}],
                                     'selector': {'name': name}}}

        resp = api.create_namespaced_service(body=service_manifest,
                                             namespace='default')
        self.assertEqual(name, resp.metadata.name)
        self.assertTrue(resp.status)

        resp = api.read_namespaced_service(name=name,
                                           namespace='default')
        self.assertEqual(name, resp.metadata.name)
        self.assertTrue(resp.status)

        service_manifest['spec']['ports'] = [{'name': 'new',
                                              'port': 8080,
                                              'protocol': 'TCP',
                                              'targetPort': 8080}]
        resp = api.patch_namespaced_service(body=service_manifest,
                                            name=name,
                                            namespace='default')
        self.assertEqual(2, len(resp.spec.ports))
        self.assertTrue(resp.status)

        resp = api.delete_namespaced_service(name=name,
                                             namespace='default')

    @unittest.skipUnless(
        base.is_k8s_running(), "Kubernetes is not available")
    def test_replication_controller_apis(self):
        client = api_client.ApiClient('http://127.0.0.1:8080/')
        api = core_v1_api.CoreV1Api(client)

        name = 'frontend-' + str(uuid.uuid4())
        rc_manifest = {
            'apiVersion': 'v1',
            'kind': 'ReplicationController',
            'metadata': {'labels': {'name': name},
                         'name': name},
            'spec': {'replicas': 2,
                     'selector': {'name': name},
                     'template': {'metadata': {
                         'labels': {'name': name}},
                         'spec': {'containers': [{
                             'image': 'nginx',
                             'name': 'nginx',
                             'ports': [{'containerPort': 80,
                                        'protocol': 'TCP'}]}]}}}}

        resp = api.create_namespaced_replication_controller(
            body=rc_manifest, namespace='default')
        self.assertEqual(name, resp.metadata.name)
        self.assertEqual(2, resp.spec.replicas)

        resp = api.read_namespaced_replication_controller(
            name=name, namespace='default')
        self.assertEqual(name, resp.metadata.name)
        self.assertEqual(2, resp.spec.replicas)

        resp = api.delete_namespaced_replication_controller(
            name=name, body={}, namespace='default')

    @unittest.skipUnless(
        base.is_k8s_running(), "Kubernetes is not available")
    def test_configmap_apis(self):
        client = api_client.ApiClient('http://127.0.0.1:8080/')
        api = core_v1_api.CoreV1Api(client)

        name = 'test-configmap-' + str(uuid.uuid4())
        test_configmap = {
            "kind": "ConfigMap",
            "apiVersion": "v1",
            "metadata": {
                "name": name,
            },
            "data": {
                "config.json": "{\"command\":\"/usr/bin/mysqld_safe\"}",
                "frontend.cnf": "[mysqld]\nbind-address = 10.0.0.3\nport = 3306\n"
            }
        }

        resp = api.create_namespaced_config_map(
            body=test_configmap, namespace='default'
        )
        self.assertEqual(name, resp.metadata.name)

        resp = api.read_namespaced_config_map(
            name=name, namespace='default')
        self.assertEqual(name, resp.metadata.name)

        test_configmap['data']['config.json'] = "{}"
        resp = api.patch_namespaced_config_map(
            name=name, namespace='default', body=test_configmap)

        resp = api.delete_namespaced_config_map(
            name=name, body={}, namespace='default')

        resp = api.list_namespaced_config_map('kube-system', pretty=True)
        self.assertEqual([], resp.items)

    @unittest.skipUnless(
        base.is_k8s_running(), "Kubernetes is not available")
    def test_node_apis(self):
        client = api_client.ApiClient('http://127.0.0.1:8080/')
        api = core_v1_api.CoreV1Api(client)

        for item in api.list_node().items:
            node = api.read_node(name=item.metadata.name)
            self.assertTrue(len(node.metadata.labels) > 0)
            self.assertTrue(isinstance(node.metadata.labels, dict))