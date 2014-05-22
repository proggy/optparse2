#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright notice
# ----------------
#
# Copyright (C) 2012-2014 Daniel Jung
# Contact: djungbremen@gmail.com
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA.
#
#
# Original copyright statement by the authors of optparse
# =======================================================
#
# Copyright (c) 2001-2006 Gregory P. Ward.  All rights reserved.
# Copyright (c) 2002-2006 Python Software Foundation.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the author nor the names of its contributors may be
#   used to endorse or promote products derived from this software without
#   specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
"""Extend the command line option parser from the module "optparse", which was
originally written by Gregory P. Ward.

The most important changes are:
--> information about the default values is automatically appended to the
    help strings of each option (if they do not already include the word
    "%default")
--> options and option groups are displayed in alphabetical order on the help
    page
--> option string conflicts may not necessarily lead to an exception. First it
    is tried to move the option string to the new option (give it a new
    meaning), as long as at least one option string remains at the old option
--> pydoc.pager is now used to display the help (similar behavior to the bash
    command "less")
--> by default, the "help" and "version" options are moved to an option group
    called "General options"
--> the "help" option does no longer have the short option string "-h", but
    instead "-?"
--> write "None" instead of "none" in default option value help string
--> preserve linebreaks in description (could still be improved)

To do:
--> only use pydoc.pager for showing help if the length of the help is
    exceeding the terminal window height"""
__created__ = '2012-05-17'
__modified__ = '2013-02-06'
import optparse
import pydoc
import textwrap


class OptionContainer(optparse.OptionContainer):
    """Extended version of optparse.OptionContainer."""
    # 2012-05-21 - 2012-05-23

    def get_option_by_name(self, name):
        """Get option by option name. A little bit different than "get_option",
        because it first checks "dest" before trying the option strings, and
        also does not expect the dashes ("-" or "--") when referencing the
        option strings."""
        # 2012-05-21 - 2012-05-21

        # check destinations
        for option in self.option_list:
            if option.dest and option.dest == name:
                return option

        # try option strings
        return self._long_opt.get('--'+name) or self._short_opt.get('-'+name)

    def add_option(self, *args, **kwargs):
        """Before calling the original method "add_option", this version checks
        if the same option strings (long and short) do already exist in another
        option definition. Instead of raising an exception rightaway, it tries
        to "overwrite" the meaning of the option string, i.e. the option string
        is deleted from the other option. However, this will only be done if
        this option string is not the only one defined in the other option,
        because at least one option string should persist for each option."""
        # 2012-05-23 - 2012-05-23

        # cycle all option strings of the new option
        for optionstring in args:
            # check if this option string already exists in some option
            if optionstring in self._short_opt:
                option = self._short_opt[optionstring]

                # make sure it is not the only option string of this option
                if len(option._short_opts)+len(option._long_opts) > 1:
                    # delete this option string from the old option
                    option._short_opts.remove(optionstring)
                    del self._short_opt[optionstring]

            elif optionstring in self._long_opt:
                option = self._long_opt[optionstring]

                # make sure it is not the only option string of this option
                if len(option._short_opts)+len(option._long_opts) > 1:
                    # delete this option string from the oLegold option
                    option._long_opts.remove(optionstring)
                    del self._long_opt[optionstring]

        # finally, call the original method
        optparse.OptionContainer.add_option(self, *args, **kwargs)


class OptionGroup(optparse.OptionGroup, OptionContainer):
    """Just make sure the modified method "OptionContainer.add_option" is used
    also for "OptionGroup"."""
    # 2012-05-23 - 2012-05-23
    add_option = OptionContainer.add_option


