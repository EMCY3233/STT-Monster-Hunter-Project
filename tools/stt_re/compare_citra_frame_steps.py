"""Compare stable, hash-verified captures around externally observed frame actions."""
import argparse,json,struct
from pathlib import Path
from translate_citra_counter import load_summary


def compare(blocks, expected):
    if len(blocks)<2 or len(expected)!=len(blocks)-1:
        raise ValueError('one expected delta per capture transition required')
    if any(type(x) is not int or not 0<=x<=10 for x in expected):
        raise ValueError('expected steps must be integers 0..10')
    first=[]
    for block in blocks:
        if len(block)<64 or len(block)%32:
            raise ValueError('at least two complete samples required')
        samples=[block[i:i+32] for i in range(0,len(block),32)]
        if any(x!=samples[0] for x in samples):
            raise ValueError('capture is not stable while waiting for the next step')
        first.append(samples[0])
    transitions=[]
    for a,b,n in zip(first,first[1:],expected):
        deltas=[(struct.unpack_from('<I',b,o)[0]-struct.unpack_from('<I',a,o)[0])&0xffffffff for o in (4,8)]
        transitions.append(dict(expected_steps=n,observed_field_deltas=deltas,matches_expected=deltas==[n,n]))
    return dict(transitions=transitions,all_match=all(x['matches_expected'] for x in transitions),
                meaning='observed agreement with externally documented Citra frame-step requests',
                instruction_writer_identified=False,game_logic_frame_identity_verified=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--captures',nargs='+',type=Path,required=True)
    p.add_argument('--expected',nargs='+',type=int,required=True)
    a=p.parse_args();blocks=[]
    for f in a.captures:
        load_summary(f)  # Reject hash, index, length, control or RPC error failures.
        blocks.append((f/'samples.bin').read_bytes())
    print(json.dumps(compare(blocks,a.expected),indent=2))
