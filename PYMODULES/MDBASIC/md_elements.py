__version__ = "2017-11-28"

# Masses and names of elements to convert masses to names and vice versa
element_name = ["X", "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne",
                "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar",
                "K ", "Ca", "Sc", "Ti", "V ", "Cr", "Mn", "Fe", "Co", "Ni", "Cu",
                "Zn", "Ga", "Ge", "As", "Se", "Br", "Kr",
                "Rb", "Sr", "Y ", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag",
                "Cd", "In", "Sn", "Sb", "Te", "I", "Xe", "Cs", "Ba", "La", "Ce",
                "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm",
                "Yb", "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg",
                "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th", "Pa",
                "U ", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md",
                "No", "Lr", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg"]

# exact masses
element_ms = [0.00000, 1.00794, 4.00260, 6.941, 9.012182, 10.811,
              12.0107, 14.0067, 15.9994, 18.9984032, 20.1797, 22.989770,
              24.3050, 26.981538, 28.0855, 30.973761, 32.065, 35.453,
              39.948, 39.0983, 40.078, 44.955910, 47.867, 50.9415,
              51.9961, 54.938049, 55.845, 58.9332, 58.6934, 63.546,
              65.409, 69.723, 72.64, 74.92160, 78.96, 79.904, 83.798,
              85.4678, 87.62, 88.90585, 91.224, 92.90638, 95.94, 98.0,
              101.07, 102.90550, 106.42, 107.8682, 112.411, 114.818,
              118.710, 121.760, 127.60, 126.90447, 131.293, 132.90545,
              137.327, 138.9055, 140.116, 140.90765, 144.24, 145.0,
              150.36, 151.964, 157.25, 158.92534, 162.500, 164.93032,
              167.259, 168.93421, 173.04, 174.967, 178.49, 180.9479,
              183.84, 186.207, 190.23, 192.217, 195.078, 196.96655,
              200.59, 204.3833, 207.2, 208.98038, 209.0, 210.0, 222.0,
              223.0, 226.0, 227.0, 232.0381, 231.03588, 238.02891,
              237.0, 244.0, 243.0, 247.07, 247.0, 251.0, 252.0, 257.0,
              258.0, 259.0, 262.0, 261.0, 262.144, 266.0, 264.0, 269.0,
              268.0, 271.0, 272.0]

# masses rounded to  first fractional digit
element_rnd_mass = [0.0, 1.0, 4.0, 6.9, 9.0, 10.8, 12.0, 14.0, 16.0, 19.0, 20.2,
                    23.0, 24.3, 27.0, 28.1, 31.0, 32.1, 35.5, 39.9, 39.1, 40.1,
                    45.0, 47.9, 50.9, 52.0, 54.9, 55.8, 58.9, 58.7, 63.5, 65.4,
                    69.7, 72.6, 74.9, 79.0, 79.9, 83.8, 85.5, 87.6, 88.9, 91.2,
                    92.9, 95.9, 98.0, 101.1, 102.9, 106.4, 107.9, 112.4, 114.8,
                    118.7, 121.8, 127.6, 126.9, 131.3, 132.9, 137.3, 138.9,
                    140.1, 140.9, 144.2, 145.0, 150.4, 152.0, 157.3, 158.9,
                    162.5, 164.9, 167.3, 168.9, 173.0, 175.0, 178.5, 180.9,
                    183.8, 186.2, 190.2, 192.2, 195.1, 197.0, 200.6, 204.4,
                    207.2, 209.0, 209.0, 210.0, 222.0, 223.0, 226.0, 227.0,
                    232.0, 231.0, 238.0, 237.0, 244.0, 243.0, 247.0, 247.0,
                    251.0, 252.0, 257.0, 258.0, 259.0, 262.0, 261.0, 262.0,
                    266.0, 264.0, 269.0, 268.0, 271.0, 272.0]

# combined masses
elements = {0.0: 'X', 1.0: 'H', 4.0: 'He', 6.9: 'Li', 9.0: 'Be', 10.8: 'B',
            12.0: 'C', 14.0: 'N', 16.0: 'O', 19.0: 'F', 20.2: 'Ne', 23.0: 'Na',
            24.3: 'Mg', 27.0: 'Al', 28.1: 'Si', 31.0: 'P', 32.1: 'S', 35.5: 'Cl',
            39.1: 'K ', 39.9: 'Ar', 40.1: 'Ca', 45.0: 'Sc', 47.9: 'Ti',
            50.9: 'V ', 52.0: 'Cr', 54.9: 'Mn', 55.8: 'Fe', 58.7: 'Ni',
            58.9: 'Co', 63.5: 'Cu', 65.4: 'Zn', 69.7: 'Ga', 72.6: 'Ge',
            74.9: 'As', 79.0: 'Se', 79.9: 'Br', 83.8: 'Kr', 85.5: 'Rb',
            87.6: 'Sr', 88.9: 'Y ', 91.2: 'Zr', 92.9: 'Nb', 95.9: 'Mo',
            98.0: 'Tc', 101.1: 'Ru', 102.9: 'Rh', 106.4: 'Pd',
            107.9: 'Ag', 112.4: 'Cd', 114.8: 'In', 118.7: 'Sn', 121.8: 'Sb',
            126.9: 'I', 127.6: 'Te', 131.3: 'Xe', 132.9: 'Cs', 137.3: 'Ba',
            138.9: 'La', 140.1: 'Ce', 140.9: 'Pr', 144.2: 'Nd', 145.0: 'Pm',
            150.4: 'Sm', 152.0: 'Eu', 157.3: 'Gd', 158.9: 'Tb', 162.5: 'Dy',
            164.9: 'Ho', 167.3: 'Er', 168.9: 'Tm', 173.0: 'Yb', 175.0: 'Lu',
            178.5: 'Hf', 180.9: 'Ta', 183.8: 'W', 186.2: 'Re', 190.2: 'Os',
            192.2: 'Ir', 195.1: 'Pt', 197.0: 'Au', 200.6: 'Hg', 204.4: 'Tl',
            207.2: 'Pb', 209.0: 'Po', 210.0: 'At', 222.0: 'Rn', 223.0: 'Fr',
            226.0: 'Ra', 227.0: 'Ac', 231.0: 'Pa', 232.0: 'Th', 237.0: 'Np',
            238.0: 'U ', 243.0: 'Am', 244.0: 'Pu', 247.0: 'Bk', 251.0: 'Cf',
            252.0: 'Es', 257.0: 'Fm', 258.0: 'Md', 259.0: 'No', 261.0: 'Rf',
            262.0: 'Db', 264.0: 'Bh', 266.0: 'Sg', 268.0: 'Mt', 269.0: 'Hs',
            271.0: 'Ds', 272.0: 'Rg'}

# atomic radii in angstrom
element_radii = [1.5, 1.2, 1.4, 1.82, 2.0, 2.0, 1.7, 1.55, 1.52, 1.47, 1.54, 1.36, 1.18,
                 2.0, 2.1, 1.8, 1.8, 2.27, 1.88, 1.76, 1.37, 2.0, 2.0, 2.0, 2.0, 2.0,
                 2.0, 2.0, 1.63, 1.4, 1.39, 1.07, 2.0, 1.85, 1.9, 1.85, 2.02, 2.0, 2.0,
                 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.63, 1.72, 1.58, 1.93, 2.17, 2.0,
                 2.06, 1.98, 2.16, 2.1, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0,
                 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.72,
                 1.66, 1.55, 1.96, 2.02, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0,
                 1.86, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0,
                 2.0, 2.0, 2.0, 2.0, 2.0, 2.0]

# element radius by mass
elements_mass_radii = dict(list(zip(element_rnd_mass, element_radii)))
element_mass = dict(list(zip(element_name, element_rnd_mass)))

# element name by atomic number
element_number = list(range(0, len(element_name)))
atomicnumber_element = dict(list(zip(element_number, element_name)))
atomic_number_mass = dict(list(zip(element_number, element_rnd_mass)))