class OptionParser(optparse.OptionParser, OptionContainer):
    """My improved version of optparse.OptionParser that overwrites some of its
    methods and changes its behavior a little bit."""
    # 2012-05-17 - 2013-02-06

    # former hdp._MyOptionParser from 2011-09-14 until 2011-12-19
    # former tb.MyOptionParser from 2011-08-03

    def __init__(self, *args, **kwargs):
        """My version of the constructor. Sets the version string if the user
        hasn't done that himself, because an empty version string would lead to
        a bug lateron.  If the keyword argument "general" is set to True, move
        help and version options to the newly created option group "General
        options" (default: True)."""
        # 2012-05-17 - 2012-05-21
        # former hdp._MyOptionParser.__init__ from 2011-11-11

        # make sure the keyword argument "version" is set to a non-empty string
        if not 'version' in kwargs:
            kwargs.update(version=' ')
        if not 'formatter' in kwargs:
            kwargs.update(formatter=IndentedHelpFormatterWithNL())

        # catch additional keyword arguments before calling the original method
        general = kwargs.pop('general', True)

        # call original initialisation method
        optparse.OptionParser.__init__(self, *args, **kwargs)

        # create an option group "general options" and move help and version
        # option there
        if general:
            og = optparse.OptionGroup(self, 'General options')
            self.move_option('help', og)
            self.move_option('version', og)
            self.add_option_group(og)

    def cmp_opts(self, a, b):
        """Compare options by first short option name or, if there is not short
        option name, by first long option name. Needed for sorting the
        options."""
        # 2012-05-17
        # former hdp._MyOptionParser.cmp_opts from 2011-08-03
        if len(a._short_opts) > 0:
            aname = a._short_opts[0][1:]
        else:
            aname = a._long_opts[0][2:]
        if len(b._short_opts) > 0:
            bname = b._short_opts[0][1:]
        else:
            bname = b._long_opts[0][2:]
        if aname == bname:
            return 0
        elif aname < bname:
            return -1
        else:
            return 1

    def print_help(self, file=None):
        """Like the old one, except uses pydoc.pager to show the help on the
        screen. The file argument no longer has any meaning, it just stays for
        compatibility reasons. Also, the method now sorts all options and
        option groups before displaying the help."""
        # 2012-05-17
        # former hdp._MyOptionParser.print_help from 2011-08-02 - 2011-12-19
        # How can line breaks be preserved in epilog and description? Maybe
        # look at the responsible mothod in optparse.OptionParser to get a hint

        # sort options (also within option groups, and groups themselves)
        self.option_list.sort(cmp=self.cmp_opts)
        self.option_groups.sort(cmp=lambda a, b: -1
                                if a.title < b.title else 1)
        for ind in xrange(len(self.option_groups)):
            self.option_groups[ind].option_list.sort(cmp=self.cmp_opts)

        #if file is None:
        #    file = _sys.stdout
        encoding = self._get_encoding(file)
        #file.write(self.format_help().encode(encoding, "replace"))
        pydoc.pager(self.format_help().encode(encoding, 'replace'))

    def _add_help_option(self):
        """Like the original method, but does not define the short option
        string "-h". Instead, defines "-?"."""
        # 2012-05-17 - 2012-07-09
        # former hdp._MyOptionParser.print_help 2011-08-03
        self.add_option('-?', '--help', action='help',
                        help='show this help message and exit')

    def add_all_default_values(self):
        """Automatically append the default values to the help strings of all
        the options of this option parser. Those options that already contain
        the substring "%default" are skipped."""
        # 2012-05-18
        self._add_default_values(self)
        for og in self.option_groups:
            self._add_default_values(og)

    def _add_default_values(self, op):
        """Automatically append information about the default values to the
        help string of the given option parser or option group object. Those
        options that already contain the substring "%default" are skipped.
        This method is used by "add_all_default_values", which should be called
        by the user. There should be no need for the user to call this method
        manually."""
        # 2012-05-18 - 2012-05-22
        # former hdp.BaseHDP.help_default from 2011-09-14
        # former tb.BaseProc.help_default from 2011-02-11
        for o in op.option_list:
            if o.help and not '%default' in o.help and o.action == 'store' \
                    and str(o.default) != '':
                # then append the information to the help string
                if not o.help[-1] in '.!':
                    o.help += '.'
                if o.help[-1] != ' ':
                    o.help += ' '
                o.help += 'Default: %default'

    def move_option(self, name, destination, source=None):
        """Move an already defined option from one option parser object to
        another.  By default, the source object is the option parser object
        itself, but can also be set to any option group object. Also the
        destination can be any option parser or option group object."""
        # 2012-05-18 - 2012-05-21

        # set source to this option parser object by default
        if source is None:
            source = self

        # search for the given option name, remember its index
        try:
            index = source.option_list.index(self.get_option_by_name(name))
        except ValueError:
            raise KeyError('option "%s" not found' % name)

        # move option object to new location
        destination.option_list.append(source.option_list.pop(index))

    def parse_args(self, args=None, values=None):
        """Does a little bit of extra stuff before calling the original method
        "parse_args"."""
        # 2012-05-21 - 2012-05-22

        # add the default values to all help strings
        self.add_all_default_values()

        # make sure line breaks are respected in epilog and description
        #self.epilog = '\n'.join([s.strip() for s in self.epilog.split('\n')])
        #self.description = '\n'.join([s.strip() \
                                    #for s in self.description.split('\n')])
        # How can line breaks be preserved in epilog and description? Maybe
        # look at the responsible mothod in optparse.OptionParser to get a hint

        # call original method
        return optparse.OptionParser.parse_args(self, args=args, values=values)

        # next thing will be to create an argument "dictionary" (or similar) to
        # feed the Values instance with extra values again, recall "dest" or
        # long or short option strings substitute kw2op with something more
        # reasonable I think this can already be done with the argument
        # "values" probably just say "values=optparse.Values(dictionary)" but
        # then, only the true option names are allowed, i.e. option.dest

    def get_option_group_by_title(self, title):
        """Get option group by group title. It is sufficient if the group title
        is starting with the given string. All strings are converted to lower
        case before comparison."""
        # 2012-05-21 - 2012-05-21

        # check all groups
        for group in self.option_groups:
            if group.title.lower().startswith(title.lower()):
                return group
        else:
            raise KeyError('option group %s not found' % title)

    def walk(self):
        """Return iterator over all options of the option parser, including
        those in option groups."""
        ### already exists by the name _get_all_options (but it is not an
        ### iterator)
        # 2012-05-22 - 2012-05-22
        for option in self.option_list:
            yield option
        for group in self.option_groups:
            for option in group.option_list:
                yield option

    def search_option(self, name):
        """Search the whole option parser recursively (also in option groups)
        for an option by the given name. If no matching option is found, return
        False.  Otherwise, return reference to the option object."""
        # 2012-05-22 - 2012-05-22
        for option in self.walk():
            if option.dest and option.dest == name \
                    or '--'+name in option._long_opts \
                    or '-'+name in option._short_opts:
                return option
        else:
            return False

    add_option = OptionContainer.add_option


