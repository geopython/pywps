# coding=utf-8
import os
import unittest
import pywps.configuration
from tempfile import TemporaryDirectory


class TestBase(unittest.TestCase):

    def setUp(self) -> None:
        # Do not use load_configuration() that will load system configuration
        # files such as /etc/pywps.cfg
        pywps.configuration.load_hardcoded_configuration()

        # Ensure all data goes into ontime temporary directory
        self.tmpdir = TemporaryDirectory(prefix="pywps_test_")

        # shortcut
        set = pywps.configuration.CONFIG.set

        set('server', 'temp_path', f"{self.tmpdir.name}/temp_path")
        set('server', 'outputpath', f"{self.tmpdir.name}/outputpath")
        set('server', 'workdir', f"{self.tmpdir.name}/workdir")

        set('logging', 'level', 'DEBUG')
        set('logging', 'file', f"{self.tmpdir.name}/logging-file.log")
        set("logging", "database", f"sqlite:///{self.tmpdir.name}/test-pywps-logs.sqlite3")

        set('processing', 'path', f"{self.tmpdir.name}/processing_path")

        os.mkdir(f"{self.tmpdir.name}/temp_path")
        os.mkdir(f"{self.tmpdir.name}/outputpath")
        os.mkdir(f"{self.tmpdir.name}/workdir")
        os.mkdir(f"{self.tmpdir.name}/processing_path")

    def tearDown(self) -> None:
        self.tmpdir.cleanup()
