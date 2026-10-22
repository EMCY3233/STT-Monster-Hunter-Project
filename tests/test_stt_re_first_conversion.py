import os,sys,struct,unittest,zlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'tools/stt_re'))
from convert_mod230_obj import strip_triangles
from convert_tex3ds_png import decode,png_rgba
dependency=os.environ.get('STT_TEXTURE_DECODER_PATH')
if dependency:sys.path.insert(0,dependency)
try:import texture2ddecoder as backend
except ImportError:backend=None


def tex(blocks,alpha=True):
    return struct.pack('<4s4I',b'TEX\0',0xa6,1|(8<<6)|(8<<19),1|((12 if alpha else 11)<<8),0)+b''.join(blocks)


def block(color=0,alpha=(1<<64)-1):return struct.pack('<QQ',alpha,color)


class StripTests(unittest.TestCase):
    def test_winding_and_restart(self):self.assertEqual(strip_triangles([0,1,2,3,65535,1,2,3],4),[(0,1,2),(2,1,3),(1,2,3)])
    def test_degenerate_still_changes_parity(self):self.assertEqual(strip_triangles([0,0,1,2],3),[(1,0,2)])
    def test_invalid_index(self):
        with self.assertRaises(ValueError):strip_triangles([0,1,4],4)
    def test_png_dimensions(self):
        png=png_rgba(bytes([1,2,3,4])*4,2,2)
        self.assertEqual(struct.unpack_from('>II',png,16),(2,2))
        with self.assertRaises(ValueError):png_rgba(b'bad',2,2)


@unittest.skipIf(backend is None,'set STT_TEXTURE_DECODER_PATH to pinned dependency')
class TextureTests(unittest.TestCase):
    def test_alpha_extremes(self):
        zero,_=decode(tex([block(alpha=0)]*4),backend);full,_=decode(tex([block()]*4),backend)
        self.assertEqual(set(zero[3::4]),{0});self.assertEqual(set(full[3::4]),{255})
        self.assertEqual([zero[i:i+3] for i in range(0,256,4)],[full[i:i+3] for i in range(0,256,4)])

    def test_alpha_nibble_coordinates(self):
        alpha=sum(i<<(4*i) for i in range(16));rgba,_=decode(tex([block(alpha=alpha)]*4),backend)
        for y in range(4):
            for x in range(4):self.assertEqual(rgba[(y*8+x)*4+3],(x*4+y)*17)

    def test_block_placement_endian_and_channels(self):
        colors=[0xff000000<<32,0x00ff0000<<32,0x0000ff00<<32,0]
        rgba,_=decode(tex([block(c) for c in colors]),backend)
        for (x,y),rgb in zip([(0,0),(4,0),(0,4),(4,4)],[(255,2,2),(2,255,2),(2,2,255),(2,2,2)]):
            self.assertEqual(tuple(rgba[(y*8+x)*4:(y*8+x)*4+3]),rgb)

    def test_etc1_without_alpha(self):
        rgba,_=decode(tex([struct.pack('<Q',0)]*4,False),backend)
        self.assertEqual(set(rgba[3::4]),{255})
