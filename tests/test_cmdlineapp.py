#
# Copyright (c) 2012 Andrew Pearce <andy@andy-pearce.com>
#

import cmdlineapp
import ConfigParser
import logging
import tempfile
import unittest



class SampleApplication(cmdlineapp.Application):

    version = "1.23.45"

    def __init__(self):
        self.unittest_args = None
        cmdlineapp.Application.__init__(self)
        self.parser.add_argument("--option", "-o", action="store_true",
                                 help="sample option")

    def app_main(self, args):
        self.unittest_args = args
        return 0



class TestOptions(unittest.TestCase):

    def setUp(self):
        self.app = SampleApplication()

    def tearDown(self):
        self.app = None

    def __run_app(self, *args):
        ret = self.app.main(argv=(["/path/app.py"] + list(args)))
        return (ret, self.app.unittest_args)

    def test_no_options(self):
        ret, args = self.__run_app()
        self.assertEqual(ret, 0)
        self.assertFalse(args.option)

    def test_no_config(self):
        ret, args = self.__run_app()
        self.assertEqual(self.app.config, None)

    def test_bad_option(self):
        try:
            ret, args = self.__run_app("-x")
            self.fail()
        except SystemExit, e:
            self.assertNotEqual(e.code, 0)

    def test_good_option(self):
        ret, args = self.__run_app("-o")
        self.assertEqual(ret, 0)
        self.assertTrue(args.option)

    def test_quiet(self):
        ret, args = self.__run_app("-q")
        self.assertEqual(ret, 0)
        self.assertEqual(logging.getLogger().level, logging.ERROR)

    def test_not_verbose(self):
        ret, args = self.__run_app()
        self.assertEqual(ret, 0)
        self.assertEqual(logging.getLogger().level, logging.WARNING)

    def test_verbose(self):
        ret, args = self.__run_app("-v")
        self.assertEqual(ret, 0)
        self.assertEqual(logging.getLogger().level, logging.INFO)

    def test_very_verbose(self):
        ret, args = self.__run_app("-v", "-v")
        self.assertEqual(ret, 0)
        self.assertEqual(logging.getLogger().level, logging.DEBUG)

    def test_version(self):
        try:
            ret, args = self.__run_app("-V")
            self.fail()
        except SystemExit, e:
            self.assertEqual(e.code, 0)



class SampleConfigApplication(cmdlineapp.Application):

    version = "1.23.45"
    configfile = "REPLACEME"

    def __init__(self, test_config_file):
        self.configfile = test_config_file
        self.unittest_args = None
        cmdlineapp.Application.__init__(self)
        self.parser.add_argument("--option", "-o", action="store_true",
                                 help="sample option")

    def app_main(self, args):
        self.unittest_args = args
        return 0



class TestConfig(unittest.TestCase):

    def setUp(self):
        self.default_config_file = tempfile.NamedTemporaryFile()
        parser = ConfigParser.RawConfigParser()
        parser.add_section("french")
        parser.set("french", "one", "un")
        parser.set("french", "two", "deux")
        parser.set("french", "three", "trois")
        parser.write(self.default_config_file)
        self.default_config_file.flush()
        self.app = SampleConfigApplication(self.default_config_file.name)

    def tearDown(self):
        self.app = None
        self.default_config_file = None

    def __run_app(self, *args):
        ret = self.app.main(argv=(["/path/app.py"] + list(args)))
        return (ret, self.app.unittest_args, self.app.config)

    def test_defaults(self):
        ret, args, config = self.__run_app()
        self.assertEqual(ret, 0)
        self.assertEqual(config.get("french", "one"), "un")
        self.assertEqual(config.get("french", "two"), "deux")
        self.assertEqual(config.get("french", "three"), "trois")

    def test_alternate(self):
        with tempfile.NamedTemporaryFile() as config_file:
            parser = ConfigParser.RawConfigParser()
            parser.add_section("german")
            parser.set("german", "one", "eins")
            parser.set("german", "two", "zwei")
            parser.set("german", "three", "drei")
            parser.write(config_file)
            config_file.flush()
            ret, args, config = self.__run_app("--config-file=%s" %
                                               (config_file.name,))
        self.assertEqual(ret, 0)
        self.assertEqual(config.get("german", "one"), "eins")
        self.assertEqual(config.get("german", "two"), "zwei")
        self.assertEqual(config.get("german", "three"), "drei")
        self.assertFalse(config.has_section("french"))

    def test_override_default(self):
        ret, args, config = self.__run_app("--config=french:two=2")
        self.assertEqual(ret, 0)
        self.assertEqual(config.get("french", "one"), "un")
        self.assertEqual(config.get("french", "two"), "2")
        self.assertEqual(config.get("french", "three"), "trois")

    def test_override_new(self):
        ret, args, config = self.__run_app("--config=french:four=quatre")
        self.assertEqual(ret, 0)
        self.assertEqual(config.get("french", "one"), "un")
        self.assertEqual(config.get("french", "two"), "deux")
        self.assertEqual(config.get("french", "three"), "trois")
        self.assertEqual(config.get("french", "four"), "quatre")



options_suite = unittest.TestLoader().loadTestsFromTestCase(TestOptions)
config_suite = unittest.TestLoader().loadTestsFromTestCase(TestConfig)

all_tests = unittest.TestSuite((options_suite, config_suite))

