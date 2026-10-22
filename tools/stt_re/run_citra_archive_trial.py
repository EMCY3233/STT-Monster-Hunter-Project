"""Bounded capture + two scheduled normal-arrow trials; no timing via chat delays."""
import argparse,json,subprocess,sys,time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from citra_session_archive import capture,analyze


def run(image,mapping,out,window,exe):
    out=Path(out);events=[]
    with ThreadPoolExecutor(max_workers=1) as pool:
        future=pool.submit(capture,image,mapping,out,0x0110BC00,8192,3,(0x0110CF40,0x0110D000))
        # Input is permitted only after the reader has created its index.
        deadline=time.monotonic()+5
        while not (out/'reads.jsonl').exists():
            if future.done():future.result();raise RuntimeError('reader finished before trial')
            if time.monotonic()>deadline:raise TimeoutError('reader did not start')
            time.sleep(.05)
        start=time.monotonic()
        for second,key in ((6,'left'),(18,'right')):
            while time.monotonic()-start<second and not future.done():time.sleep(.05)
            if future.done():
                future.result();events.append(dict(key=key,status='skipped_reader_finished'));break
            receipt=out/(key+'-input.json')
            args=[sys.executable,str(Path(__file__).with_name('hold_citra_arrow.py')),
                  '--window',str(window),'--exe',str(exe),'--key',key,'--seconds','1',
                  '--receipt',str(receipt),'--execute']
            before=time.time();r=subprocess.run(args,capture_output=True,text=True,timeout=8)
            events.append(dict(key=key,utc_start=before,utc_end=time.time(),returncode=r.returncode,
                               receipt=receipt.name,visually_verified=False))
            if r.returncode:break  # No further input after an unknown/failed action.
        result=future.result()
    (out/'actions.json').write_text(json.dumps(events,indent=2)+'\n',encoding='utf-8')
    summary=analyze(out)
    for event in events:
        event['entirely_within_capture']=event.get('utc_start',0)>=result['utc_start'] and event.get('utc_end',float('inf'))<=result['utc_end']
    (out/'trial.json').write_text(json.dumps(dict(actions=events,reader=result,analysis=summary),indent=2)+'\n',encoding='utf-8')
    return dict(successful_reads=result['successful_reads'],unique_objects=result['unique_objects'],
        stored_bytes=result['stored_bytes'],changed_words=len(summary['changed_aligned_words']),actions=events)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('image','mapping','out','exe'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--window',type=int,required=True)
    a=p.parse_args();print(json.dumps(run(a.image,a.mapping,a.out,a.window,a.exe)))
