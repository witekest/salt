"""
    :codeauthor: Jayesh Kariya <jayeshk@saltstack.com>
"""


import logging
import os

import salt.modules.dpkg_lowpkg as dpkg
from tests.support.mixins import LoaderModuleMockMixin
from tests.support.mock import MagicMock, patch
from tests.support.unit import TestCase

DPKG_ERROR_MSG = """dpkg-query: package 'httpd' is not installed
Use dpkg --contents (= dpkg-deb --contents) to list archive files contents.
"""

DPKG_L_OUTPUT = {
    "hostname": """\
/.
/bin
/bin/hostname
/usr
/usr/share
/usr/share/doc
/usr/share/doc/hostname
/usr/share/doc/hostname/changelog.gz
/usr/share/doc/hostname/copyright
/usr/share/man
/usr/share/man/man1
/usr/share/man/man1/hostname.1.gz
/bin/dnsdomainname
/bin/domainname
/bin/nisdomainname
/bin/ypdomainname
/usr/share/man/man1/dnsdomainname.1.gz
/usr/share/man/man1/domainname.1.gz
/usr/share/man/man1/nisdomainname.1.gz
/usr/share/man/man1/ypdomainname.1.gz
"""
}


class DpkgTestCase(TestCase, LoaderModuleMockMixin):
    """
    Test cases for salt.modules.dpkg
    """

    def setUp(self):
        dpkg_lowpkg_logger = logging.getLogger("salt.modules.dpkg_lowpkg")
        self.level = dpkg_lowpkg_logger.level
        dpkg_lowpkg_logger.setLevel(logging.FATAL)

    def tearDown(self):
        logging.getLogger("salt.modules.dpkg_lowpkg").setLevel(self.level)

    def dpkg_L_side_effect(self, cmd, **kwargs):
        self.assertEqual(cmd[:2], ["dpkg", "-L"])
        package = cmd[2]
        return DPKG_L_OUTPUT[package]

    dselect_pkg = {
        "emacs": {
            "priority": "optional",
            "filename": "pool/main/e/emacs-defaults/emacs_46.1_all.deb",
            "description": "GNU Emacs editor (metapackage)",
            "md5sum": "766eb2cee55ba0122dac64c4cea04445",
            "sha256": "d172289b9a1608820eddad85c7ffc15f346a6e755c3120de0f64739c4bbc44ce",
            "description-md5": "21fb7da111336097a2378959f6d6e6a8",
            "bugs": "https://bugs.launchpad.net/springfield/+filebug",
            "depends": "emacs24 | emacs24-lucid | emacs24-nox",
            "origin": "Simpsons",
            "version": "46.1",
            "task": "ubuntu-usb, edubuntu-usb",
            "original-maintainer": "Homer Simpson <homer@springfield.org>",
            "package": "emacs",
            "architecture": "all",
            "size": "1692",
            "sha1": "9271bcec53c1f7373902b1e594d9fc0359616407",
            "source": "emacs-defaults",
            "maintainer": "Simpsons Developers <simpsons-devel-discuss@lists.springfield.org>",
            "supported": "9m",
            "section": "editors",
            "installed-size": "25",
        }
    }

    pkgs_info = [
        {
            "version": "46.1",
            "arch": "all",
            "build_date": "2014-08-07T16:51:48Z",
            "install_date_time_t": 1481745778,
            "section": "editors",
            "description": "GNU Emacs editor (metapackage)\n GNU Emacs is the extensible "
            "self-documenting text editor.\n This is a metapackage that will always "
            "depend on the latest\n recommended Emacs release.\n",
            "package": "emacs",
            "source": "emacs-defaults",
            "maintainer": "Simpsons Developers <simpsons-devel-discuss@lists.springfield.org>",
            "build_date_time_t": 1407430308,
            "installed_size": "25",
            "install_date": "2016-12-14T20:02:58Z",
        }
    ]

    def setup_loader_modules(self):
        return {dpkg: {}}

    # 'unpurge' function tests: 2

    def test_unpurge(self):
        """
        Test if it change package selection for each package
        specified to 'install'
        """
        mock = MagicMock(return_value=[])
        with patch.dict(dpkg.__salt__, {"pkg.list_pkgs": mock, "cmd.run": mock}):
            self.assertDictEqual(dpkg.unpurge("curl"), {})

    def test_unpurge_empty_package(self):
        """
        Test if it change package selection for each package
        specified to 'install'
        """
        self.assertDictEqual(dpkg.unpurge(), {})

    # 'list_pkgs' function tests: 1

    def test_list_pkgs(self):
        """
        Test if it lists the packages currently installed
        """
        mock = MagicMock(
            return_value={
                "retcode": 0,
                "stderr": "",
                "stdout": "installed\thostname\t3.21",
            }
        )
        with patch.dict(dpkg.__salt__, {"cmd.run_all": mock}):
            self.assertDictEqual(dpkg.list_pkgs("hostname"), {"hostname": "3.21"})

        mock = MagicMock(
            return_value={
                "retcode": 1,
                "stderr": "dpkg-query: no packages found matching httpd",
                "stdout": "",
            }
        )
        with patch.dict(dpkg.__salt__, {"cmd.run_all": mock}):
            self.assertEqual(
                dpkg.list_pkgs("httpd"),
                "Error:  dpkg-query: no packages found matching httpd",
            )

    # 'file_list' function tests: 1

    def test_file_list(self):
        """
        Test if it lists the files that belong to a package.
        """
        dpkg_query_mock = MagicMock(
            return_value={"retcode": 0, "stderr": "", "stdout": "installed\thostname"}
        )
        dpkg_L_mock = MagicMock(side_effect=self.dpkg_L_side_effect)
        with patch.dict(
            dpkg.__salt__, {"cmd.run_all": dpkg_query_mock, "cmd.run": dpkg_L_mock}
        ):
            self.assertDictEqual(
                dpkg.file_list("hostname"),
                {
                    "errors": [],
                    "files": [
                        "/.",
                        "/bin",
                        "/bin/dnsdomainname",
                        "/bin/domainname",
                        "/bin/hostname",
                        "/bin/nisdomainname",
                        "/bin/ypdomainname",
                        "/usr",
                        "/usr/share",
                        "/usr/share/doc",
                        "/usr/share/doc/hostname",
                        "/usr/share/doc/hostname/changelog.gz",
                        "/usr/share/doc/hostname/copyright",
                        "/usr/share/man",
                        "/usr/share/man/man1",
                        "/usr/share/man/man1/dnsdomainname.1.gz",
                        "/usr/share/man/man1/domainname.1.gz",
                        "/usr/share/man/man1/hostname.1.gz",
                        "/usr/share/man/man1/nisdomainname.1.gz",
                        "/usr/share/man/man1/ypdomainname.1.gz",
                    ],
                },
            )

        mock = MagicMock(
            return_value={"retcode": 1, "stderr": DPKG_ERROR_MSG, "stdout": ""}
        )
        with patch.dict(dpkg.__salt__, {"cmd.run_all": mock}):
            self.assertEqual(dpkg.file_list("httpd"), "Error:  " + DPKG_ERROR_MSG)

    # 'file_dict' function tests: 1

    def test_file_dict(self):
        """
        Test if it lists the files that belong to a package, grouped by package
        """
        dpkg_query_mock = MagicMock(
            return_value={"retcode": 0, "stderr": "", "stdout": "installed\thostname"}
        )
        dpkg_L_mock = MagicMock(side_effect=self.dpkg_L_side_effect)
        with patch.dict(
            dpkg.__salt__, {"cmd.run_all": dpkg_query_mock, "cmd.run": dpkg_L_mock}
        ):
            expected = {
                "errors": [],
                "packages": {
                    "hostname": [
                        "/.",
                        "/bin",
                        "/bin/hostname",
                        "/usr",
                        "/usr/share",
                        "/usr/share/doc",
                        "/usr/share/doc/hostname",
                        "/usr/share/doc/hostname/changelog.gz",
                        "/usr/share/doc/hostname/copyright",
                        "/usr/share/man",
                        "/usr/share/man/man1",
                        "/usr/share/man/man1/hostname.1.gz",
                        "/bin/dnsdomainname",
                        "/bin/domainname",
                        "/bin/nisdomainname",
                        "/bin/ypdomainname",
                        "/usr/share/man/man1/dnsdomainname.1.gz",
                        "/usr/share/man/man1/domainname.1.gz",
                        "/usr/share/man/man1/nisdomainname.1.gz",
                        "/usr/share/man/man1/ypdomainname.1.gz",
                    ]
                },
            }
            self.assertDictEqual(dpkg.file_dict("hostname"), expected)

        mock = MagicMock(
            return_value={"retcode": 1, "stderr": DPKG_ERROR_MSG, "stdout": ""}
        )
        with patch.dict(dpkg.__salt__, {"cmd.run_all": mock}):
            self.assertEqual(dpkg.file_dict("httpd"), "Error:  " + DPKG_ERROR_MSG)

    def test_bin_pkg_info_spaces(self):
        """
        Test the bin_pkg_info function
        """
        file_proto_mock = MagicMock(return_value=True)
        with patch.dict(dpkg.__salt__, {"config.valid_fileproto": file_proto_mock}):
            cache_mock = MagicMock(return_value="/path/to/some/package.deb")
            with patch.dict(dpkg.__salt__, {"cp.cache_file": cache_mock}):
                dpkg_info_mock = MagicMock(
                    return_value={
                        "retcode": 0,
                        "stderr": "",
                        "stdout": (
                            " new Debian package, version 2.0\n"
                            " size 123456 bytes: control archive: 4029  bytes.\n"
                            " Package          : package_name\n"
                            " Version          : 1.0\n"
                            " Section          : section_name\n"
                            " Priority         : priority\n"
                            " Architecture     : all\n"
                            " Description      : some package\n"
                        ),
                    }
                )
                with patch.dict(dpkg.__salt__, {"cmd.run_all": dpkg_info_mock}):
                    self.assertEqual(
                        dpkg.bin_pkg_info("package.deb")["name"], "package_name"
                    )

    def test_bin_pkg_info_no_spaces(self):
        """
        Test the bin_pkg_info function
        """
        file_proto_mock = MagicMock(return_value=True)
        with patch.dict(dpkg.__salt__, {"config.valid_fileproto": file_proto_mock}):
            cache_mock = MagicMock(return_value="/path/to/some/package.deb")
            with patch.dict(dpkg.__salt__, {"cp.cache_file": cache_mock}):
                dpkg_info_mock = MagicMock(
                    return_value={
                        "retcode": 0,
                        "stderr": "",
                        "stdout": (
                            " new Debian package, version 2.0\n"
                            " size 123456 bytes: control archive: 4029  bytes.\n"
                            " Package: package_name\n"
                            " Version: 1.0\n"
                            " Section: section_name\n"
                            " Priority: priority\n"
                            " Architecture: all\n"
                            " Description: some package\n"
                        ),
                    }
                )
                with patch.dict(dpkg.__salt__, {"cmd.run_all": dpkg_info_mock}):
                    self.assertEqual(
                        dpkg.bin_pkg_info("package.deb")["name"], "package_name"
                    )

    @patch(
        "salt.modules.dpkg_lowpkg._get_pkg_ds_avail",
        MagicMock(return_value=dselect_pkg),
    )
    @patch("salt.modules.dpkg_lowpkg._get_pkg_info", MagicMock(return_value=pkgs_info))
    @patch(
        "salt.modules.dpkg_lowpkg._get_pkg_license", MagicMock(return_value="BSD v3")
    )
    def test_info(self):
        """
        Test info
        :return:
        """
        ret = dpkg.info("emacs")

        assert isinstance(ret, dict)
        assert len(ret.keys()) == 1
        assert "emacs" in ret

        pkg_data = ret["emacs"]

        assert isinstance(pkg_data, dict)
        for pkg_section in [
            "section",
            "architecture",
            "original-maintainer",
            "maintainer",
            "package",
            "installed-size",
            "build_date_time_t",
            "sha256",
            "origin",
            "build_date",
            "size",
            "source",
            "version",
            "install_date_time_t",
            "license",
            "priority",
            "description",
            "md5sum",
            "supported",
            "filename",
            "sha1",
            "install_date",
            "arch",
        ]:
            assert pkg_section in pkg_data

        assert pkg_data["section"] == "editors"
        assert (
            pkg_data["maintainer"]
            == "Simpsons Developers <simpsons-devel-discuss@lists.springfield.org>"
        )
        assert pkg_data["license"] == "BSD v3"

    @patch(
        "salt.modules.dpkg_lowpkg._get_pkg_ds_avail",
        MagicMock(return_value=dselect_pkg),
    )
    @patch("salt.modules.dpkg_lowpkg._get_pkg_info", MagicMock(return_value=pkgs_info))
    @patch(
        "salt.modules.dpkg_lowpkg._get_pkg_license", MagicMock(return_value="BSD v3")
    )
    def test_info_attr(self):
        """
        Test info with 'attr' parameter
        :return:
        """
        ret = dpkg.info("emacs", attr="arch,license,version")
        assert isinstance(ret, dict)
        assert "emacs" in ret
        for attr in ["arch", "license", "version"]:
            assert attr in ret["emacs"]

        assert ret["emacs"]["arch"] == "all"
        assert ret["emacs"]["license"] == "BSD v3"
        assert ret["emacs"]["version"] == "46.1"