# solve the problem that newline characters are erased in the docstring
# courtesy to Tim Chase
# https://groups.google.com/forum/?fromgroups#!topic/comp.lang.python/
# bfbmtUGhW8I
class IndentedHelpFormatterWithNL(optparse.IndentedHelpFormatter):
    __created__ = '2013-02-06'
    __modified__ = '2013-02-06'

    NO_DEFAULT_VALUE = 'None'

    def format_description(self, description):
        if not description:
            return ''
        desc_width = self.width - self.current_indent
        indent = " "*self.current_indent
        # the above is still the same
        bits = description.split('\n')
        formatted_bits = [
            textwrap.fill(bit, desc_width, initial_indent=indent,
                          subsequent_indent=indent)
            for bit in bits]
        result = "\n".join(formatted_bits) + "\n"
        return result

    def format_option(self, option):
        # The help for each option consists of two parts:
        #   * the opt strings and metavars
        #   eg. ("-x", or "-fFILENAME, --file=FILENAME")
        #   * the user-supplied help string
        #   eg. ("turn on expert mode", "read data from FILENAME")
        #
        # If possible, we write both of these on the same line:
        #   -x    turn on expert mode
        #
        # But if the opt string list is too long, we put the help
        # string on a second line, indented to the same column it would
        # start in if it fit on the first line.
        #   -fFILENAME, --file=FILENAME
        #       read data from FILENAME
        result = []
        opts = self.option_strings[option]
        opt_width = self.help_position - self.current_indent - 2
        if len(opts) > opt_width:
            opts = "%*s%s\n" % (self.current_indent, "", opts)
            indent_first = self.help_position
        else:  # start help on same line as opts
            opts = "%*s%-*s  " % (self.current_indent, "", opt_width, opts)
            indent_first = 0
        result.append(opts)
        if option.help:
            help_text = self.expand_default(option)
        # everything is the same up through here
            help_lines = []
            for para in help_text.split("\n"):
                help_lines.extend(textwrap.wrap(para, self.help_width))
        # everything is the same after here
            result.append("%*s%s\n" % (
                indent_first, "", help_lines[0]))
            result.extend(["%*s%s\n" % (self.help_position, "", line)
                           for line in help_lines[1:]])
        elif opts[-1] != "\n":
            result.append("\n")
        return "".join(result)
