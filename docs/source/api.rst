Class diagram
-------------
The following diagram shows all classes and their relationships in the library:

.. graphviz::

    digraph classes {
        rankdir=LR;
        node [shape=box, style=filled, fillcolor="#ffffcc", fontname="Helvetica"];
        edge [fontname="Helvetica", fontsize=10];

        DiskInfo -> Disk [arrowhead=diamond, label="1..*"];
        Disk -> Partition [arrowhead=diamond, label="0..*"];
        Disk -> FileSystem [arrowhead=diamond, label="0..1"];
        Disk -> DiskSmartData [style=dashed, label="creates"];
        Disk -> DiskType [style=dashed, label="uses"];
        Partition -> FileSystem [arrowhead=diamond, label="1"];
        DiskSmartData -> SmartAttribute [arrowhead=diamond, label="0..*"];
        DiskSmartData -> NvmeAttributes [arrowhead=diamond, label="0..1"];

        subgraph cluster_legend {
            label="Legend";
            fontname="Helvetica";
            fontsize=9;
            style=dashed;
            color=grey;
            margin=20;
            node [shape=plaintext, style="", fillcolor="", width=0, height=0, fontsize=8];
            edge [fontname="Helvetica", fontsize=8, minlen=1];
            l1a [label=""];
            l1b [label=""];
            l2a [label=""];
            l2b [label=""];
            l1a -> l1b [arrowhead=diamond, label="composition"];
            l2a -> l2b [style=dashed, label="dependency"];
        }
    }


API reference
-------------
In this section you will find the detailed API reference about the implemented classes and functions
of ``diskinfo`` library.

.. toctree::

    diskinfo.rst
    disk.rst
    disktype.rst
    disksmart.rst
    smartattr.rst
    nvmeattr.rst
    partition.rst
    filesystem.rst
    utils.rst
