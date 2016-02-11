""" Write Inputfile for SRIM calculations

"""


class AutoTRIM(object):
    """ Determines state of TRIM calculation

     - [0] TRIM runs normally.
     - [1] TRIM runs without keyboard input
     - [2] TRIM resumes running its last saved calculation

    [1] is really the only one you would want for python calculations
    """
    def __init__(self, mode=1, restart_directroy=None):
        self._mode = mode

    def write(self):
        """ write AUTOTRIM in current directory """
        with open('TRIMAUTO', 'w') as f:
            f.write('{}'.format(self._mode))


class TRIMInput(object):
    """ Input File representation of SRIM run """
    def __init__(self, srim):
        self._srim = srim

    def write(self):
        with open('TRIM.IN', 'w') as f:
            # Not guarentted to be the number of unique elements
            srim_num_elements = sum(len(layer.elements) for layer in self._srim.target.layers) 

            # Line 1-2: Comments
            f.write((
                'This file controls TRIM Calculations generated by srim-python\r\n'
                'Ion: Z, Mass [amu], Energy [keV], Angle [degrees], Number Ions, Bragg Corr, AutoSave Number\r\n'
            ))
            # Line 3: Ion information
            f.write('{} {} {} {} {} {} {}\r\n'.format(
                self._srim.ion.atomic_number,
                self._srim.ion.mass,
                self._srim.ion.energy / 1000.0, # eV -> keV
                self._srim.settings.angle_ions,
                self._srim.number_ions,
                self._srim.settings.bragg_correction,
                self._srim.settings.autosave
            ))
            # Line 4: Comment
            f.write('Cascades(1=Kitchn-Peese, 2=Full-Cascade, 3=Sputtering, 4-5=Ions;6-7=Neutrons), Random Number Seed, Reminders\r\n')
            # Line 5: Type of calculation and random seed
            f.write('{} {} {}\r\n'.format(
                self._srim.calculation,
                self._srim.settings.random_seed,
                self._srim.settings.reminders
            ))
            # Line 6: Comment
            f.write('Diskfiles (0=no,1=yes): RANGES.txt, BACKSCATT.txt, TRANSMIT.txt, Sputtered, COLLISIONS.txt(0=no, 1=Ion, 2=Ion+Recoils), Special EXYZ.txt file\r\n')
            # Line 7: Datafiles to write
            f.write('{} {} {} {} {} {}\r\n'.format(
                self._srim.settings.ranges,
                self._srim.settings.backscattered,
                self._srim.settings.transmit,
                self._srim.settings.sputtered,
                self._srim.settings.collisions,
                self._srim.settings.exyz
            ))
            # Line 8: Comment
            f.write('Target material : Number of Elements, Number of Layers\r\n')
            # Line 9: Target name, number of elements, number of layers
            f.write('"{}" {} {}\r\n'.format(
                self._srim.settings.description,
                len(self._srim.target.layers),
                srim_num_elements
            ))
            # Line 10: Comment
            f.write('PlotType (0-5); Plot Depths: Xmin, Xmax(Ang.) [=0 0 for Viewing Full Target]\r\n')
            # Line 11: PlotType, Viewing window depths (must be between width)
            f.write('{} {} {}\r\n'.format(
                self._srim.settings.plot_mode,
                self._srim.settings.plot_xmin,
                self._srim.settings.plot_xmax
            ))
            # Line 12: Comment
            f.write('Target Elements:    Z   Mass [amu]\r\n')
            # Line 13 to (12 + num_atoms):
            index = 1
            for layer in self._srim.target.layers:
                for element in layer.elements:
                    f.write('Atom {} = {} =  {} {}\r\n'.format(
                        index, element.symbol, 
                        element.atomic_number,
                        element.mass
                    ))
                    index += 1
            # After Atoms Description 2 lines: Comment
            line_1 = 'Layer    Layer Name   Width Density'
            line_2 = 'Number   Description  (Ang) (g/cm^3)' + '  Stoich' * srim_num_elements + '\r\n'
            for layer in self._srim.target.layers:
                for element in layer.elements:
                    line_1 = line_1 + '  {}({})'.format(
                        element.symbol, element.atomic_number)
            f.write(line_1 + '\r\n' + line_2)
            # Layer descriptions
            element_index = 0
            for layer_index, layer in enumerate(self._srim.target.layers):
                layer_str = '{} "{}" {} {}'.format(
                    layer_index, 
                    layer.name,
                    layer.width,
                    layer.density
                )
                layer_str = layer_str + ' 0.0' * element_index
                for element in layer.elements:
                    layer_str = layer_str + ' {}'.format(layer.elements[element]['stoich'])
                layer_str = layer_str + ' 0.0' * (srim_num_elements - element_index - len(layer.elements))
                f.write(layer_str + '\r\n')
                element_index += len(layer.elements)
            # Layer Phases: Comment
            f.write('0  Target layer phases (0=Solid, 1=Gas)\r\n')
            # Layer Phases: (solid or gas)
            f.write(' '.join(str(layer.phase) for layer in self._srim.target.layers) + '\r\n')

            # Layer Bragg Correction
            f.write('Target Compound Corrections (Bragg)\r\n')
            f.write(' 1' * len(self._srim.target.layers) + '\r\n')

            # Per Atom Displacement Energies
            f.write('Individual target atom displacement energies (eV)\r\n')
            line = ''
            for layer in self._srim.target.layers:
                for element in layer.elements:
                    line = line + ' {}'.format(layer.elements[element]['E_d'])
            f.write(line + '\r\n')
            #Per Atom Lattice Binding Energy
            f.write('Individual target atom lattice binding energies (eV)\r\n')
            line = ''
            for layer in self._srim.target.layers:
                for element in layer.elements:
                    line = line + ' {}'.format(layer.elements[element]['lattice'])
            f.write(line + '\r\n')
            #Per Atom Lattice Binding Energy
            f.write('Individual target atom surface binding energies (eV)\r\n')
            line = ''
            for layer in self._srim.target.layers:
                for element in layer.elements:
                    line = line + ' {}'.format(layer.elements[element]['surface'])
            f.write(line + '\r\n')
            
            # Stopping power version
            f.write('Stopping Power Version (1=2011, 0=2011)\r\n')
            f.write('{}\r\n'.format(self._srim.settings.version))
