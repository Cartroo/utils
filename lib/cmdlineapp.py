#
# Copyright (c) 2012 Andrew Pearce <andy@andy-pearce.com>
#

import argparse
import ConfigParser
import logging
import os
import sys


class FatalError(Exception):
    pass



class Application(object):

    version = None
    configfile = None

    def __init__(self, config_parser_class=ConfigParser.RawConfigParser):
        """Init default command-line arguments and logging."""

        # Assume no config parser instance (is replaced with an instance below)
        self.config = None

        # Create default command-line parser.
        self.parser = argparse.ArgumentParser(description=self.__doc__)
        if self.version is not None:
            self.parser.add_argument("--version", "-V", action="version",
                                     version=self.version)
        if self.configfile is not None:
            self.config = config_parser_class()
            self.parser.add_argument("--config-file", default=None,
                                     help="config file to load")
            self.parser.add_argument("--skip-config", action="store_true",
                                     help="skip loading any config file")
            self.parser.add_argument("--config", action="append", default=[],
                                     metavar="SECTION:KEY=VALUE",
                                     help="override configuration setting")
        self.parser.add_argument("--verbose", "-v", action="count",
                                 help="once for progress, twice for debug")
        self.parser.add_argument("--quiet", "-q", action="store_true",
                                 help="disable all but errors, overrides -v")

        # Configure default logging.
        logging.basicConfig(level=logging.WARNING,
                            format="%(asctime)s - %(processName)s:"
                            " %(levelname)s: %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")

        # Create logger.
        self.logger = logging.getLogger(__name__)


    def handle_default_args(self, args):
        """Handle default arguments as specified in base constructor."""

        # Set default logging level
        if args.quiet:
            level = logging.ERROR
        elif args.verbose >= 2:
            level = logging.DEBUG
        elif args.verbose == 1:
            level = logging.INFO
        else:
            level = logging.WARNING
        logging.getLogger().setLevel(level)

        # If specified, load a configuration file.
        if self.config is not None:

            if args.config_file is None:
                # If the default config file fails to parse, this isn't an
                # error (the read() method silently ignores bad/missing files).
                default = os.path.expanduser(os.path.join("~", self.configfile))
                self.logger.debug("attempting to read default config file %r"
                                  % (default,))
                if not self.config.read(default):
                    self.logger.debug("failed to read default config file")
            else:
                # If a file was actually specified, regard it as an error if
                # it fails to parse.
                self.logger.debug("attempting to read user-specified config"
                                  " file %r" % (args.config_file,))
                if not self.config.read(args.config_file):
                    raise FatalError("failed to read config file %r"
                                     % (args.config_file,))

            # Add any user-specified configuration overrides.
            for override in args.config:
                try:
                    key_spec, value = override.split("=", 1)
                    section, key = key_spec.split(":", 1)
                    try:
                        self.config.add_section(section)
                    except ConfigParser.DuplicateSectionError:
                        pass
                    self.config.set(section, key, value)
                except ValueError:
                    raise FatalError("config override %r invalid" % (override,))


    def app_main(self, args):
        """Application-defined entry-point."""

        raise NotImplementedError("applications must implement app_main()")


    def main(self, argv=None):
        """Main function - returns int error code."""

        if argv is None:
            argv = sys.argv

        try:
            args = self.parser.parse_args(argv[1:])
            self.handle_default_args(args)
            return self.app_main(args)

        except FatalError, e:
            logging.error("%s", (e,))
            return 1

        except Exception, e:
            logging.critical("%s", (e,), exc_info=True)
            return 2

