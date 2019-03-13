import pf_vector
import pf_halfplane
import pf_map_base


class RawMap(pf_map_base.MapBase):
    @staticmethod
    def read(path):
        """ read the map """
        height, width = 0, 0
        # open source in binary read mode and open destination in binary write mode
        with open(path, "rb") as f:
            # read the first 3+x lines
            read_lines = 0
            while read_lines != 3:
                line = f.readline()

                # ignore comments
                if line.startswith(b'#'):
                    continue

                # first line is the version
                if read_lines == 0:
                    version = line.strip()
                    assert (version == b"P5")
                # second line is width and height
                if read_lines == 1:
                    width, height = line.strip().split(b" ")
                    width, height = int(width), int(height)
                # third line is the max pixel value
                if read_lines == 2:
                    max_value = line.strip()

                # increment read line counter
                read_lines += 1

            # after that, all is data
            data = f.read()

        assert (len(data) == width * height)

        # return interesting data
        return RawMap(width, height, data)
