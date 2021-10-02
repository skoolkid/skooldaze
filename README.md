Skool Daze disassembly
======================

A disassembly of the [Spectrum](https://en.wikipedia.org/wiki/ZX_Spectrum)
version of [Skool Daze](https://en.wikipedia.org/wiki/Skool_Daze), created
using [SkoolKit](https://skoolkit.ca).

Decide which number base you prefer and then click the corresponding link below
to browse the latest release:

* [Skool Daze disassembly](https://skoolkid.github.io/skooldaze/) (hexadecimal; mirror [here](https://skoolkid.gitlab.io/skooldaze/))
* [Skool Daze disassembly](https://skoolkid.github.io/skooldaze/dec/) (decimal; mirror [here](https://skoolkid.gitlab.io/skooldaze/dec/))

To build the current development version of the disassembly, first obtain the
development version of [SkoolKit](https://github.com/skoolkid/skoolkit). Then:

    $ skool2html.py sources/sd.skool

To build an assembly language source file that can be fed to an assembler:

    $ skool2asm.py sources/sd.skool > sd.asm
