.. optparse2 documentation master file, created by
   sphinx-quickstart on Thu Jul  3 11:11:53 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


optparse2
#########

.. toctree::
   :maxdepth: 2

.. automodule:: optparse2


Classes
=======

.. autoclass:: OptionContainer
    :members: get_option_by_name, add_option

.. autoclass:: OptionGroup

.. autoclass:: OptionParser
    :members: __init__, cmp_opts, print_help, _add_help_option,
              add_all_default_values, _add_default_values, move_option,
              parse_args, get_option_group_by_title, walk, search_option

.. autoclass:: IndentedHelpFormatterWithNL
    :members: format_description, format_option


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
